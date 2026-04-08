"""Prepare a repo-local held_out_v3 candidate pool and review sheet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

DEFAULT_INPUT = (
    "data/validation/recovery_sources/"
    "held_out_sentences_v2_review_sheet_10k_only_clean_prelabeled_recovered.csv"
)
DEFAULT_CANDIDATE_OUTPUT = "data/validation/held_out_v3/held_out_sentences_v3_candidate_pool.csv"
DEFAULT_REVIEW_OUTPUT = "data/validation/held_out_v3/held_out_sentences_v3_review_sheet.csv"
DEFAULT_SLICE_OUTPUT = "data/validation/held_out_v3/held_out_sentences_v3_review_slice40.csv"
DEFAULT_REPORT = "reports/final/ai_washing_heldout_v3_preparation_v1.json"
DEFAULT_SLICE_SIZE = 40
DEFAULT_EXCLUDED_IDS = [
    "70d33b9f57a2874e",
    "773f16a020f75457",
    "ad6e625b4aa0275c",
]

REQUIRED_COLUMNS = {
    "sentence_id",
    "sentence",
    "source_cik",
    "source_year",
    "source_form",
    "source_file",
    "sentence_index",
}


def _now_utc() -> str:
    return pd.Timestamp.utcnow().isoformat()


def _read_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(Path(path).expanduser().resolve())


def _write_csv(frame: pd.DataFrame, path: str | Path) -> None:
    resolved = Path(path).expanduser().resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(resolved, index=False)


def _write_json(payload: dict[str, Any], path: str | Path) -> None:
    resolved = Path(path).expanduser().resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _blank_str_column(frame: pd.DataFrame, name: str) -> None:
    frame[name] = ""


def prepare_heldout_v3_assets(
    *,
    input_csv: str = DEFAULT_INPUT,
    candidate_output_csv: str = DEFAULT_CANDIDATE_OUTPUT,
    review_output_csv: str = DEFAULT_REVIEW_OUTPUT,
    slice_output_csv: str = DEFAULT_SLICE_OUTPUT,
    output_report: str = DEFAULT_REPORT,
    slice_size: int = DEFAULT_SLICE_SIZE,
    exclude_sentence_ids: list[str] | None = None,
) -> dict[str, Any]:
    source_path = Path(input_csv).expanduser().resolve()
    frame = _read_csv(source_path)
    missing = sorted(REQUIRED_COLUMNS - set(frame.columns))
    if missing:
        raise ValueError(f"Recovered held_out_v3 source missing required columns: {missing}")

    excluded_ids = [str(value).strip() for value in (exclude_sentence_ids or DEFAULT_EXCLUDED_IDS)]
    excluded_ids = [value for value in excluded_ids if value]

    original_rows = int(len(frame))
    original_candidate_counts = (
        frame["candidate_label"].fillna("").astype(str).value_counts().to_dict()
        if "candidate_label" in frame.columns
        else {}
    )

    frame = frame.copy()
    frame["sentence_id"] = frame["sentence_id"].astype(str)
    if excluded_ids:
        frame = frame[~frame["sentence_id"].isin(excluded_ids)].copy()

    legacy_map = {
        "candidate_label": "legacy_candidate_label",
        "assistive_label": "legacy_assistive_label",
        "assistive_confidence": "legacy_assistive_confidence",
        "assistive_rationale": "legacy_assistive_rationale",
        "assistive_model": "legacy_assistive_model",
        "assistive_generated_at": "legacy_assistive_generated_at",
        "assistive_prompt_hash": "legacy_assistive_prompt_hash",
        "benchmark_asset_role": "legacy_benchmark_asset_role",
    }
    for old_name, new_name in legacy_map.items():
        if old_name in frame.columns:
            frame = frame.rename(columns={old_name: new_name})

    # Canonical current-review columns start blank.
    for column in (
        "label",
        "review_note",
        "assistive_label",
        "assistive_confidence",
        "assistive_rationale",
        "assistive_model",
        "assistive_generated_at",
        "assistive_prompt_hash",
    ):
        _blank_str_column(frame, column)

    if "is_uncertain" not in frame.columns:
        _blank_str_column(frame, "is_uncertain")
    else:
        frame["is_uncertain"] = ""
    if "uncertainty_note" not in frame.columns:
        _blank_str_column(frame, "uncertainty_note")
    else:
        frame["uncertainty_note"] = ""

    frame["benchmark_name"] = "held_out_v3"
    frame["benchmark_asset_role"] = "canonical_current_rubric_evaluation_set_candidate_v3"
    frame["review_status"] = "pending"
    frame["rubric_version"] = "track_a_as_rubric_rewrite_v1"
    frame["recovery_source_path"] = str(source_path)
    frame["recovery_generated_at"] = _now_utc()
    frame["prelabel_eligible"] = True
    frame["skip_reason"] = ""

    sort_columns = ["source_year", "source_cik", "source_file", "sentence_index", "sentence_id"]
    frame = frame.sort_values(sort_columns).reset_index(drop=True)

    candidate_frame = frame.copy()
    review_frame = frame.copy()
    slice_frame = review_frame.head(int(slice_size)).copy()

    _write_csv(candidate_frame, candidate_output_csv)
    _write_csv(review_frame, review_output_csv)
    _write_csv(slice_frame, slice_output_csv)

    report = {
        "generated_at_utc": _now_utc(),
        "inputs": {
            "recovered_input_csv": str(source_path),
            "excluded_sentence_ids": excluded_ids,
        },
        "outputs": {
            "candidate_pool_csv": str(Path(candidate_output_csv).expanduser().resolve()),
            "review_sheet_csv": str(Path(review_output_csv).expanduser().resolve()),
            "review_slice_csv": str(Path(slice_output_csv).expanduser().resolve()),
        },
        "summary": {
            "rows_before_exclusions": original_rows,
            "rows_excluded": int(original_rows - len(candidate_frame)),
            "rows_after_exclusions": int(len(candidate_frame)),
            "slice_rows": int(len(slice_frame)),
            "original_candidate_label_distribution": original_candidate_counts,
            "legacy_assistive_present_rows": int(
                candidate_frame["legacy_assistive_label"].fillna("").astype(str).str.strip().ne("").sum()
            )
            if "legacy_assistive_label" in candidate_frame.columns
            else 0,
        },
    }
    _write_json(report, output_report)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", default=DEFAULT_INPUT)
    parser.add_argument("--candidate-output-csv", default=DEFAULT_CANDIDATE_OUTPUT)
    parser.add_argument("--review-output-csv", default=DEFAULT_REVIEW_OUTPUT)
    parser.add_argument("--slice-output-csv", default=DEFAULT_SLICE_OUTPUT)
    parser.add_argument("--output-report", default=DEFAULT_REPORT)
    parser.add_argument("--slice-size", type=int, default=DEFAULT_SLICE_SIZE)
    parser.add_argument("--exclude-sentence-ids", nargs="*", default=DEFAULT_EXCLUDED_IDS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = prepare_heldout_v3_assets(
        input_csv=args.input_csv,
        candidate_output_csv=args.candidate_output_csv,
        review_output_csv=args.review_output_csv,
        slice_output_csv=args.slice_output_csv,
        output_report=args.output_report,
        slice_size=args.slice_size,
        exclude_sentence_ids=list(args.exclude_sentence_ids),
    )
    print(
        "[heldout-v3-prepare] "
        f"rows_after_exclusions={report['summary']['rows_after_exclusions']} "
        f"slice_rows={report['summary']['slice_rows']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
