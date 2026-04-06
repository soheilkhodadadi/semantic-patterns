"""Initialize a canonical review sheet from assistive prelabels."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

DEFAULT_SLICE_SIZE = 40


def initialize_review_sheet(
    *,
    input_csv: str,
    output_csv: str,
    slice_output_csv: str = "",
    slice_size: int = DEFAULT_SLICE_SIZE,
    existing_review_csv: str = "",
) -> tuple[int, int]:
    frame = pd.read_csv(input_csv)
    for column in ("label", "is_uncertain", "uncertainty_note"):
        if column not in frame.columns:
            frame[column] = ""
        frame[column] = ""

    if existing_review_csv:
        existing = pd.read_csv(existing_review_csv)
        if "sentence_id" not in frame.columns or "sentence_id" not in existing.columns:
            raise ValueError("existing_review_csv requires sentence_id in both inputs")
        carry = existing[["sentence_id", "label", "is_uncertain", "uncertainty_note"]].copy()
        for column in ("label", "is_uncertain", "uncertainty_note"):
            carry[column] = carry[column].fillna("").astype(str)
        frame = frame.drop(columns=["label", "is_uncertain", "uncertainty_note"]).merge(
            carry,
            on="sentence_id",
            how="left",
        )
        for column in ("label", "is_uncertain", "uncertainty_note"):
            frame[column] = frame[column].fillna("").astype(str)

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)

    written_slice_rows = 0
    if slice_output_csv:
        slice_frame = frame.head(int(slice_size)).copy()
        slice_path = Path(slice_output_csv)
        slice_path.parent.mkdir(parents=True, exist_ok=True)
        slice_frame.to_csv(slice_path, index=False)
        written_slice_rows = int(len(slice_frame))

    return int(len(frame)), written_slice_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--slice-output-csv", default="")
    parser.add_argument("--slice-size", type=int, default=DEFAULT_SLICE_SIZE)
    parser.add_argument("--existing-review-csv", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    total_rows, slice_rows = initialize_review_sheet(
        input_csv=args.input_csv,
        output_csv=args.output_csv,
        slice_output_csv=args.slice_output_csv,
        slice_size=args.slice_size,
        existing_review_csv=args.existing_review_csv,
    )
    print(
        "[review-sheet] "
        f"initialized_rows={total_rows} slice_rows={slice_rows} output={args.output_csv}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
