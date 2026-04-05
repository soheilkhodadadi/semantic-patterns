"""Sample a balanced candidate review package for held_out_sentences_v2."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd

from semantic_ai_washing.classification.model_runtime import (
    build_legacy_two_stage_runtime,
    predict_sentences,
)
from ai_washing_member.labeling.common import load_table, normalize_sentence, write_excel

DEFAULT_YEARS = (2021, 2022, 2023, 2024)
TARGET_PER_LABEL = 60
TARGET_TOTAL = 180
LABELS = ("Actionable", "Speculative", "Irrelevant")
PRELABELERS = ("legacy_two_stage", "heuristic")
REVIEW_COLUMNS = [
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

ANY_AI = re.compile(r"\b(ai|artificial intelligence|machine learning|ml)\b", re.I)
ACTIONABLE_VERBS = re.compile(
    r"\b(deploy(?:ed|ing)?|implement(?:ed|ing)?|use(?:d|s|ing)?|build(?:s|ing|t)?|"
    r"develop(?:s|ed|ing)?|offer(?:s|ed|ing)?|provide(?:s|d|ing)?|operate(?:s|d|ing)?|"
    r"run(?:s|ning)?|launch(?:ed|es|ing)?|integrat(?:e|ed|es|ing)|automate(?:d|s|ing)?)\b",
    re.I,
)
SPECULATIVE_CUES = re.compile(
    r"\b(may|might|could|plan(?:s|ned)? to|planning to|intend(?:s|ed)? to|aim(?:s|ed)? to|"
    r"expect(?:s|ed)? to|will|future|focus(?:ed|es|ing)? on)\b",
    re.I,
)
IRRELEVANT_CUES = re.compile(
    r"\b(laws? and regulations|subject to multiple lawsuits|ai infrastructure|"
    r"graphics processing units|data leakage|unauthorized exposure|reevaluated our data center)\b",
    re.I,
)


def load_sentence_pool(root: str | Path, years: list[int]) -> pd.DataFrame:
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


def load_exclusions(labels_master: str | Path, held_out: str | Path) -> set[str]:
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


def select_candidate_review_rows(eligible: pd.DataFrame) -> pd.DataFrame:
    if eligible.empty:
        raise ValueError("No eligible sentences remain after exclusions.")
    if "candidate_label" not in eligible.columns:
        raise ValueError("Eligible candidate pool must include `candidate_label`.")
    eligible = eligible.copy()
    eligible["source_cik_norm"] = eligible["source_cik"].fillna("").astype(str)

    selected_frames = []
    used_ciks: set[str] = set()
    shortfall: dict[str, int] = {}
    for label in LABELS:
        bucket = eligible[
            (eligible["candidate_label"] == label) & (~eligible["source_cik_norm"].isin(used_ciks))
        ].copy()
        bucket = bucket.sort_values(["source_year", "source_cik_norm", "sentence_id"])
        bucket = bucket.drop_duplicates(subset=["source_cik_norm"], keep="first")
        bucket = bucket.groupby("source_year", group_keys=False).head(15)
        if len(bucket) < TARGET_PER_LABEL:
            remainder = eligible[
                (eligible["candidate_label"] == label)
                & (~eligible["sentence_id"].isin(bucket["sentence_id"]))
                & (~eligible["source_cik_norm"].isin(used_ciks))
            ].copy()
            remainder = remainder.sort_values(["source_year", "source_cik_norm", "sentence_id"])
            remainder = remainder.drop_duplicates(subset=["source_cik_norm"], keep="first")
            if not remainder.empty:
                bucket = pd.concat(
                    [bucket, remainder.head(TARGET_PER_LABEL - len(bucket))], ignore_index=True
                )
        if len(bucket) < TARGET_PER_LABEL:
            relaxed = eligible[
                (eligible["candidate_label"] == label)
                & (~eligible["sentence_id"].isin(bucket["sentence_id"]))
            ].copy()
            relaxed = relaxed.sort_values(["source_year", "source_cik_norm", "sentence_id"])
            if not relaxed.empty:
                bucket = pd.concat(
                    [bucket, relaxed.head(TARGET_PER_LABEL - len(bucket))], ignore_index=True
                )
        bucket = bucket.head(TARGET_PER_LABEL).copy()
        shortfall[label] = TARGET_PER_LABEL - int(len(bucket))
        used_ciks.update(bucket["source_cik_norm"].tolist())
        selected_frames.append(bucket)

    selected = pd.concat(selected_frames, ignore_index=True)
    if len(selected) != TARGET_TOTAL:
        raise ValueError(
            "Unable to build a full 180-row candidate pack; "
            f"selected={len(selected)} shortfall={shortfall}"
        )
    selected = selected.sort_values(
        ["candidate_label", "source_year", "source_cik", "sentence_id"]
    ).reset_index(drop=True)
    selected = selected.drop(columns=["source_cik_norm"], errors="ignore")
    selected["label"] = ""
    selected["review_note"] = ""
    selected["benchmark_asset_role"] = "canonical_current_rubric_evaluation_set_candidate"
    return selected


def build_sampling_report(
    *,
    selected: pd.DataFrame,
    years: list[int],
    output_csv: str | Path,
    output_xlsx: str | Path,
) -> dict:
    return {
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


def write_review_package(
    *,
    selected: pd.DataFrame,
    years: list[int],
    output_csv: str | Path,
    output_xlsx: str | Path,
    output_report: str | Path,
) -> dict:
    output_csv = Path(output_csv)
    output_xlsx = Path(output_xlsx)
    output_report = Path(output_report)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_report.parent.mkdir(parents=True, exist_ok=True)
    selected[REVIEW_COLUMNS].to_csv(output_csv, index=False)
    write_excel(output_xlsx, selected[REVIEW_COLUMNS], sheet_name="held_out_v2_review")
    report = build_sampling_report(
        selected=selected,
        years=years,
        output_csv=output_csv,
        output_xlsx=output_xlsx,
    )
    output_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def heuristic_candidate_label(text: str) -> str:
    sentence = str(text)
    has_ai = bool(ANY_AI.search(sentence))
    actionable = bool(ACTIONABLE_VERBS.search(sentence))
    speculative = bool(SPECULATIVE_CUES.search(sentence))
    irrelevant = bool(IRRELEVANT_CUES.search(sentence))

    if speculative and not actionable:
        return "Speculative"
    if irrelevant and not speculative:
        return "Irrelevant"
    if has_ai and actionable:
        return "Actionable"
    if speculative:
        return "Speculative"
    if irrelevant:
        return "Irrelevant"
    return "Irrelevant"


def predict_candidate_labels(
    sentences: list[str], *, prelabeler: str = "legacy_two_stage"
) -> list[str]:
    mode = str(prelabeler).strip().lower()
    if mode == "heuristic":
        return [heuristic_candidate_label(sentence) for sentence in sentences]
    if mode != "legacy_two_stage":
        raise ValueError(f"Unsupported prelabeler: {prelabeler}")

    legacy = build_legacy_two_stage_runtime()
    predicted, _scores = predict_sentences(sentences, legacy)
    return predicted


def run_sampling(args: argparse.Namespace) -> dict:
    years = [int(value) for value in args.years]
    pool = load_sentence_pool(args.input_root, years)
    include_forms = [
        str(value).strip().upper()
        for value in str(getattr(args, "include_forms", "") or "").split(",")
        if str(value).strip()
    ]
    if include_forms:
        pool = pool[
            pool["source_form"].fillna("").astype(str).str.upper().isin(include_forms)
        ].copy()
        if pool.empty:
            raise ValueError(f"No sentence rows remain after form filter: {include_forms}")
    exclusions = load_exclusions(args.labels_master, args.historical_held_out)
    eligible = pool[~pool["sentence_norm"].isin(exclusions)].copy()
    eligible["candidate_label"] = predict_candidate_labels(
        eligible["sentence"].astype(str).tolist(),
        prelabeler=getattr(args, "prelabeler", "legacy_two_stage"),
    )
    eligible = eligible.sort_values(["source_year", "source_cik", "sentence_id"]).reset_index(
        drop=True
    )
    selected = select_candidate_review_rows(eligible)
    return write_review_package(
        selected=selected,
        years=years,
        output_csv=args.output_csv,
        output_xlsx=args.output_xlsx,
        output_report=args.output_report,
    )


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
    parser.add_argument(
        "--include-forms",
        default="",
        help="Optional comma-separated form filter, e.g. `10-K`.",
    )
    parser.add_argument("--prelabeler", choices=list(PRELABELERS), default="legacy_two_stage")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_sampling(args)
    print(f"[heldout-v2] status={report['status']} rows={report['summary']['rows_selected']}")
    print(f"[heldout-v2] review sheet -> {args.output_xlsx}")


if __name__ == "__main__":
    main()
