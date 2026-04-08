"""Freeze a reviewed held_out_v3 sheet into the canonical benchmark asset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

ALLOWED_LABELS = {"Actionable", "Speculative", "Irrelevant"}

DEFAULT_REVIEWED_INPUT = "data/validation/held_out_v3/held_out_sentences_v3_review_sheet.csv"
DEFAULT_OUTPUT_CSV = "data/validation/held_out_v3/held_out_sentences_v3.csv"
DEFAULT_OUTPUT_REPORT = "reports/final/ai_washing_heldout_v3_freeze_v1.json"


def _normalize_label(value: Any) -> str:
    if pd.isna(value):
        return ""
    text = str(value or "").strip()
    if text and text not in ALLOWED_LABELS:
        raise ValueError(f"Unexpected label in held_out_v3 review sheet: {text!r}")
    return text


def _write_json(payload: dict[str, Any], path: str | Path) -> None:
    resolved = Path(path).expanduser().resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def freeze_heldout_v3(
    *,
    reviewed_input: str = DEFAULT_REVIEWED_INPUT,
    output_csv: str = DEFAULT_OUTPUT_CSV,
    output_report: str = DEFAULT_OUTPUT_REPORT,
) -> tuple[dict[str, Any], int]:
    reviewed_path = Path(reviewed_input).expanduser().resolve()
    frame = pd.read_csv(reviewed_path).copy()
    required = {"sentence_id", "sentence", "label"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Held_out_v3 review sheet missing required columns: {missing}")

    frame["label"] = frame["label"].map(_normalize_label)
    pending = frame[frame["label"].eq("")].copy()
    counts = frame.loc[frame["label"].ne(""), "label"].value_counts().to_dict()

    report = {
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "inputs": {
            "reviewed_input": str(reviewed_path),
        },
        "summary": {
            "status": "pending_review" if len(pending) else "frozen",
            "rows_total": int(len(frame)),
            "rows_pending_review": int(len(pending)),
            "label_counts": counts,
            "benchmark_name": "held_out_v3",
        },
        "outputs": {
            "held_out_v3_csv": str(Path(output_csv).expanduser().resolve()),
        },
    }

    if len(pending):
        _write_json(report, output_report)
        return report, 1

    frozen = frame.drop(columns=[c for c in ("legacy_candidate_label",) if c in frame.columns])
    output_path = Path(output_csv).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frozen.to_csv(output_path, index=False)
    _write_json(report, output_report)
    return report, 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewed-input", default=DEFAULT_REVIEWED_INPUT)
    parser.add_argument("--output-csv", default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-report", default=DEFAULT_OUTPUT_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report, exit_code = freeze_heldout_v3(
        reviewed_input=args.reviewed_input,
        output_csv=args.output_csv,
        output_report=args.output_report,
    )
    print(
        "[heldout-v3-freeze] "
        f"status={report['summary']['status']} "
        f"rows_pending_review={report['summary']['rows_pending_review']}"
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
