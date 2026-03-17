"""Publish the finalized adjudicated IRR slice as a diagnostic boundary benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from semantic_ai_washing.labeling.common import ALLOWED_LABELS, load_table


OUTPUT_COLUMNS = [
    "irr_item_id",
    "sentence_id",
    "sentence",
    "label",
    "source_cik",
    "source_year",
    "source_form",
    "source_file",
    "sentence_index",
    "ff12_code",
    "ff12_name",
    "rater1_label",
    "rater2_label",
    "disagreement_pair",
    "transition",
    "resolution_source",
    "is_disagreement_case",
    "benchmark_role",
]


def run_build(args: argparse.Namespace) -> dict:
    frame = load_table(args.adjudication)
    if "resolved_label" not in frame.columns:
        raise ValueError("Adjudication parquet must include `resolved_label`.")
    benchmark = frame[frame["resolved_label"].isin(ALLOWED_LABELS)].copy()
    if benchmark.empty:
        raise ValueError("Adjudication parquet does not contain resolved rows.")
    benchmark["label"] = benchmark["resolved_label"]
    benchmark["is_disagreement_case"] = (
        benchmark["disagreement_pair"].fillna("").astype(str).ne("")
    )
    benchmark["benchmark_role"] = "boundary_benchmark_v1"
    for column in OUTPUT_COLUMNS:
        if column not in benchmark.columns:
            benchmark[column] = ""
    benchmark = benchmark[OUTPUT_COLUMNS].copy()

    output_csv = Path(args.output_csv)
    output_json = Path(args.output_report)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    benchmark.to_csv(output_csv, index=False)

    summary = {
        "status": "passed",
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "summary": {
            "status": "passed",
            "rows_total": int(len(benchmark)),
            "rows_disagreement_case": int(benchmark["is_disagreement_case"].sum()),
            "rows_agreement_case": int((~benchmark["is_disagreement_case"]).sum()),
            "label_counts": benchmark["label"].value_counts().to_dict(),
            "resolution_source_counts": benchmark["resolution_source"]
            .fillna("")
            .value_counts()
            .to_dict(),
        },
        "outputs": {
            "benchmark_csv": str(output_csv),
        },
    }
    output_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adjudication", default="data/labels/v1/adjudication.parquet")
    parser.add_argument("--output-csv", default="data/validation/irr_boundary_benchmark_v1.csv")
    parser.add_argument(
        "--output-report", default="reports/validation/irr_boundary_benchmark_v1.json"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run_build(args)
    print(
        "[irr-boundary] published "
        f"rows={summary['summary']['rows_total']} disagreements={summary['summary']['rows_disagreement_case']}"
    )
    print(f"[irr-boundary] csv -> {args.output_csv}")


if __name__ == "__main__":
    main()
