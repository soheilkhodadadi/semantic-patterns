"""Publish a truthful disagreement diagnostic for finalized IRR artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd

from ai_washing_member.labeling.common import ALLOWED_LABELS, ensure_allowed_label, load_table

SHORT = {"Actionable": "A", "Speculative": "S", "Irrelevant": "I"}


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _sha256_if_exists(path: str | Path) -> str:
    resolved = Path(path)
    if not resolved.exists():
        return ""
    hasher = hashlib.sha256()
    with open(resolved, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _load_json(path: str | Path) -> dict[str, Any]:
    resolved = Path(path)
    if not resolved.exists():
        return {}
    return json.loads(resolved.read_text(encoding="utf-8"))


def _cohen_kappa(confusion: pd.DataFrame) -> float | None:
    n = confusion.values.sum()
    if n == 0:
        return None
    po = float(confusion.values.diagonal().sum()) / float(n)
    row_marginals = confusion.sum(axis=1).values.astype(float)
    col_marginals = confusion.sum(axis=0).values.astype(float)
    pe = float((row_marginals * col_marginals).sum()) / float(n * n)
    if math.isclose(1.0 - pe, 0.0):
        return 1.0 if math.isclose(po, 1.0) else 0.0
    return float((po - pe) / (1.0 - pe))


def _agreement_rate(left: pd.Series, right: pd.Series) -> float | None:
    if len(left) == 0:
        return None
    return float((left == right).mean())


def _load_master(path: str | Path) -> pd.DataFrame:
    frame = load_table(path)
    if "irr_item_id" not in frame.columns:
        raise ValueError("IRR master file must include `irr_item_id`.")
    if "rater1_label" not in frame.columns and "label" in frame.columns:
        frame["rater1_label"] = frame["label"]
    if "rater1_label" not in frame.columns:
        raise ValueError("IRR master file must include `rater1_label` or `label`.")
    if "sample_id" not in frame.columns:
        frame["sample_id"] = frame.get("batch_row_id", frame["irr_item_id"])
    for column in [
        "sample_id",
        "sentence",
        "source_cik",
        "source_year",
        "ff12_code",
        "ff12_name",
        "batch_row_id",
        "sentence_id",
    ]:
        if column not in frame.columns:
            frame[column] = ""
        frame[column] = frame[column].fillna("").astype(str)
    frame["rater1_label"] = frame["rater1_label"].map(ensure_allowed_label)
    return frame[frame["rater1_label"].isin(ALLOWED_LABELS)].copy()


def _load_rater2(path: str | Path) -> pd.DataFrame:
    frame = load_table(path)
    if "irr_item_id" not in frame.columns or "rater2_label" not in frame.columns:
        raise ValueError("Completed rater2 handoff must include `irr_item_id` and `rater2_label`.")
    keep = frame[["irr_item_id", "rater2_label"]].copy()
    keep["rater2_label"] = keep["rater2_label"].map(ensure_allowed_label)
    return keep


def _load_adjudication(path: str | Path) -> pd.DataFrame:
    frame = load_table(path)
    if "irr_item_id" not in frame.columns or "resolved_label" not in frame.columns:
        raise ValueError("Adjudication artifact must include `irr_item_id` and `resolved_label`.")
    for column in ["disagreement_pair", "transition", "resolution_source"]:
        if column not in frame.columns:
            frame[column] = ""
    keep = frame[
        ["irr_item_id", "resolved_label", "disagreement_pair", "transition", "resolution_source"]
    ].copy()
    keep["resolved_label"] = keep["resolved_label"].map(ensure_allowed_label)
    keep["disagreement_pair"] = keep["disagreement_pair"].fillna("").astype(str)
    keep["transition"] = keep["transition"].fillna("").astype(str)
    keep["resolution_source"] = keep["resolution_source"].fillna("").astype(str)
    return keep


def _binary_relevance(label: str) -> str:
    return "Irrelevant" if label == "Irrelevant" else "Non-Irrelevant"


def _binary_confusion(left: pd.Series, right: pd.Series) -> pd.DataFrame:
    frame = pd.crosstab(left, right, dropna=False)
    for value in ["Irrelevant", "Non-Irrelevant"]:
        if value not in frame.index:
            frame.loc[value, :] = 0
        if value not in frame.columns:
            frame.loc[:, value] = 0
    return frame.loc[["Irrelevant", "Non-Irrelevant"], ["Irrelevant", "Non-Irrelevant"]]


def _as_confusion(left: pd.Series, right: pd.Series) -> pd.DataFrame:
    frame = pd.crosstab(left, right, dropna=False)
    for value in ["Actionable", "Speculative"]:
        if value not in frame.index:
            frame.loc[value, :] = 0
        if value not in frame.columns:
            frame.loc[:, value] = 0
    return frame.loc[["Actionable", "Speculative"], ["Actionable", "Speculative"]]


def run_diagnostic(args: argparse.Namespace) -> dict[str, Any]:
    output_report = Path(args.output_report)
    output_rows = Path(args.output_rows)
    output_report.parent.mkdir(parents=True, exist_ok=True)
    output_rows.parent.mkdir(parents=True, exist_ok=True)

    master = _load_master(args.master)
    rater2 = _load_rater2(args.rater2)
    adjudication = _load_adjudication(args.adjudication)
    irr_report = _load_json(args.irr_report)

    merged = master.drop(columns=[col for col in ["rater2_label"] if col in master.columns]).merge(
        rater2, on="irr_item_id", how="left"
    )
    merged = merged.merge(adjudication, on="irr_item_id", how="left")
    merged["rater2_label"] = merged["rater2_label"].fillna("").map(ensure_allowed_label)
    merged["resolved_label"] = merged["resolved_label"].fillna("").map(ensure_allowed_label)
    merged["disagreement_pair"] = merged["disagreement_pair"].fillna("").astype(str)
    merged["transition"] = merged["transition"].fillna("").astype(str)
    merged["resolution_source"] = merged["resolution_source"].fillna("").astype(str)

    scored = merged[
        merged["rater1_label"].isin(ALLOWED_LABELS) & merged["rater2_label"].isin(ALLOWED_LABELS)
    ].copy()
    disagreements = scored[scored["rater1_label"] != scored["rater2_label"]].copy()
    resolved = merged[merged["resolved_label"].isin(ALLOWED_LABELS)].copy()
    unresolved_disagreements = int(
        (
            (merged["rater1_label"].isin(ALLOWED_LABELS))
            & (merged["rater2_label"].isin(ALLOWED_LABELS))
            & (merged["rater1_label"] != merged["rater2_label"])
            & (~merged["resolved_label"].isin(ALLOWED_LABELS))
        ).sum()
    )

    binary_left = scored["rater1_label"].map(_binary_relevance)
    binary_right = scored["rater2_label"].map(_binary_relevance)
    binary_kappa = _cohen_kappa(_binary_confusion(binary_left, binary_right))

    as_subset = scored[
        scored["rater1_label"].isin(["Actionable", "Speculative"])
        & scored["rater2_label"].isin(["Actionable", "Speculative"])
    ].copy()
    as_kappa = _cohen_kappa(_as_confusion(as_subset["rater1_label"], as_subset["rater2_label"]))

    disagreement_rows = disagreements[
        [
            "irr_item_id",
            "sample_id",
            "sentence",
            "source_cik",
            "source_year",
            "ff12_code",
            "ff12_name",
            "rater1_label",
            "rater2_label",
            "resolved_label",
            "transition",
        ]
    ].copy()
    disagreement_rows.to_csv(output_rows, index=False)

    transition_counts = {
        key: int(value)
        for key, value in disagreements["transition"].fillna("").astype(str).value_counts().items()
        if key
    }
    transition_counts = dict(sorted(transition_counts.items()))
    class_counts = {
        key: int(value)
        for key, value in disagreements["rater1_label"].astype(str).value_counts().items()
    }
    ff12_counts = {
        key: int(value)
        for key, value in disagreements["ff12_code"].fillna("").astype(str).value_counts().items()
        if key
    }
    year_counts = {
        key: int(value)
        for key, value in disagreements["source_year"]
        .fillna("")
        .astype(str)
        .value_counts()
        .items()
        if key
    }

    summary = {
        "headline_irr_status": irr_report.get("summary", {}).get("status", ""),
        "headline_three_class_kappa": irr_report.get("summary", {}).get("kappa"),
        "reviewed_items": int(len(scored)),
        "rows_disagreement": int(len(disagreements)),
        "unresolved_disagreements": unresolved_disagreements,
        "binary_relevance_kappa": binary_kappa,
        "binary_relevance_reviewed_items": int(len(scored)),
        "actionable_speculative_conditional_kappa": as_kappa,
        "actionable_speculative_conditional_items": int(len(as_subset)),
        "rater1_vs_final_agreement": _agreement_rate(
            resolved["rater1_label"], resolved["resolved_label"]
        ),
        "rater2_vs_final_agreement": _agreement_rate(
            resolved["rater2_label"], resolved["resolved_label"]
        ),
        "transition_counts": transition_counts,
        "disagreement_counts_by_rater1_class": class_counts,
        "disagreement_counts_by_ff12_code": ff12_counts,
        "disagreement_counts_by_year": year_counts,
        "adjudicator_based_metrics_are_not_irr": True,
    }
    report = {
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "git_commit": _git_commit(),
        "inputs": {
            "master": args.master,
            "rater2": args.rater2,
            "adjudication": args.adjudication,
            "irr_report": args.irr_report,
            "master_sha256": _sha256_if_exists(args.master),
            "rater2_sha256": _sha256_if_exists(args.rater2),
            "adjudication_sha256": _sha256_if_exists(args.adjudication),
            "irr_report_sha256": _sha256_if_exists(args.irr_report),
        },
        "summary": summary,
        "artifacts": {
            "disagreement_rows": str(output_rows),
        },
    }
    output_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master", default="data/labels/v1/irr_subset_master.csv")
    parser.add_argument("--rater2", default="data/labels/v1/irr_subset_rater2_completed.xlsx")
    parser.add_argument("--adjudication", default="data/labels/v1/adjudication.parquet")
    parser.add_argument("--irr-report", default="reports/labels/irr_report.json")
    parser.add_argument(
        "--output-report", default="reports/labels/irr_disagreement_diagnostic_v1.json"
    )
    parser.add_argument("--output-rows", default="reports/labels/irr_disagreement_rows_v1.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_diagnostic(args)
    print(
        "[irr] disagreement_diagnostic "
        f"reviewed_items={report['summary']['reviewed_items']} "
        f"rows_disagreement={report['summary']['rows_disagreement']} "
        f"headline_kappa={report['summary']['headline_three_class_kappa']}"
    )
    print(f"[irr] report -> {args.output_report}")


if __name__ == "__main__":
    main()
