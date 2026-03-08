"""Merge verified labeling tranche CSVs into the canonical labels master artifacts."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd

from semantic_ai_washing.labeling.common import (
    ensure_allowed_label,
    normalize_sentence,
    parse_uncertain_flag,
)

DEFAULT_OUTPUT_PARQUET = "data/labels/v1/labels_master.parquet"
DEFAULT_OUTPUT_REVIEW_CSV = "data/labels/v1/labels_master_review.csv"
DEFAULT_REPORT = "reports/labels/label_expansion_summary.json"
DEFAULT_HELD_OUT = "data/validation/held_out_sentences.csv"

REQUIRED_COLUMNS = [
    "batch_id",
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
]


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _load_heldout_norms(path: str) -> set[str]:
    held_out = pd.read_csv(path)
    if "sentence" not in held_out.columns:
        raise ValueError("Held-out dataset must contain `sentence`.")
    return {
        normalize_sentence(value)
        for value in held_out["sentence"].fillna("").astype(str)
        if normalize_sentence(value)
    }


def _read_verified_csv(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path)
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Verified tranche CSV {path} missing required columns: {missing}")
    frame["source_input_path"] = str(path)
    return frame


def merge_labeling_batches(
    *,
    input_csvs: list[str],
    held_out_path: str = DEFAULT_HELD_OUT,
    output_parquet_path: str = DEFAULT_OUTPUT_PARQUET,
    output_review_csv_path: str = DEFAULT_OUTPUT_REVIEW_CSV,
    report_path: str = DEFAULT_REPORT,
) -> tuple[dict[str, Any], int]:
    if not input_csvs:
        raise ValueError("At least one verified tranche CSV is required.")

    frames = [_read_verified_csv(path) for path in input_csvs]
    combined = pd.concat(frames, ignore_index=True)
    combined["label"] = combined["label"].map(ensure_allowed_label)
    invalid_label_count = int(combined["label"].isna().sum())
    if invalid_label_count:
        combined["label"] = combined["label"].fillna("")

    combined["is_uncertain"] = combined["is_uncertain"].map(parse_uncertain_flag)
    combined["sentence_norm"] = combined["sentence_norm"].fillna("").astype(str)
    combined["label_source"] = "human_verified"
    combined["assistive_present"] = (
        combined.get("assistive_label", pd.Series(index=combined.index))
        .fillna("")
        .astype(str)
        .str.strip()
        .ne("")
    )
    combined.sort_values(
        ["source_quarter", "source_file", "sentence_index", "sentence_id"], inplace=True
    )
    combined.reset_index(drop=True, inplace=True)

    source_duplicate_count = int(combined["sentence_text_id"].duplicated().sum())
    heldout_norms = _load_heldout_norms(held_out_path)
    heldout_overlap_count = int(combined["sentence_norm"].isin(heldout_norms).sum())
    nonempty_label_count = int(combined["label"].fillna("").astype(str).str.strip().ne("").sum())

    summary = {
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "git_commit": _git_commit(),
        "inputs": {
            "verified_tranche_csvs": [str(Path(path)) for path in input_csvs],
            "held_out": held_out_path,
        },
        "summary": {
            "total_input_rows": int(len(combined)),
            "total_canonical_labeled_rows": int(nonempty_label_count),
            "min_class_count": int(
                combined[combined["label"].astype(str).str.strip().ne("")]["label"]
                .value_counts()
                .min()
            )
            if nonempty_label_count
            else 0,
        },
        "class_counts": {
            str(label): int(count)
            for label, count in combined[combined["label"].astype(str).str.strip().ne("")]["label"]
            .value_counts()
            .sort_index()
            .items()
        },
        "tranche_counts": {
            str(batch_id): int(count)
            for batch_id, count in combined["batch_id"]
            .astype(str)
            .value_counts()
            .sort_index()
            .items()
        },
        "quality": {
            "heldout_overlap_count": heldout_overlap_count,
            "exact_duplicate_count": int(source_duplicate_count),
            "invalid_label_count": invalid_label_count,
            "nonempty_label_count": nonempty_label_count,
        },
        "assistive_provenance": {
            "rows_with_assistive_columns": int(combined["assistive_present"].sum()),
            "rows_without_assistive_columns": int((~combined["assistive_present"]).sum()),
        },
        "artifacts": {
            "labels_master_parquet": output_parquet_path,
            "labels_master_review_csv": output_review_csv_path,
        },
    }

    report_file = Path(report_path)
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if invalid_label_count or heldout_overlap_count or source_duplicate_count:
        return summary, 1

    canonical = combined[combined["label"].astype(str).str.strip().ne("")].copy()
    output_parquet = Path(output_parquet_path)
    output_parquet.parent.mkdir(parents=True, exist_ok=True)
    canonical.to_parquet(output_parquet, index=False, engine="pyarrow", compression="snappy")

    output_review_csv = Path(output_review_csv_path)
    output_review_csv.parent.mkdir(parents=True, exist_ok=True)
    canonical.to_csv(output_review_csv, index=False)
    return summary, 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", nargs="+", required=True)
    parser.add_argument("--held-out", default=DEFAULT_HELD_OUT)
    parser.add_argument("--output-parquet", default=DEFAULT_OUTPUT_PARQUET)
    parser.add_argument("--output-review-csv", default=DEFAULT_OUTPUT_REVIEW_CSV)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    _, exit_code = merge_labeling_batches(
        input_csvs=args.inputs,
        held_out_path=args.held_out,
        output_parquet_path=args.output_parquet,
        output_review_csv_path=args.output_review_csv,
        report_path=args.report,
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
