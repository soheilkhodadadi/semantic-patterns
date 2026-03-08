"""Build the canonical labeling batch for Iteration 1 label ops bootstrap."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

import pandas as pd

from semantic_ai_washing.labeling.common import length_bin_from_tokens, normalize_sentence

DEFAULT_SENTENCES = "data/processed/sentences/year=2024/ai_sentences.parquet"
DEFAULT_MANIFEST = "data/manifests/filings/pilot_2024_10k_v1.csv"
DEFAULT_HELD_OUT = "data/validation/held_out_sentences.csv"
DEFAULT_OUTPUT_PARQUET = "data/labels/v1/labeling_batch_v1.parquet"
DEFAULT_OUTPUT_CSV = "data/labels/v1/labeling_batch_v1.csv"
DEFAULT_REPORT = "reports/labels/labeling_batch_v1_summary.json"

OUTPUT_COLUMNS = [
    "batch_id",
    "batch_row_id",
    "sampling_seed",
    "selection_reason",
    "sentence_id",
    "sentence_text_id",
    "sentence",
    "sentence_norm",
    "label",
    "is_uncertain",
    "uncertainty_note",
    "source_file",
    "source_year",
    "source_quarter",
    "source_form",
    "source_cik",
    "sentence_index",
    "manifest_id",
    "manifest_row_id",
    "source_window_id",
    "token_count",
    "fragment_score",
    "integrity_flags",
    "sic",
    "ff12_code",
    "ff12_name",
    "industry_metadata_source",
    "length_bin",
    "edge_case_flag",
    "filing_selection_reason",
]

_EDGE_CASE_RE = re.compile(
    r"\b(may|might|could|intend|plan|expect|future|transform|revolution|generative ai|risk|uncertain|aim|seek|hope)\b",
    re.I,
)
_LENGTH_PRIORITY = {"medium": 0, "long": 1, "short": 2}


def _sha1_short(payload: str) -> str:
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


def _git_commit() -> str:
    try:
        output = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True)
        return output.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _require_columns(frame: pd.DataFrame, required: list[str], label: str) -> None:
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"{label} missing required columns: {', '.join(sorted(missing))}")


def _load_heldout_norms(path: str) -> set[str]:
    held_out = pd.read_csv(path)
    if "sentence" not in held_out.columns:
        raise ValueError("Held-out dataset must contain `sentence`.")
    return {
        normalize_sentence(sentence)
        for sentence in held_out["sentence"].fillna("").astype(str)
        if normalize_sentence(sentence)
    }


def _load_existing_sentence_text_ids(path: str) -> set[str]:
    frame = pd.read_csv(path)
    if "sentence_text_id" not in frame.columns:
        raise ValueError("Existing batch CSV must contain `sentence_text_id`.")
    return {
        str(value).strip()
        for value in frame["sentence_text_id"].fillna("").astype(str)
        if str(value).strip()
    }


def _load_candidates(sentences_path: str, manifest_path: str) -> pd.DataFrame:
    sentences = pd.read_parquet(sentences_path)
    manifest = pd.read_csv(manifest_path)

    _require_columns(
        sentences,
        [
            "sentence_id",
            "sentence_text_id",
            "sentence",
            "sentence_norm",
            "source_file",
            "source_year",
            "source_quarter",
            "source_form",
            "source_cik",
            "sentence_index",
            "manifest_id",
            "source_window_id",
            "token_count",
            "fragment_score",
            "integrity_flags",
        ],
        "Sentence table",
    )
    _require_columns(
        manifest,
        [
            "manifest_id",
            "manifest_row_id",
            "selection_reason",
            "path",
            "sic",
            "ff12_code",
            "ff12_name",
            "industry_metadata_source",
        ],
        "Pilot manifest",
    )

    manifest_view = manifest[
        [
            "path",
            "manifest_id",
            "manifest_row_id",
            "selection_reason",
            "sic",
            "ff12_code",
            "ff12_name",
            "industry_metadata_source",
        ]
    ].rename(columns={"selection_reason": "filing_selection_reason"})

    merged = sentences.merge(
        manifest_view,
        left_on=["source_file", "manifest_id"],
        right_on=["path", "manifest_id"],
        how="left",
        validate="many_to_one",
    )
    missing_manifest = int(merged["manifest_row_id"].isna().sum())
    if missing_manifest:
        raise ValueError(
            "Sentence table contains rows missing manifest metadata after join: "
            f"{missing_manifest}"
        )

    merged["source_quarter"] = merged["source_quarter"].astype(int)
    merged["source_year"] = merged["source_year"].astype(int)
    merged["sentence_index"] = merged["sentence_index"].astype(int)
    merged["token_count"] = merged["token_count"].astype(int)
    merged["fragment_score"] = merged["fragment_score"].astype(float)
    merged["sentence_norm"] = merged["sentence_norm"].fillna("").astype(str)
    merged["sentence"] = merged["sentence"].fillna("").astype(str)
    merged["edge_case_flag"] = merged["sentence"].map(
        lambda value: bool(_EDGE_CASE_RE.search(value))
    )
    merged["length_bin"] = merged["token_count"].map(length_bin_from_tokens)
    return merged


def _allocate_quotas(
    available_by_quarter: dict[int, int],
    target_size: int,
    base_quarter_quota: int,
) -> dict[int, int]:
    quotas = {
        quarter: min(base_quarter_quota, int(available_by_quarter.get(quarter, 0)))
        for quarter in sorted(available_by_quarter)
    }
    assigned = sum(quotas.values())
    if assigned > target_size:
        raise ValueError("Base quarter allocation exceeds target size.")

    while assigned < target_size:
        progressed = False
        for quarter in sorted(quotas, key=lambda item: (quotas[item], item)):
            if quotas[quarter] >= int(available_by_quarter.get(quarter, 0)):
                continue
            quotas[quarter] += 1
            assigned += 1
            progressed = True
            if assigned == target_size:
                break
        if not progressed:
            break

    if assigned < target_size:
        raise ValueError(
            f"Eligible pool cannot satisfy target size {target_size}; only {assigned} rows "
            "available after quarter redistribution."
        )
    return quotas


def _is_known_ff12(row: pd.Series) -> bool:
    return str(row.get("industry_metadata_source", "")).strip().lower() != "unknown"


def _stage_a_key(row: pd.Series, selected_per_file: dict[str, int]) -> tuple[Any, ...]:
    return (
        selected_per_file[str(row["source_file"])],
        str(row["source_file"]),
        int(row["sentence_index"]),
        str(row["sentence_id"]),
    )


def _stage_b_key(row: pd.Series, selected_per_file: dict[str, int]) -> tuple[Any, ...]:
    return (
        selected_per_file[str(row["source_file"])],
        0 if bool(row["edge_case_flag"]) else 1,
        0 if _is_known_ff12(row) else 1,
        _LENGTH_PRIORITY.get(str(row["length_bin"]), 99),
        str(row["source_file"]),
        int(row["sentence_index"]),
        str(row["sentence_id"]),
    )


def _select_for_quarter(
    quarter_frame: pd.DataFrame,
    quota: int,
    selected_per_file: dict[str, int],
) -> list[tuple[int, str]]:
    selected: list[tuple[int, str]] = []
    remaining = quarter_frame.copy()
    remaining = remaining.sort_values(
        by=["source_file", "sentence_index", "sentence_id"]
    ).reset_index(drop=False)

    while len(selected) < quota:
        known = remaining[
            remaining["industry_metadata_source"].astype(str).str.lower() != "unknown"
        ]
        if known.empty:
            break

        progressed = False
        ff12_codes = sorted(
            {
                str(value)
                for value in known["ff12_code"].tolist()
                if pd.notna(value) and str(value).strip() != ""
            }
        )
        for ff12_code in ff12_codes:
            bucket = known[known["ff12_code"].astype(str) == ff12_code]
            if bucket.empty:
                continue
            best_row = min(
                bucket.itertuples(index=False),
                key=lambda row: _stage_a_key(pd.Series(row._asdict()), selected_per_file),
            )
            selected.append((int(best_row.index), "quarter_ff12_round_robin"))
            selected_per_file[str(best_row.source_file)] += 1
            remaining = remaining[remaining["index"] != int(best_row.index)]
            known = known[known["index"] != int(best_row.index)]
            progressed = True
            if len(selected) == quota:
                break
        if not progressed:
            break

    while len(selected) < quota and not remaining.empty:
        best_row = min(
            remaining.itertuples(index=False),
            key=lambda row: _stage_b_key(pd.Series(row._asdict()), selected_per_file),
        )
        selected.append((int(best_row.index), "quarter_diversity_fill"))
        selected_per_file[str(best_row.source_file)] += 1
        remaining = remaining[remaining["index"] != int(best_row.index)]

    return selected


def _selection_summary(batch: pd.DataFrame, quotas: dict[int, int]) -> dict[str, Any]:
    known_mask = batch["industry_metadata_source"].astype(str).str.lower() != "unknown"
    return {
        "batch_row_count": int(len(batch)),
        "target_size": int(sum(quotas.values())),
        "quota_satisfied": bool(len(batch) == sum(quotas.values())),
        "quarter_quotas_used": {str(key): int(value) for key, value in quotas.items()},
        "selected_quarter_counts": {
            str(int(key)): int(value)
            for key, value in batch["source_quarter"].value_counts().sort_index().items()
        },
        "selected_file_count": int(batch["source_file"].nunique()),
        "selected_ff12_counts": {
            str(key): int(value)
            for key, value in batch["ff12_code"].astype(str).value_counts().sort_index().items()
        },
        "selected_known_ff12_count": int(known_mask.sum()),
        "selected_unknown_ff12_count": int((~known_mask).sum()),
        "selected_length_counts": {
            str(key): int(value)
            for key, value in batch["length_bin"].value_counts().sort_index().items()
        },
        "selected_edge_case_count": int(batch["edge_case_flag"].astype(bool).sum()),
    }


def build_labeling_batch(
    sentences_path: str = DEFAULT_SENTENCES,
    manifest_path: str = DEFAULT_MANIFEST,
    held_out_path: str = DEFAULT_HELD_OUT,
    output_parquet_path: str = DEFAULT_OUTPUT_PARQUET,
    output_csv_path: str = DEFAULT_OUTPUT_CSV,
    report_path: str = DEFAULT_REPORT,
    batch_id: str = "labeling_batch_v1",
    target_size: int = 240,
    base_quarter_quota: int = 60,
    min_tokens: int = 6,
    max_tokens: int = 120,
    seed: int = 20260306,
    exclude_existing_csv: str = "",
) -> dict[str, Any]:
    candidates = _load_candidates(sentences_path=sentences_path, manifest_path=manifest_path)
    source_rows = int(len(candidates))

    clean = candidates[
        (candidates["fragment_score"] <= 0.0)
        & (candidates["token_count"] >= int(min_tokens))
        & (candidates["token_count"] <= int(max_tokens))
    ].copy()
    rows_after_clean_filters = int(len(clean))

    held_out_norms = _load_heldout_norms(held_out_path)
    overlap_mask = clean["sentence_norm"].isin(held_out_norms)
    heldout_overlap_removed = int(overlap_mask.sum())
    clean = clean[~overlap_mask].copy()

    existing_batch_excluded = 0
    if exclude_existing_csv:
        existing_sentence_text_ids = _load_existing_sentence_text_ids(exclude_existing_csv)
        existing_mask = clean["sentence_text_id"].astype(str).isin(existing_sentence_text_ids)
        existing_batch_excluded = int(existing_mask.sum())
        clean = clean[~existing_mask].copy()

    clean = clean.sort_values(
        by=["source_quarter", "source_file", "sentence_index", "sentence_id"]
    ).reset_index(drop=True)
    before_dedupe = int(len(clean))
    clean = clean.drop_duplicates(subset=["sentence_text_id"], keep="first").copy()
    exact_text_duplicates_removed = before_dedupe - int(len(clean))

    available_rows = int(len(clean))
    available_by_quarter = {
        int(key): int(value)
        for key, value in clean["source_quarter"].value_counts().sort_index().items()
    }
    available_files_by_quarter = {
        str(int(key)): int(value)
        for key, value in clean.groupby("source_quarter")["source_file"]
        .nunique()
        .sort_index()
        .items()
    }

    if available_rows < int(target_size):
        raise ValueError(
            f"Eligible pool has {available_rows} rows after filters; target size is {target_size}."
        )

    quotas = _allocate_quotas(
        available_by_quarter=available_by_quarter,
        target_size=int(target_size),
        base_quarter_quota=int(base_quarter_quota),
    )

    selected_per_file: dict[str, int] = defaultdict(int)
    selected_rows: list[tuple[int, str]] = []
    for quarter in sorted(quotas):
        quarter_frame = clean[clean["source_quarter"] == int(quarter)].copy()
        if quarter_frame.empty or quotas[quarter] == 0:
            continue
        selected_rows.extend(
            _select_for_quarter(
                quarter_frame=quarter_frame,
                quota=int(quotas[quarter]),
                selected_per_file=selected_per_file,
            )
        )

    if len(selected_rows) != int(target_size):
        raise ValueError(
            f"Selection produced {len(selected_rows)} rows; expected {target_size}. "
            "Quarter redistribution or diversity selection exhausted candidates unexpectedly."
        )

    selected_index_to_reason = {row_index: reason for row_index, reason in selected_rows}
    batch = clean.loc[sorted(selected_index_to_reason)].copy()
    batch["selection_reason"] = batch.index.map(selected_index_to_reason)
    batch["batch_id"] = batch_id
    batch["batch_row_id"] = batch["sentence_id"].map(
        lambda sentence_id: _sha1_short(f"{batch_id}|{sentence_id}")
    )
    batch["sampling_seed"] = int(seed)
    batch["label"] = ""
    batch["is_uncertain"] = ""
    batch["uncertainty_note"] = ""

    batch = batch.sort_values(
        by=["source_quarter", "selection_reason", "source_file", "sentence_index", "sentence_id"]
    ).reset_index(drop=True)
    batch = batch[OUTPUT_COLUMNS].copy()

    output_parquet = Path(output_parquet_path)
    output_parquet.parent.mkdir(parents=True, exist_ok=True)
    batch.to_parquet(output_parquet, index=False, engine="pyarrow", compression="snappy")

    output_csv = Path(output_csv_path)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    batch.to_csv(output_csv, index=False)

    quality = {
        "heldout_overlap_count": int(batch["sentence_norm"].isin(held_out_norms).sum()),
        "exact_duplicate_count": int(batch["sentence_text_id"].duplicated().sum()),
    }
    summary = {
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "git_commit": _git_commit(),
        "inputs": {
            "sentences": sentences_path,
            "manifest": manifest_path,
            "held_out": held_out_path,
            "exclude_existing_csv": exclude_existing_csv,
        },
        "parameters": {
            "batch_id": batch_id,
            "target_size": int(target_size),
            "base_quarter_quota": int(base_quarter_quota),
            "min_tokens": int(min_tokens),
            "max_tokens": int(max_tokens),
            "seed": int(seed),
        },
        "candidate_stats": {
            "source_rows": source_rows,
            "rows_after_clean_filters": rows_after_clean_filters,
            "heldout_overlap_removed": heldout_overlap_removed,
            "existing_batch_excluded": existing_batch_excluded,
            "exact_text_duplicates_removed": exact_text_duplicates_removed,
            "rows_after_filters": available_rows,
            "available_quarter_counts": {
                str(key): int(value) for key, value in available_by_quarter.items()
            },
            "available_file_counts": {
                "total_unique_files": int(clean["source_file"].nunique()),
                "quarter_unique_file_counts": available_files_by_quarter,
            },
        },
        "selection": _selection_summary(batch, quotas),
        "quality": quality,
        "artifacts": {
            "parquet": str(output_parquet),
            "csv": str(output_csv),
        },
    }

    report_file = Path(report_path)
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sentences", default=DEFAULT_SENTENCES)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--held-out", default=DEFAULT_HELD_OUT)
    parser.add_argument("--output-parquet", default=DEFAULT_OUTPUT_PARQUET)
    parser.add_argument("--output-csv", default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    parser.add_argument("--batch-id", default="labeling_batch_v1")
    parser.add_argument("--target-size", type=int, default=240)
    parser.add_argument("--base-quarter-quota", type=int, default=60)
    parser.add_argument("--min-tokens", type=int, default=6)
    parser.add_argument("--max-tokens", type=int, default=120)
    parser.add_argument("--seed", type=int, default=20260306)
    parser.add_argument("--exclude-existing-csv", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = build_labeling_batch(
        sentences_path=args.sentences,
        manifest_path=args.manifest,
        held_out_path=args.held_out,
        output_parquet_path=args.output_parquet,
        output_csv_path=args.output_csv,
        report_path=args.report,
        batch_id=args.batch_id,
        target_size=args.target_size,
        base_quarter_quota=args.base_quarter_quota,
        min_tokens=args.min_tokens,
        max_tokens=args.max_tokens,
        seed=args.seed,
        exclude_existing_csv=args.exclude_existing_csv,
    )
    print(
        "[label-ops] "
        f"selected={summary['selection']['batch_row_count']} "
        f"quarters={summary['selection']['selected_quarter_counts']}"
    )
    print(f"[label-ops] summary -> {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
