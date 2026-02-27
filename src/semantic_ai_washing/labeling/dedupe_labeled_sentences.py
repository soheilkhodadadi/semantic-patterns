"""Deduplicate and merge labeled datasets for Phase 1."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd

from semantic_ai_washing.labeling.common import (
    ALLOWED_LABELS,
    compute_sample_id,
    compute_sentence_id,
    ensure_allowed_label,
    normalize_sentence,
    parse_uncertain_flag,
    safe_int,
    token_count,
    length_bin_from_tokens,
)

OUTPUT_COLUMNS = [
    "sample_id",
    "sentence_id",
    "sentence",
    "sentence_norm",
    "label",
    "is_uncertain",
    "uncertainty_note",
    "source_file",
    "source_year",
    "source_form",
    "source_cik",
    "sentence_index",
    "sic",
    "sic2",
    "ff12_code",
    "ff12_name",
    "token_count",
    "length_bin",
    "edge_case_flag",
]


@dataclass
class DedupeStats:
    rows_base: int = 0
    rows_new: int = 0
    rows_combined: int = 0
    rows_invalid_label_removed: int = 0
    rows_autofilled_from_suggestion: int = 0
    rows_leakage_removed: int = 0
    rows_exact_deduped: int = 0
    rows_near_deduped: int = 0
    rows_conflicted: int = 0
    rows_uncertain_split: int = 0
    rows_final_preqa: int = 0


def _load_heldout_norms(path: str) -> set[str]:
    heldout: set[str] = set()
    with open(path, newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            norm = normalize_sentence(row.get("sentence", ""))
            if norm:
                heldout.add(norm)
    return heldout


def _ensure_columns(df: pd.DataFrame, is_base: bool) -> pd.DataFrame:
    out = df.copy()
    required = {"sentence"}
    missing = required - set(out.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    for col in OUTPUT_COLUMNS:
        if col not in out.columns:
            out[col] = ""

    if "label_suggested" not in out.columns:
        out["label_suggested"] = ""
    if "source_dataset" not in out.columns:
        out["source_dataset"] = "base" if is_base else "new"
    return out


def _prepare_rows(df: pd.DataFrame, is_base: bool, stats: DedupeStats) -> pd.DataFrame:
    out = _ensure_columns(df, is_base=is_base)
    out["sentence"] = out["sentence"].astype(str)
    out["sentence_norm"] = out["sentence_norm"].astype(str)
    out["sentence_norm"] = out["sentence_norm"].map(normalize_sentence)
    out["label_suggested"] = out["label_suggested"].astype(str)
    out["label"] = out["label"].astype(str)
    out["is_uncertain"] = out["is_uncertain"].map(parse_uncertain_flag)
    out["uncertainty_note"] = out["uncertainty_note"].fillna("").astype(str)
    out["source_file"] = out["source_file"].fillna("").astype(str)
    out["source_year"] = out["source_year"].fillna("").astype(str)
    out["source_form"] = out["source_form"].fillna("").astype(str)
    out["source_cik"] = out["source_cik"].fillna("").astype(str)
    out["sentence_index"] = out["sentence_index"].map(lambda v: safe_int(v, default=0))
    out["edge_case_flag"] = out["edge_case_flag"].map(parse_uncertain_flag)

    autofilled = 0
    labels = []
    for _, row in out.iterrows():
        label = ensure_allowed_label(row["label"])
        if label is None and row["is_uncertain"] == 0:
            suggested = ensure_allowed_label(row["label_suggested"])
            if suggested is not None:
                label = suggested
                autofilled += 1
        labels.append(label or "")
    out["label"] = labels
    stats.rows_autofilled_from_suggestion += autofilled

    out["token_count"] = out["token_count"].map(lambda v: safe_int(v, default=0))
    out["token_count"] = out["token_count"].where(
        out["token_count"] > 0, out["sentence"].map(token_count)
    )
    out["length_bin"] = out["length_bin"].where(
        out["length_bin"].astype(str).isin(["short", "medium", "long"]),
        out["token_count"].map(length_bin_from_tokens),
    )

    missing_ids = out["sample_id"].astype(str).str.strip() == ""
    out.loc[missing_ids, "sample_id"] = out[missing_ids].apply(
        lambda r: compute_sample_id(
            r["source_file"] or ("base_labeled" if is_base else "new"),
            r["sentence_index"],
            r["sentence_norm"],
        ),
        axis=1,
    )
    missing_sentence_id = out["sentence_id"].astype(str).str.strip() == ""
    out.loc[missing_sentence_id, "sentence_id"] = out.loc[
        missing_sentence_id, "sentence_norm"
    ].map(compute_sentence_id)

    out = out[out["sentence_norm"] != ""].copy()
    invalid_mask = (~out["label"].isin(ALLOWED_LABELS)) & (out["is_uncertain"] == 0)
    stats.rows_invalid_label_removed += int(invalid_mask.sum())
    out = out[~invalid_mask].copy()
    return out


def _near_dedupe(df: pd.DataFrame, threshold: float) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    rows = df.reset_index(drop=True).copy()
    removed = set()
    conflicted = set()
    conflicts: list[dict] = []
    near_deduped = 0

    for i in range(len(rows)):
        if i in removed:
            continue
        sentence_i = rows.at[i, "sentence_norm"]
        label_i = rows.at[i, "label"]
        sample_i = rows.at[i, "sample_id"]
        for j in range(i + 1, len(rows)):
            if j in removed:
                continue
            sentence_j = rows.at[j, "sentence_norm"]
            ratio = SequenceMatcher(None, sentence_i, sentence_j).ratio()
            if ratio < threshold:
                continue
            label_j = rows.at[j, "label"]
            sample_j = rows.at[j, "sample_id"]
            if label_i == label_j:
                removed.add(j)
                near_deduped += 1
            else:
                conflicted.add(i)
                conflicted.add(j)
                conflicts.append(
                    {
                        "sample_id_a": sample_i,
                        "sample_id_b": sample_j,
                        "sentence_a": rows.at[i, "sentence"],
                        "sentence_b": rows.at[j, "sentence"],
                        "label_a": label_i,
                        "label_b": label_j,
                        "similarity": round(float(ratio), 6),
                        "reason": "near_duplicate_conflicting_labels",
                    }
                )

    conflicted |= {idx for idx in removed if idx in conflicted}
    drop_idx = removed | conflicted
    cleaned = rows.drop(index=list(drop_idx)).copy().reset_index(drop=True)
    conflict_df = pd.DataFrame(conflicts)
    return cleaned, conflict_df, near_deduped


def run_dedupe(args: argparse.Namespace) -> dict:
    stats = DedupeStats()
    heldout_norms = _load_heldout_norms(args.held_out)

    base_df = pd.read_csv(args.base)
    new_df = pd.read_csv(args.new)
    stats.rows_base = int(len(base_df))
    stats.rows_new = int(len(new_df))

    base_df = _prepare_rows(base_df, is_base=True, stats=stats)
    new_df = _prepare_rows(new_df, is_base=False, stats=stats)
    combined = pd.concat([base_df, new_df], ignore_index=True)
    stats.rows_combined = int(len(combined))

    leakage_mask = combined["sentence_norm"].isin(heldout_norms)
    stats.rows_leakage_removed = int(leakage_mask.sum())
    combined = combined[~leakage_mask].copy()

    before_exact = len(combined)
    combined = combined.sort_values(
        by=["source_dataset", "source_file", "sentence_index", "sample_id"]
    ).drop_duplicates(subset=["sentence_norm"], keep="first")
    stats.rows_exact_deduped = int(before_exact - len(combined))
    combined = combined.reset_index(drop=True)

    cleaned, conflicts_df, near_deduped = _near_dedupe(combined, threshold=args.near_threshold)
    stats.rows_near_deduped = int(near_deduped)
    stats.rows_conflicted = int(
        len(set(conflicts_df.get("sample_id_a", [])) | set(conflicts_df.get("sample_id_b", [])))
    )

    uncertain_df = cleaned[cleaned["is_uncertain"].map(parse_uncertain_flag) == 1].copy()
    final_df = cleaned[cleaned["is_uncertain"].map(parse_uncertain_flag) == 0].copy()
    stats.rows_uncertain_split = int(len(uncertain_df))
    stats.rows_final_preqa = int(len(final_df))

    for frame in (uncertain_df, final_df):
        frame["is_uncertain"] = frame["is_uncertain"].map(parse_uncertain_flag)

    output_path = Path(args.output)
    uncertain_path = Path(args.uncertain_output)
    conflicts_path = Path(args.conflicts_output)
    report_path = Path(args.report)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    uncertain_path.parent.mkdir(parents=True, exist_ok=True)
    conflicts_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    final_df[OUTPUT_COLUMNS].to_csv(output_path, index=False)
    uncertain_df[OUTPUT_COLUMNS].to_csv(uncertain_path, index=False)
    if conflicts_df.empty:
        pd.DataFrame(
            columns=[
                "sample_id_a",
                "sample_id_b",
                "sentence_a",
                "sentence_b",
                "label_a",
                "label_b",
                "similarity",
                "reason",
            ]
        ).to_csv(conflicts_path, index=False)
    else:
        conflicts_df.to_csv(conflicts_path, index=False)

    report = {
        "inputs": {"base": args.base, "new": args.new, "held_out": args.held_out},
        "parameters": {"near_threshold": args.near_threshold},
        "stats": stats.__dict__,
        "final_class_counts": Counter(final_df["label"].tolist()),
        "artifacts": {
            "expanded_labeled_sentences_preqa": str(output_path),
            "uncertain_rows": str(uncertain_path),
            "label_conflicts": str(conflicts_path),
        },
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge + dedupe expanded labeled dataset.")
    parser.add_argument("--base", required=True)
    parser.add_argument("--new", required=True)
    parser.add_argument("--held-out", required=True)
    parser.add_argument("--near-threshold", type=float, default=0.95)
    parser.add_argument("--output", required=True)
    parser.add_argument("--uncertain-output", required=True)
    parser.add_argument("--conflicts-output", required=True)
    parser.add_argument("--report", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_dedupe(args)
    stats = report["stats"]
    print(
        "[phase1] dedupe:"
        f" combined={stats['rows_combined']} "
        f" preqa={stats['rows_final_preqa']} "
        f" uncertain={stats['rows_uncertain_split']} "
        f" conflicts={stats['rows_conflicted']}"
    )
    print(f"[phase1] report -> {args.report}")


if __name__ == "__main__":
    main()
