"""Sample a balanced candidate review package for held_out_sentences_v2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from semantic_ai_washing.classification.model_runtime import (
    build_legacy_two_stage_runtime,
    predict_sentences,
)
from semantic_ai_washing.labeling.common import load_table, normalize_sentence, write_excel

DEFAULT_YEARS = (2021, 2022, 2023, 2024)
TARGET_PER_LABEL = 60
TARGET_TOTAL = 180
LABELS = ("Actionable", "Speculative", "Irrelevant")


def _load_sentence_pool(root: str | Path, years: list[int]) -> pd.DataFrame:
    frames = []
    for year in years:
        path = Path(root) / f"year={year}" / "ai_sentences.parquet"
        if not path.exists():
            raise FileNotFoundError(f"Sentence table missing for year={year}: {path}")
        frame = load_table(path)
        required = {
            "sentence_id",
            "sentence",
            "source_cik",
            "source_year",
            "source_form",
            "source_file",
            "sentence_index",
        }
        missing = sorted(required - set(frame.columns))
        if missing:
            raise ValueError(f"Sentence table for year={year} missing columns: {missing}")
        frames.append(frame.copy())
    pool = pd.concat(frames, ignore_index=True)
    pool["sentence_norm"] = pool["sentence"].fillna("").astype(str).map(normalize_sentence)
    return pool


def _load_exclusions(labels_master: str | Path, held_out: str | Path) -> set[str]:
    labels = pd.read_parquet(labels_master)
    if "sentence" not in labels.columns:
        raise ValueError("Labels master must include `sentence`.")
    held = pd.read_csv(held_out)
    if "sentence" not in held.columns:
        raise ValueError("Historical held-out must include `sentence`.")
    norms = set(labels["sentence"].fillna("").astype(str).map(normalize_sentence))
    norms.update(held["sentence"].fillna("").astype(str).map(normalize_sentence))
    norms.discard("")
    return norms


def run_sampling(args: argparse.Namespace) -> dict:
    years = [int(value) for value in args.years]
    pool = _load_sentence_pool(args.input_root, years)
    exclusions = _load_exclusions(args.labels_master, args.historical_held_out)
    eligible = pool[~pool["sentence_norm"].isin(exclusions)].copy()
    if eligible.empty:
        raise ValueError("No eligible sentences remain after exclusions.")

    legacy = build_legacy_two_stage_runtime()
    predicted, _scores = predict_sentences(eligible["sentence"].astype(str).tolist(), legacy)
    eligible["candidate_label"] = predicted
    eligible = eligible.sort_values(["source_year", "source_cik", "sentence_id"]).reset_index(
        drop=True
    )

    selected_frames = []
    used_ciks: set[str] = set()
    shortfall: dict[str, int] = {}
    for label in LABELS:
        bucket = eligible[
            (eligible["candidate_label"] == label) & (~eligible["source_cik"].isin(used_ciks))
        ].copy()
        bucket = bucket.groupby("source_year", group_keys=False).head(15)
        if len(bucket) < TARGET_PER_LABEL:
            remainder = eligible[
                (eligible["candidate_label"] == label)
                & (~eligible["sentence_id"].isin(bucket["sentence_id"]))
                & (~eligible["source_cik"].isin(used_ciks))
            ].copy()
            if not remainder.empty:
                bucket = pd.concat(
                    [bucket, remainder.head(TARGET_PER_LABEL - len(bucket))], ignore_index=True
                )
        bucket = bucket.head(TARGET_PER_LABEL).copy()
        shortfall[label] = TARGET_PER_LABEL - int(len(bucket))
        used_ciks.update(bucket["source_cik"].astype(str).tolist())
        selected_frames.append(bucket)

    selected = pd.concat(selected_frames, ignore_index=True)
    if len(selected) != TARGET_TOTAL:
        raise ValueError(
            f"Unable to build a full 180-row candidate pack; selected={len(selected)} shortfall={shortfall}"
        )
    selected = selected.sort_values(
        ["candidate_label", "source_year", "source_cik", "sentence_id"]
    ).reset_index(drop=True)
    selected["label"] = ""
    selected["review_note"] = ""
    selected["benchmark_asset_role"] = "canonical_current_rubric_evaluation_set_candidate"

    review_columns = [
        "sentence_id",
        "sentence",
        "source_cik",
        "source_year",
        "source_form",
        "source_file",
        "sentence_index",
        "candidate_label",
        "label",
        "review_note",
        "benchmark_asset_role",
    ]
    output_csv = Path(args.output_csv)
    output_xlsx = Path(args.output_xlsx)
    output_report = Path(args.output_report)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_report.parent.mkdir(parents=True, exist_ok=True)
    selected[review_columns].to_csv(output_csv, index=False)
    write_excel(output_xlsx, selected[review_columns], sheet_name="held_out_v2_review")

    report = {
        "status": "pending_review",
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "summary": {
            "status": "pending_review",
            "rows_selected": int(len(selected)),
            "target_total": TARGET_TOTAL,
            "candidate_label_counts": selected["candidate_label"].value_counts().to_dict(),
            "years": years,
            "unique_firms": int(selected["source_cik"].astype(str).nunique()),
        },
        "outputs": {
            "candidate_csv": str(output_csv),
            "review_xlsx": str(output_xlsx),
        },
    }
    output_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", default="data/processed/sentences")
    parser.add_argument("--years", nargs="+", default=[str(year) for year in DEFAULT_YEARS])
    parser.add_argument("--labels-master", default="data/labels/v1/labels_master.parquet")
    parser.add_argument("--historical-held-out", default="data/validation/held_out_sentences.csv")
    parser.add_argument(
        "--output-csv", default="data/validation/held_out_sentences_v2_review_sheet.csv"
    )
    parser.add_argument(
        "--output-xlsx", default="data/validation/held_out_sentences_v2_review_sheet.xlsx"
    )
    parser.add_argument(
        "--output-report", default="reports/validation/held_out_v2_sampling_report.json"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_sampling(args)
    print(f"[heldout-v2] status={report['status']} rows={report['summary']['rows_selected']}")
    print(f"[heldout-v2] review sheet -> {args.output_xlsx}")


if __name__ == "__main__":
    main()
