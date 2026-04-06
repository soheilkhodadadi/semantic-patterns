"""Prepare a stratified IRR subset and blinded second-rater handoff files."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
from collections import Counter
from pathlib import Path

import pandas as pd

from ai_washing_member.labeling.common import (
    ALLOWED_LABELS,
    ensure_allowed_label,
    load_table,
    write_excel,
)

REQUIRED_COLUMNS = ["sentence_id", "sentence", "label", "source_year", "ff12_code"]
MASTER_COLUMNS = [
    "irr_item_id",
    "sample_id",
    "batch_row_id",
    "sentence_id",
    "sentence",
    "source_cik",
    "source_year",
    "source_form",
    "source_file",
    "sentence_index",
    "ff12_code",
    "ff12_name",
    "label",
    "rater1_label",
    "rater2_label",
    "rater2_note",
]
BLINDED_COLUMNS = ["irr_item_id", "sentence", "rater2_label", "rater2_note"]


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _sha256_file(path: str | Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _normalize_input(df: pd.DataFrame) -> pd.DataFrame:
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for IRR subset prep: {missing}")

    out = df.copy()
    out["label"] = out["label"].map(ensure_allowed_label)
    out = out[out["label"].isin(ALLOWED_LABELS)].copy()
    if out.empty:
        raise ValueError("No valid labeled rows available for IRR subset.")

    text_columns = [
        "sentence_id",
        "sentence",
        "source_year",
        "source_form",
        "source_cik",
        "source_file",
        "sentence_index",
        "ff12_code",
        "ff12_name",
        "batch_row_id",
    ]
    for column in text_columns:
        if column not in out.columns:
            out[column] = ""
        out[column] = out[column].fillna("").astype(str)

    if "sample_id" not in out.columns:
        out["sample_id"] = ""
    out["sample_id"] = out["sample_id"].fillna("").astype(str)
    sample_missing = out["sample_id"].str.strip() == ""
    out.loc[sample_missing, "sample_id"] = out.loc[sample_missing, "batch_row_id"]
    sample_missing = out["sample_id"].str.strip() == ""
    out.loc[sample_missing, "sample_id"] = out.loc[sample_missing, "sentence_id"]

    out["firm_key"] = out["source_cik"].where(
        out["source_cik"].str.strip() != "", out["source_file"]
    )
    blank_firm = out["firm_key"].fillna("").astype(str).str.strip() == ""
    out.loc[blank_firm, "firm_key"] = out.loc[blank_firm, "sample_id"]
    out["stratum_key"] = (
        out["source_year"].fillna("unknown").astype(str)
        + "|"
        + out["ff12_code"].fillna("unknown").astype(str)
        + "|"
        + out["label"].astype(str)
    )
    return out.reset_index(drop=True)


def _make_irr_item_id(sample_id: str, sentence_id: str) -> str:
    payload = f"{sample_id}|{sentence_id}|irr"
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


def _candidate_priority(
    row: pd.Series,
    *,
    used_firms: set[str],
    selected_strata: Counter,
    available_rows: pd.DataFrame,
    rng: random.Random,
) -> tuple[int, int, int, float, str]:
    stratum = row["stratum_key"]
    firm = row["firm_key"]
    stratum_size = int((available_rows["stratum_key"] == stratum).sum())
    return (
        0 if firm not in used_firms else 1,
        selected_strata.get(stratum, 0),
        stratum_size,
        rng.random(),
        str(row["sample_id"]),
    )


def _pick_rows(
    data: pd.DataFrame,
    *,
    per_label_target: int,
    min_unique_firms: int,
    seed: int,
) -> pd.DataFrame:
    available = data.copy()
    selected_rows: list[pd.Series] = []
    used_firms: set[str] = set()
    selected_strata: Counter = Counter()
    rng = random.Random(seed)

    for round_idx in range(per_label_target):
        for label in ALLOWED_LABELS:
            label_rows = available[available["label"] == label]
            if label_rows.empty:
                raise ValueError(f"Insufficient rows available for label quota: {label}")
            ordered = sorted(
                label_rows.index.tolist(),
                key=lambda idx: _candidate_priority(
                    available.loc[idx],
                    used_firms=used_firms,
                    selected_strata=selected_strata,
                    available_rows=label_rows,
                    rng=rng,
                ),
            )
            next_idx = ordered[0]
            row = available.loc[next_idx].copy()
            selected_rows.append(row)
            used_firms.add(str(row["firm_key"]))
            selected_strata[str(row["stratum_key"])] += 1
            available = available.drop(index=next_idx)

    selected = pd.DataFrame(selected_rows).reset_index(drop=True)
    if selected["firm_key"].nunique() >= min_unique_firms:
        return selected

    # Repair repeated-firm picks with unused firms from the same label when possible.
    remaining = available.copy()
    while selected["firm_key"].nunique() < min_unique_firms:
        duplicated = selected[selected["firm_key"].duplicated(keep=False)].copy()
        if duplicated.empty:
            break
        replaced = False
        for idx, row in duplicated.sort_values(
            by=["label", "firm_key", "sample_id"], ascending=[True, True, True]
        ).iterrows():
            label = row["label"]
            used_elsewhere = set(selected.drop(index=idx)["firm_key"].astype(str))
            candidates = remaining[
                (remaining["label"] == label)
                & (~remaining["firm_key"].astype(str).isin(used_elsewhere))
            ].copy()
            if candidates.empty:
                continue
            candidates = candidates.sort_values(
                by=["stratum_key", "sample_id"], ascending=[True, True]
            )
            replacement_idx = candidates.index[0]
            replacement = remaining.loc[replacement_idx].copy()
            remaining = pd.concat([remaining.drop(index=replacement_idx), row.to_frame().T])
            selected.loc[idx] = replacement
            replaced = True
            break
        if not replaced:
            break

    if selected["firm_key"].nunique() < min_unique_firms:
        raise ValueError(
            "Unable to satisfy minimum unique firm coverage for IRR subset. "
            f"selected={selected['firm_key'].nunique()} target={min_unique_firms}"
        )
    return selected


def _build_blinded(master: pd.DataFrame) -> pd.DataFrame:
    blinded = master[BLINDED_COLUMNS].copy()
    blinded["rater2_label"] = ""
    blinded["rater2_note"] = ""
    return blinded


def _industry_year_balanced(subset: pd.DataFrame, source: pd.DataFrame) -> bool:
    available_years = sorted(source["source_year"].dropna().astype(str).unique().tolist())
    if not available_years:
        return False
    for label in ALLOWED_LABELS:
        selected = subset[subset["label"] == label]
        source_rows = source[source["label"] == label]
        if selected.empty or source_rows.empty:
            return False
        selected_years = sorted(selected["source_year"].dropna().astype(str).unique().tolist())
        if selected_years != available_years:
            return False
        available_ff12 = source_rows["ff12_code"].dropna().astype(str).nunique()
        selected_ff12 = selected["ff12_code"].dropna().astype(str).nunique()
        if selected_ff12 < min(2, available_ff12):
            return False
    return True


def _resolve_outputs(args: argparse.Namespace) -> dict[str, Path]:
    output_dir = Path(getattr(args, "output_dir", "data/labels/v1"))
    report_dir = Path(getattr(args, "report_dir", "reports/labels"))
    return {
        "subset_parquet": Path(getattr(args, "output_parquet", output_dir / "irr_subset.parquet")),
        "master_csv": Path(
            getattr(args, "output_master_csv", output_dir / "irr_subset_master.csv")
        ),
        "blinded_csv": Path(
            getattr(
                args,
                "output_blinded_csv",
                output_dir / "irr_subset_rater2_blinded.csv",
            )
        ),
        "blinded_xlsx": Path(
            getattr(
                args,
                "output_blinded_xlsx",
                output_dir / "irr_subset_rater2_blinded.xlsx",
            )
        ),
        "report": Path(
            getattr(
                args,
                "output_report",
                report_dir / "irr_subset_sampling_report.json",
            )
        ),
        "attestation": Path(
            getattr(args, "attestation_output", report_dir / "irr_attestation.json")
        ),
    }


def run_prepare(args: argparse.Namespace) -> dict:
    input_path = Path(args.input)
    outputs = _resolve_outputs(args)
    for path in outputs.values():
        path.parent.mkdir(parents=True, exist_ok=True)

    raw = load_table(input_path)
    data = _normalize_input(raw)

    per_label_target = int(getattr(args, "class_quota", getattr(args, "min_per_class", 40)))
    target_size = int(getattr(args, "target_size", per_label_target * len(ALLOWED_LABELS)))
    expected_total = per_label_target * len(ALLOWED_LABELS)
    if target_size != expected_total:
        raise ValueError(
            f"IRR target size must equal len(ALLOWED_LABELS) * class_quota. "
            f"got target_size={target_size} expected={expected_total}"
        )
    min_unique_firms = int(getattr(args, "min_unique_firms", 100))
    seed = int(getattr(args, "seed", 20260314))

    selected = _pick_rows(
        data,
        per_label_target=per_label_target,
        min_unique_firms=min_unique_firms,
        seed=seed,
    )
    selected = selected.sort_values(
        by=["source_year", "ff12_code", "label", "sample_id", "sentence_index"],
        ascending=[True, True, True, True, True],
    ).reset_index(drop=True)
    selected["irr_item_id"] = selected.apply(
        lambda row: _make_irr_item_id(str(row["sample_id"]), str(row["sentence_id"])),
        axis=1,
    )
    selected["rater1_label"] = selected["label"]
    selected["rater2_label"] = ""
    selected["rater2_note"] = ""

    subset_parquet = selected[MASTER_COLUMNS].copy()
    subset_parquet.to_parquet(outputs["subset_parquet"], index=False)

    master = selected[MASTER_COLUMNS].copy()
    master.to_csv(outputs["master_csv"], index=False)

    blinded = _build_blinded(master)
    blinded.to_csv(outputs["blinded_csv"], index=False)
    write_excel(outputs["blinded_xlsx"], blinded)

    unique_firms = int(selected["firm_key"].nunique())
    class_counts = selected["label"].value_counts().to_dict()
    class_targets_met = all(
        class_counts.get(label, 0) == per_label_target for label in ALLOWED_LABELS
    )
    industry_year_balanced = _industry_year_balanced(selected, data)

    sampling_report = {
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "git_commit": _git_commit(),
        "inputs": {
            "input": str(input_path),
            "input_sha256": _sha256_file(input_path),
        },
        "parameters": {
            "target_size": target_size,
            "class_quota": per_label_target,
            "min_unique_firms": min_unique_firms,
            "seed": seed,
            "blind_mode": str(getattr(args, "blind_mode", "text_only")),
        },
        "summary": {
            "rows_input": int(len(data)),
            "rows_selected": int(len(selected)),
            "selected_class_counts": {
                label: int(class_counts.get(label, 0)) for label in ALLOWED_LABELS
            },
            "selected_year_counts": {
                str(key): int(value)
                for key, value in selected["source_year"].value_counts().sort_index().items()
            },
            "selected_ff12_counts": {
                str(key): int(value)
                for key, value in selected["ff12_code"].value_counts().sort_index().items()
            },
            "selected_label_strata_counts": {
                str(key): int(value)
                for key, value in selected["stratum_key"].value_counts().sort_index().items()
            },
            "unique_firms": unique_firms,
            "stratified_100_firms_min": bool(
                unique_firms >= min_unique_firms and class_targets_met
            ),
            "industry_year_balanced": bool(industry_year_balanced),
        },
        "artifacts": {
            "subset_parquet": str(outputs["subset_parquet"]),
            "master_csv": str(outputs["master_csv"]),
            "blinded_csv": str(outputs["blinded_csv"]),
            "blinded_xlsx": str(outputs["blinded_xlsx"]),
        },
    }
    outputs["report"].write_text(json.dumps(sampling_report, indent=2), encoding="utf-8")

    attestation = {
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "git_commit": _git_commit(),
        "blind_mode": str(getattr(args, "blind_mode", "text_only")),
        "handoff_formats": ["csv", "xlsx"],
        "human_human_only": True,
        "third_adjudicator_used": False,
        "second_rater_completed": False,
        "third_adjudicator_completed": False,
        "rater1_initials": "",
        "rater2_initials": "",
        "adjudicator_initials": "",
        "notes": "",
    }
    outputs["attestation"].write_text(json.dumps(attestation, indent=2), encoding="utf-8")
    return sampling_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a stratified IRR subset and blinded second-rater handoff files."
    )
    parser.add_argument("--input", default="data/labels/v1/labels_master.parquet")
    parser.add_argument("--output-parquet", default="data/labels/v1/irr_subset.parquet")
    parser.add_argument("--output-master-csv", default="data/labels/v1/irr_subset_master.csv")
    parser.add_argument(
        "--output-blinded-csv",
        default="data/labels/v1/irr_subset_rater2_blinded.csv",
    )
    parser.add_argument(
        "--output-blinded-xlsx",
        default="data/labels/v1/irr_subset_rater2_blinded.xlsx",
    )
    parser.add_argument(
        "--output-report",
        default="reports/labels/irr_subset_sampling_report.json",
    )
    parser.add_argument(
        "--attestation-output",
        default="reports/labels/irr_attestation.json",
    )
    parser.add_argument("--target-size", type=int, default=120)
    parser.add_argument("--class-quota", type=int, default=40)
    parser.add_argument("--min-unique-firms", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260314)
    parser.add_argument("--blind-mode", choices=("text_only",), default="text_only")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_prepare(args)
    print(
        "[irr] subset prepared "
        f"rows={report['summary']['rows_selected']} "
        f"unique_firms={report['summary']['unique_firms']}"
    )
    print(f"[irr] report -> {args.output_report}")


if __name__ == "__main__":
    main()
