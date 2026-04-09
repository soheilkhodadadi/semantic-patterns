"""Build held_out_v4 benchmark assets from a finalized adjudicated IRR pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from ai_washing_member.labeling.common import ALLOWED_LABELS, ensure_allowed_label, load_table

DEFAULT_MASTER = "data/labels/v1/irr_subset_boundary_revised_v2_master.csv"
DEFAULT_RATER2 = "data/labels/v2/irr_subset_boundary_revised_v2_rater2_blinded_Filled.xlsx"
DEFAULT_ADJUDICATION = "data/labels/v2/adjudication_boundary_revised_v2_final.parquet"
DEFAULT_BENCHMARK_CSV = "data/validation/held_out_v4/held_out_sentences_v4.csv"
DEFAULT_INPUT_CSV = "data/validation/held_out_v4/held_out_sentences_v4_input.csv"
DEFAULT_REPORT = "reports/final/ai_washing_heldout_v4_build_v1.json"

BENCHMARK_COLUMNS = [
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
    "source_section",
    "ff12_code",
    "ff12_name",
    "label",
    "review_note",
    "rater1_label",
    "rater2_label",
    "rater2_note",
    "disagreement_pair",
    "transition",
    "resolution_source",
    "adjudication_note",
    "benchmark_name",
    "benchmark_asset_role",
    "review_status",
    "rubric_version",
    "prelabel_eligible",
    "skip_reason",
]


def _clean_label(value: Any) -> str:
    label = ensure_allowed_label(value)
    return label or ""


def _resolve_note(rater2_note: str, adjudication_note: str) -> str:
    adjudication_note = str(adjudication_note or "").strip()
    if adjudication_note:
        return adjudication_note
    return str(rater2_note or "").strip()


def build_heldout_v4(
    *,
    master_path: str = DEFAULT_MASTER,
    rater2_path: str = DEFAULT_RATER2,
    adjudication_path: str = DEFAULT_ADJUDICATION,
    benchmark_csv: str = DEFAULT_BENCHMARK_CSV,
    input_csv: str = DEFAULT_INPUT_CSV,
    report_path: str = DEFAULT_REPORT,
    rubric_version: str = "track_a_as_rubric_rewrite_v1",
) -> dict[str, Any]:
    master = load_table(master_path).copy()
    rater2 = load_table(rater2_path).copy()
    adjudication = load_table(adjudication_path).copy()

    for frame, name, required in [
        (master, "master", {"irr_item_id", "sentence_id", "sentence", "rater1_label"}),
        (rater2, "rater2", {"irr_item_id", "rater2_label"}),
        (adjudication, "adjudication", {"irr_item_id", "resolved_label", "resolution_source"}),
    ]:
        missing = sorted(required - set(frame.columns))
        if missing:
            raise ValueError(f"{name} missing required columns: {missing}")

    master["rater1_label"] = master["rater1_label"].map(_clean_label)
    rater2["rater2_label"] = rater2["rater2_label"].map(_clean_label)
    adjudication["resolved_label"] = adjudication["resolved_label"].map(_clean_label)
    if "rater2_note" not in rater2.columns:
        rater2["rater2_note"] = ""
    if "adjudication_note" not in adjudication.columns:
        adjudication["adjudication_note"] = ""

    merged = master.drop(columns=[c for c in ["rater2_label", "rater2_note"] if c in master.columns]).merge(
        rater2[["irr_item_id", "rater2_label", "rater2_note"]],
        on="irr_item_id",
        how="left",
    )
    merged = merged.merge(
        adjudication[
            [
                "irr_item_id",
                "resolved_label",
                "resolution_source",
                "disagreement_pair",
                "transition",
                "adjudication_note",
            ]
        ],
        on="irr_item_id",
        how="left",
    )
    merged["rater2_label"] = merged["rater2_label"].fillna("").map(_clean_label)
    merged["rater2_note"] = merged["rater2_note"].fillna("").astype(str)
    merged["adjudication_note"] = merged["adjudication_note"].fillna("").astype(str)
    merged["resolved_label"] = merged["resolved_label"].fillna("").map(_clean_label)

    unresolved = merged[~merged["resolved_label"].isin(ALLOWED_LABELS)].copy()
    if not unresolved.empty:
        raise ValueError(
            "Adjudication file still contains unresolved rows; cannot build held_out_v4."
        )

    for column in [
        "sample_id",
        "batch_row_id",
        "source_cik",
        "source_year",
        "source_form",
        "source_file",
        "sentence_index",
        "ff12_code",
        "ff12_name",
        "disagreement_pair",
        "transition",
        "resolution_source",
    ]:
        if column not in merged.columns:
            merged[column] = ""
        merged[column] = merged[column].fillna("").astype(str)

    merged["source_section"] = ""
    merged["label"] = merged["resolved_label"]
    merged["review_note"] = merged.apply(
        lambda row: _resolve_note(row.get("rater2_note", ""), row.get("adjudication_note", "")),
        axis=1,
    )
    merged["benchmark_name"] = "held_out_v4"
    merged["benchmark_asset_role"] = "canonical_adjudicated_boundary_benchmark_v4"
    merged["review_status"] = "adjudicated"
    merged["rubric_version"] = str(rubric_version)
    merged["prelabel_eligible"] = True
    merged["skip_reason"] = ""

    benchmark = merged[BENCHMARK_COLUMNS].copy().sort_values("irr_item_id").reset_index(drop=True)

    benchmark_output = Path(benchmark_csv).expanduser().resolve()
    benchmark_output.parent.mkdir(parents=True, exist_ok=True)
    benchmark.to_csv(benchmark_output, index=False)

    input_frame = benchmark.copy()
    input_frame["benchmark_label"] = input_frame["label"]
    input_frame["label"] = ""
    input_frame["assistive_label"] = ""
    input_frame["assistive_confidence"] = ""
    input_frame["assistive_rationale"] = ""
    input_frame["assistive_model"] = ""
    input_frame["assistive_generated_at"] = ""
    input_frame["assistive_prompt_hash"] = ""
    input_output = Path(input_csv).expanduser().resolve()
    input_output.parent.mkdir(parents=True, exist_ok=True)
    input_frame.to_csv(input_output, index=False)

    report = {
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "inputs": {
            "master_path": str(Path(master_path).expanduser().resolve()),
            "rater2_path": str(Path(rater2_path).expanduser().resolve()),
            "adjudication_path": str(Path(adjudication_path).expanduser().resolve()),
        },
        "summary": {
            "status": "built",
            "rows_total": int(len(benchmark)),
            "label_counts": benchmark["label"].value_counts().to_dict(),
            "resolution_source_counts": benchmark["resolution_source"].value_counts().to_dict(),
            "rows_with_review_note": int(benchmark["review_note"].fillna("").astype(str).str.strip().ne("").sum()),
            "benchmark_name": "held_out_v4",
            "rubric_version": str(rubric_version),
        },
        "outputs": {
            "benchmark_csv": str(benchmark_output),
            "input_csv": str(input_output),
        },
    }
    report_output = Path(report_path).expanduser().resolve()
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master-path", default=DEFAULT_MASTER)
    parser.add_argument("--rater2-path", default=DEFAULT_RATER2)
    parser.add_argument("--adjudication-path", default=DEFAULT_ADJUDICATION)
    parser.add_argument("--benchmark-csv", default=DEFAULT_BENCHMARK_CSV)
    parser.add_argument("--input-csv", default=DEFAULT_INPUT_CSV)
    parser.add_argument("--report-path", default=DEFAULT_REPORT)
    parser.add_argument("--rubric-version", default="track_a_as_rubric_rewrite_v1")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_heldout_v4(
        master_path=args.master_path,
        rater2_path=args.rater2_path,
        adjudication_path=args.adjudication_path,
        benchmark_csv=args.benchmark_csv,
        input_csv=args.input_csv,
        report_path=args.report_path,
        rubric_version=args.rubric_version,
    )
    print(
        "[heldout-v4-build] "
        f"status={report['summary']['status']} "
        f"rows_total={report['summary']['rows_total']}"
    )
    print(f"[heldout-v4-build] benchmark -> {report['outputs']['benchmark_csv']}")


if __name__ == "__main__":
    main()
