"""Prepare a stratified IRR subset and blinded rater templates."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
from collections import Counter
from pathlib import Path

import pandas as pd

from semantic_ai_washing.labeling.common import ALLOWED_LABELS, ensure_allowed_label

REQUIRED_COLUMNS = [
    "sample_id",
    "sentence_id",
    "sentence",
    "label",
    "source_year",
    "ff12_code",
]

MASTER_COLUMNS = [
    "irr_item_id",
    "sample_id",
    "sentence_id",
    "sentence",
    "source_year",
    "source_form",
    "source_cik",
    "source_file",
    "sentence_index",
    "ff12_code",
    "ff12_name",
    "rater1_label",
    "rater2_label",
    "rater2_note",
]


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _sha256_file(path: str) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _validate_input(df: pd.DataFrame) -> None:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for IRR subset prep: {missing}")


def _stratified_pick(
    rows: pd.DataFrame,
    n: int,
    seed: int,
    selected_strata: Counter,
) -> list[int]:
    if n <= 0 or rows.empty:
        return []

    local = rows.copy()
    rng = random.Random(seed)
    local["rand"] = [rng.random() for _ in range(len(local))]
    stratum_size = local["stratum_key"].value_counts().to_dict()
    local["stratum_size"] = local["stratum_key"].map(stratum_size)
    local["stratum_selected"] = local["stratum_key"].map(lambda s: selected_strata.get(s, 0))

    local = local.sort_values(
        by=["stratum_selected", "stratum_size", "rand", "sample_id"],
        ascending=[True, True, True, True],
    )
    return local.head(n).index.tolist()


def _make_irr_item_id(sample_id: str, sentence_id: str) -> str:
    payload = f"{sample_id}|{sentence_id}|irr"
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


def _build_blinded(df: pd.DataFrame, blind_mode: str) -> pd.DataFrame:
    base_cols = ["irr_item_id", "sentence"]
    if blind_mode == "text_only":
        cols = base_cols
    elif blind_mode == "partial":
        cols = base_cols + ["source_year", "source_form"]
    elif blind_mode == "none":
        cols = base_cols + [
            "source_year",
            "source_form",
            "source_cik",
            "source_file",
            "sentence_index",
            "ff12_code",
            "ff12_name",
        ]
    else:
        raise ValueError(f"Unsupported blind mode: {blind_mode}")

    blinded = df[cols].copy()
    blinded["rater2_label"] = ""
    blinded["rater2_note"] = ""
    return blinded


def run_prepare(args: argparse.Namespace) -> dict:
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    report_dir = Path(args.report_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)
    _validate_input(df)

    data = df.copy()
    data["label"] = data["label"].map(ensure_allowed_label)
    data = data[data["label"].isin(ALLOWED_LABELS)].copy()
    if data.empty:
        raise ValueError("No valid labeled rows available for IRR subset.")

    data["source_year"] = data["source_year"].fillna("unknown").astype(str)
    data["source_form"] = data.get("source_form", "").fillna("").astype(str)
    data["source_cik"] = data.get("source_cik", "").fillna("").astype(str)
    data["source_file"] = data.get("source_file", "").fillna("").astype(str)
    data["sentence_index"] = data.get("sentence_index", "").fillna("").astype(str)
    data["ff12_code"] = data["ff12_code"].fillna("unknown").astype(str)
    data["ff12_name"] = data.get("ff12_name", "").fillna("").astype(str)
    data["sample_id"] = data["sample_id"].fillna("").astype(str)
    data["sentence_id"] = data["sentence_id"].fillna("").astype(str)
    data["sentence"] = data["sentence"].fillna("").astype(str)
    data["stratum_key"] = data["source_year"] + "|" + data["ff12_code"]

    n_total = len(data)
    target_from_fraction = max(1, int(round(n_total * float(args.subset_fraction))))
    class_counts = data["label"].value_counts().to_dict()
    min_required = sum(
        min(int(args.min_per_class), int(class_counts.get(lbl, 0))) for lbl in ALLOWED_LABELS
    )
    target_n = min(n_total, max(target_from_fraction, min_required))

    selected_indices: set[int] = set()
    selected_strata: Counter = Counter()
    selected_labels: Counter = Counter()

    for label_idx, label in enumerate(ALLOWED_LABELS, start=1):
        rows = data[data["label"] == label]
        quota = min(int(args.min_per_class), len(rows))
        pick = _stratified_pick(
            rows, quota, seed=int(args.seed) + label_idx, selected_strata=selected_strata
        )
        for idx in pick:
            selected_indices.add(idx)
            selected_strata[data.at[idx, "stratum_key"]] += 1
            selected_labels[data.at[idx, "label"]] += 1

    desired_by_class = {
        label: int(round(target_n * (class_counts.get(label, 0) / n_total)))
        for label in ALLOWED_LABELS
    }
    remainder = target_n - sum(desired_by_class.values())
    label_order = sorted(ALLOWED_LABELS, key=lambda lab: class_counts.get(lab, 0), reverse=True)
    for idx in range(max(0, remainder)):
        desired_by_class[label_order[idx % len(label_order)]] += 1

    remaining = data.loc[~data.index.isin(selected_indices)].copy()
    rng = random.Random(int(args.seed) + 1000)
    remaining["rand"] = [rng.random() for _ in range(len(remaining))]
    stratum_totals = data["stratum_key"].value_counts().to_dict()

    while len(selected_indices) < target_n and not remaining.empty:

        def _priority(row: pd.Series) -> tuple:
            label = row["label"]
            deficit = max(0, desired_by_class.get(label, 0) - selected_labels.get(label, 0))
            stratum = row["stratum_key"]
            return (
                0 if deficit > 0 else 1,
                -deficit,
                selected_strata.get(stratum, 0),
                stratum_totals.get(stratum, 0),
                row["rand"],
                row["sample_id"],
            )

        next_idx = min(remaining.index.tolist(), key=lambda i: _priority(remaining.loc[i]))
        selected_indices.add(next_idx)
        selected_strata[data.at[next_idx, "stratum_key"]] += 1
        selected_labels[data.at[next_idx, "label"]] += 1
        remaining = remaining.drop(index=next_idx)

    subset = data.loc[sorted(selected_indices)].copy()
    subset = subset.sort_values(
        by=["source_year", "ff12_code", "sample_id", "sentence_index"], ascending=True
    ).reset_index(drop=True)

    subset["irr_item_id"] = subset.apply(
        lambda row: _make_irr_item_id(str(row["sample_id"]), str(row["sentence_id"])),
        axis=1,
    )
    subset["rater1_label"] = subset["label"]
    subset["rater2_label"] = ""
    subset["rater2_note"] = ""

    master_path = output_dir / "irr_subset_master.csv"
    master_df = subset[MASTER_COLUMNS].copy()
    master_df.to_csv(master_path, index=False)

    blinded_path = output_dir / "irr_subset_rater2_blinded.csv"
    blinded_df = _build_blinded(master_df, args.blind_mode)
    blinded_df.to_csv(blinded_path, index=False)

    report = {
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "git_commit": _git_commit(),
        "inputs": {
            "input": str(input_path),
            "input_sha256": _sha256_file(str(input_path)),
        },
        "parameters": {
            "subset_fraction": float(args.subset_fraction),
            "min_per_class": int(args.min_per_class),
            "seed": int(args.seed),
            "blind_mode": str(args.blind_mode),
        },
        "summary": {
            "rows_input": int(len(data)),
            "rows_target": int(target_n),
            "rows_selected": int(len(subset)),
            "selected_class_counts": subset["label"].value_counts().to_dict(),
            "selected_year_counts": subset["source_year"].value_counts().to_dict(),
            "selected_ff12_counts": subset["ff12_code"].value_counts().to_dict(),
        },
        "artifacts": {
            "master": str(master_path),
            "rater2_blinded": str(blinded_path),
        },
    }

    report_path = report_dir / "irr_subset_sampling_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare stratified IRR subset and rater templates."
    )
    parser.add_argument(
        "--input",
        default="data/labels/iteration1/recovery/expanded_labeled_sentences_preqa.csv",
    )
    parser.add_argument("--output-dir", default="data/labels/iteration1/irr")
    parser.add_argument("--report-dir", default="reports/iteration1/phase2_irr")
    parser.add_argument("--subset-fraction", type=float, default=0.30)
    parser.add_argument("--min-per-class", type=int, default=10)
    parser.add_argument("--seed", type=int, default=20260303)
    parser.add_argument(
        "--blind-mode",
        choices=("text_only", "partial", "none"),
        default="text_only",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_prepare(args)
    print(
        "[irr] subset rows="
        f"{report['summary']['rows_selected']}/{report['summary']['rows_input']} "
        f"blind_mode={report['parameters']['blind_mode']}"
    )
    print(f"[irr] report -> {Path(args.report_dir) / 'irr_subset_sampling_report.json'}")


if __name__ == "__main__":
    main()
