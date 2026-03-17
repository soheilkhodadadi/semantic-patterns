"""Freeze a reviewed held-out v2 sheet into the canonical evaluation asset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from semantic_ai_washing.labeling.common import ALLOWED_LABELS, ensure_allowed_label, load_table

TARGET_COUNTS = {"Actionable": 60, "Speculative": 60, "Irrelevant": 60}


def run_freeze(args: argparse.Namespace) -> tuple[dict, int]:
    reviewed = load_table(args.reviewed_input)
    required = {"sentence_id", "sentence", "label"}
    missing = sorted(required - set(reviewed.columns))
    if missing:
        raise ValueError(f"Reviewed hold-out v2 sheet missing required columns: {missing}")
    reviewed = reviewed.copy()
    reviewed["label"] = reviewed["label"].map(ensure_allowed_label)
    pending = reviewed[reviewed["label"].isna()].copy()
    output_csv = Path(args.output_csv)
    output_report = Path(args.output_report)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_report.parent.mkdir(parents=True, exist_ok=True)

    status = "pending_review"
    exit_code = 1
    counts = {label: int((reviewed["label"] == label).sum()) for label in ALLOWED_LABELS}
    if pending.empty and counts == TARGET_COUNTS:
        status = "frozen"
        exit_code = 0
        reviewed[[column for column in reviewed.columns if column != "candidate_label"]].to_csv(
            output_csv, index=False
        )

    report = {
        "status": status,
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "summary": {
            "status": status,
            "rows_total": int(len(reviewed)),
            "rows_pending_review": int(len(pending)),
            "label_counts": counts,
            "target_counts": TARGET_COUNTS,
        },
        "outputs": {
            "held_out_v2_csv": str(output_csv),
        },
    }
    output_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report, exit_code


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reviewed-input", default="data/validation/held_out_sentences_v2_review_sheet.xlsx"
    )
    parser.add_argument("--output-csv", default="data/validation/held_out_sentences_v2.csv")
    parser.add_argument(
        "--output-report", default="reports/validation/held_out_sentences_v2_freeze.json"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report, exit_code = run_freeze(args)
    print(f"[heldout-v2-freeze] status={report['status']}")
    print(f"[heldout-v2-freeze] report -> {args.output_report}")
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
