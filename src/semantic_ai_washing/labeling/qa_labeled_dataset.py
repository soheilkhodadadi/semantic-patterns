"""QA checks for Phase 1 expanded labeled dataset."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from collections import Counter
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd

from semantic_ai_washing.labeling.common import (
    ALLOWED_LABELS,
    ensure_allowed_label,
    normalize_sentence,
    parse_uncertain_flag,
    safe_int,
    token_count,
)

OUTPUT_COLUMNS = [
    "sample_id",
    "sentence_id",
    "sentence",
    "sentence_norm",
    "label",
    "is_uncertain",
    "uncertainty_note",
    "source_file",
    "source_year",
    "source_form",
    "source_cik",
    "sentence_index",
    "sic",
    "sic2",
    "ff12_code",
    "ff12_name",
    "token_count",
    "length_bin",
    "edge_case_flag",
]

REQUIRED_COLUMNS = [
    "sample_id",
    "sentence_id",
    "sentence",
    "sentence_norm",
    "label",
    "is_uncertain",
    "token_count",
]


@dataclass
class QASummary:
    status: str
    violations: list[str]
    row_count: int
    class_counts: dict[str, int]
    leakage_overlap_count: int
    near_duplicate_pair_count: int
    sample_id_duplicate_count: int
    sentence_id_duplicate_count: int
    sentence_norm_duplicate_count: int


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _file_sha256(path: str) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _load_heldout_norms(path: str) -> set[str]:
    heldout: set[str] = set()
    with open(path, newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            norm = normalize_sentence(row.get("sentence", ""))
            if norm:
                heldout.add(norm)
    return heldout


def _read_json_if_exists(path: str | None) -> dict | None:
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _compute_near_duplicate_pairs(df: pd.DataFrame, threshold: float) -> list[dict]:
    rows = df.reset_index(drop=True)
    pairs = []
    for i in range(len(rows)):
        sentence_i = rows.at[i, "sentence_norm"]
        for j in range(i + 1, len(rows)):
            ratio = SequenceMatcher(None, sentence_i, rows.at[j, "sentence_norm"]).ratio()
            if ratio >= threshold:
                pairs.append(
                    {
                        "sample_id_a": rows.at[i, "sample_id"],
                        "sample_id_b": rows.at[j, "sample_id"],
                        "sentence_id_a": rows.at[i, "sentence_id"],
                        "sentence_id_b": rows.at[j, "sentence_id"],
                        "label_a": rows.at[i, "label"],
                        "label_b": rows.at[j, "label"],
                        "similarity": round(float(ratio), 6),
                    }
                )
    return pairs


def _prepare_df(input_path: str) -> pd.DataFrame:
    df = pd.read_csv(input_path)
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    out = df.copy()
    for col in OUTPUT_COLUMNS:
        if col not in out.columns:
            out[col] = ""

    out["sentence"] = out["sentence"].fillna("").astype(str)
    out["sentence_norm"] = out["sentence_norm"].fillna("").astype(str).map(normalize_sentence)
    empty_norm = out["sentence_norm"].eq("")
    out.loc[empty_norm, "sentence_norm"] = out.loc[empty_norm, "sentence"].map(normalize_sentence)

    out["label"] = out["label"].map(ensure_allowed_label)
    out["is_uncertain"] = out["is_uncertain"].map(parse_uncertain_flag)
    out["token_count"] = out["token_count"].map(lambda v: safe_int(v, default=0))
    out["token_count"] = out["token_count"].where(
        out["token_count"] > 0, out["sentence"].map(token_count)
    )
    out["sample_id"] = out["sample_id"].fillna("").astype(str)
    out["sentence_id"] = out["sentence_id"].fillna("").astype(str)

    # Keep only rows intended for training set in final QA output.
    out = out[out["is_uncertain"] == 0].copy().reset_index(drop=True)
    return out


def _build_metadata(
    args: argparse.Namespace,
    final_df: pd.DataFrame,
    heldout_overlap_count: int,
) -> dict:
    sampling_summary = _read_json_if_exists(args.sampling_summary)
    dedupe_report = _read_json_if_exists(args.dedupe_report)

    metadata = {
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "git_commit": _git_commit(),
        "rubric_path": args.rubric_path,
        "source_files": {
            "preqa_dataset": args.input,
            "held_out_dataset": args.held_out,
            "sampling_summary": args.sampling_summary,
            "dedupe_report": args.dedupe_report,
        },
        "source_fingerprints": {
            "preqa_dataset_sha256": _file_sha256(args.input),
            "held_out_dataset_sha256": _file_sha256(args.held_out),
        },
        "normalization": {
            "sentence_norm": "lowercase + strip punctuation + collapse whitespace",
            "sentence_id": "sha1(sentence_norm)[:16] (generated earlier in pipeline)",
            "sample_id": "sha1(source_file|sentence_index|sentence_norm)[:16] (generated earlier in pipeline)",
        },
        "dedupe": {
            "method": "exact sentence_norm + near-duplicate SequenceMatcher",
            "near_duplicate_threshold": args.near_threshold,
            "dedupe_report_stats": (dedupe_report or {}).get("stats", {}),
        },
        "leakage_policy": {
            "held_out_file_frozen": args.held_out,
            "overlap_exclusions_by_sentence_norm": int(heldout_overlap_count),
        },
        "sampling": {
            "seed": ((sampling_summary or {}).get("parameters") or {}).get("seed"),
            "summary": (sampling_summary or {}).get("sampling", {}),
        },
        "qa_parameters": {
            "min_tokens": args.min_tokens,
            "min_class_count": args.min_class_count,
            "target_size": args.target_size,
            "enforce_target_size": not args.allow_target_size_mismatch,
            "near_threshold": args.near_threshold,
        },
        "final_dataset": {
            "path": args.output,
            "rows": int(len(final_df)),
            "class_counts": Counter(final_df["label"].tolist()),
        },
        "artifacts": {
            "qa_report": args.report,
            "leakage_overlap_report": args.leakage_report,
            "dataset_metadata": args.metadata_output,
        },
    }
    return metadata


def run_qa(args: argparse.Namespace) -> dict:
    input_path = Path(args.input)
    output_path = Path(args.output)
    report_path = Path(args.report)
    leakage_report_path = Path(args.leakage_report)
    metadata_path = Path(args.metadata_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    leakage_report_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    violations: list[str] = []
    heldout_norms = _load_heldout_norms(args.held_out)
    df = _prepare_df(str(input_path))

    empty_sentence_count = int(df["sentence"].fillna("").astype(str).str.strip().eq("").sum())
    if empty_sentence_count > 0:
        violations.append(f"empty_sentence_count={empty_sentence_count}")

    missing_label_count = int(df["label"].isna().sum())
    if missing_label_count > 0:
        violations.append(f"missing_label_count={missing_label_count}")

    invalid_label_count = int((~df["label"].isin(ALLOWED_LABELS)).sum())
    if invalid_label_count > 0:
        violations.append(f"invalid_label_count={invalid_label_count}")

    short_token_count = int((df["token_count"] < args.min_tokens).sum())
    if short_token_count > 0:
        violations.append(f"below_min_tokens_count={short_token_count}")

    sentence_norm_duplicate_count = int(df["sentence_norm"].duplicated().sum())
    if sentence_norm_duplicate_count > 0:
        violations.append(f"sentence_norm_duplicates={sentence_norm_duplicate_count}")

    sample_id_duplicate_count = int(df["sample_id"].duplicated().sum())
    if sample_id_duplicate_count > 0:
        violations.append(f"sample_id_duplicates={sample_id_duplicate_count}")

    sentence_id_duplicate_count = int(df["sentence_id"].duplicated().sum())
    if sentence_id_duplicate_count > 0:
        violations.append(f"sentence_id_duplicates={sentence_id_duplicate_count}")

    leakage_mask = df["sentence_norm"].isin(heldout_norms)
    leakage_df = df[leakage_mask].copy()
    leakage_overlap_count = int(len(leakage_df))
    if leakage_overlap_count > 0:
        violations.append(f"held_out_overlap_count={leakage_overlap_count}")

    near_duplicate_pairs = _compute_near_duplicate_pairs(df, threshold=args.near_threshold)
    near_duplicate_pair_count = len(near_duplicate_pairs)
    if near_duplicate_pair_count > 0:
        violations.append(f"near_duplicate_pair_count={near_duplicate_pair_count}")

    class_counts = Counter(df["label"].tolist())
    for label in ALLOWED_LABELS:
        count = int(class_counts.get(label, 0))
        if count < args.min_class_count:
            violations.append(f"class_count_below_min:{label}={count}<{args.min_class_count}")

    if not args.allow_target_size_mismatch and len(df) != args.target_size:
        violations.append(f"target_size_mismatch:{len(df)}!={args.target_size}")

    leakage_columns = [
        "sample_id",
        "sentence_id",
        "sentence_norm",
        "sentence",
        "label",
        "source_file",
        "source_year",
    ]
    if leakage_df.empty:
        pd.DataFrame(columns=leakage_columns).to_csv(leakage_report_path, index=False)
    else:
        leakage_df[leakage_columns].to_csv(leakage_report_path, index=False)

    status = "pass" if not violations else "fail"
    if status == "pass":
        df[OUTPUT_COLUMNS].to_csv(output_path, index=False)

    qa_summary = QASummary(
        status=status,
        violations=violations,
        row_count=int(len(df)),
        class_counts={k: int(v) for k, v in class_counts.items()},
        leakage_overlap_count=leakage_overlap_count,
        near_duplicate_pair_count=near_duplicate_pair_count,
        sample_id_duplicate_count=sample_id_duplicate_count,
        sentence_id_duplicate_count=sentence_id_duplicate_count,
        sentence_norm_duplicate_count=sentence_norm_duplicate_count,
    )
    report = {
        "inputs": {
            "input": args.input,
            "held_out": args.held_out,
        },
        "parameters": {
            "min_tokens": args.min_tokens,
            "min_class_count": args.min_class_count,
            "target_size": args.target_size,
            "allow_target_size_mismatch": args.allow_target_size_mismatch,
            "near_threshold": args.near_threshold,
        },
        "summary": qa_summary.__dict__,
        "artifacts": {
            "output_dataset": args.output if status == "pass" else "",
            "qa_report": args.report,
            "leakage_overlap_report": args.leakage_report,
            "dataset_metadata": args.metadata_output,
        },
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    metadata = _build_metadata(args=args, final_df=df, heldout_overlap_count=leakage_overlap_count)
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run QA gates for expanded labeled dataset.")
    parser.add_argument("--input", required=True, help="Pre-QA expanded dataset CSV.")
    parser.add_argument(
        "--held-out", required=True, help="Frozen held-out CSV for leakage checks."
    )
    parser.add_argument("--min-tokens", type=int, default=6)
    parser.add_argument("--min-class-count", type=int, default=60)
    parser.add_argument("--target-size", type=int, default=400)
    parser.add_argument(
        "--allow-target-size-mismatch",
        action="store_true",
        help="If set, do not fail when final row count differs from target-size.",
    )
    parser.add_argument(
        "--near-threshold",
        type=float,
        default=0.95,
        help="Near-duplicate threshold checked during QA.",
    )
    parser.add_argument("--output", required=True, help="Final QA-passed dataset output path.")
    parser.add_argument("--report", required=True, help="QA report JSON output path.")
    parser.add_argument(
        "--leakage-report",
        required=True,
        help="CSV listing held-out overlaps discovered during QA.",
    )
    parser.add_argument(
        "--metadata-output",
        default="data/labels/iteration1/dataset_metadata.json",
        help="Dataset metadata JSON output path.",
    )
    parser.add_argument(
        "--rubric-path",
        default="docs/labeling_protocol.md",
        help="Path to labeling rubric doc referenced in dataset metadata.",
    )
    parser.add_argument(
        "--sampling-summary",
        default="reports/iteration1/phase1/sampling_summary.json",
        help="Path to sampling summary JSON for metadata linkage.",
    )
    parser.add_argument(
        "--dedupe-report",
        default="reports/iteration1/phase1/dedupe_report.json",
        help="Path to dedupe report JSON for metadata linkage.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_qa(args)
    status = report["summary"]["status"]
    row_count = report["summary"]["row_count"]
    violations = report["summary"]["violations"]
    print(f"[phase1] qa status={status} rows={row_count} violations={len(violations)}")
    print(f"[phase1] qa report -> {args.report}")
    if status != "pass":
        for item in violations:
            print(f"[phase1] violation: {item}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
