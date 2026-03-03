"""Compute IRR metrics (Cohen's kappa + disagreement taxonomy)."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
from pathlib import Path

import pandas as pd

from semantic_ai_washing.labeling.common import ALLOWED_LABELS, ensure_allowed_label

TRANSITIONS = ["A->S", "A->I", "S->A", "S->I", "I->A", "I->S"]
SHORT = {"Actionable": "A", "Speculative": "S", "Irrelevant": "I"}


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


def _write_empty_confusion(path: Path) -> None:
    df = pd.DataFrame(0, index=list(ALLOWED_LABELS), columns=list(ALLOWED_LABELS))
    df.to_csv(path, index_label="rater1_label")


def _write_transition_counts(path: Path, counts: dict[str, int]) -> None:
    rows = [{"transition": key, "count": int(counts.get(key, 0))} for key in TRANSITIONS]
    pd.DataFrame(rows).to_csv(path, index=False)


def _pending_payload(
    args: argparse.Namespace,
    reason: str,
    master_rows: int,
    scored_rows: int,
) -> tuple[dict, dict, int]:
    report = {
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "git_commit": _git_commit(),
        "inputs": {
            "master": args.master,
            "rater2": args.rater2,
            "master_sha256": _sha256_file(args.master),
            "rater2_sha256": _sha256_file(args.rater2) if os.path.exists(args.rater2) else "",
        },
        "parameters": {
            "min_kappa": float(args.min_kappa),
            "gate_mode": str(args.gate_mode),
        },
        "summary": {
            "status": "pending_rater2",
            "kappa": None,
            "rows_master": int(master_rows),
            "rows_scored": int(scored_rows),
            "reason": reason,
        },
    }
    status = {
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "gate_mode": str(args.gate_mode),
        "gate_result": "deferred",
        "status": "pending_rater2",
        "reason": reason,
        "min_kappa": float(args.min_kappa),
        "kappa": None,
        "rows_master": int(master_rows),
        "rows_scored": int(scored_rows),
    }
    exit_code = 0 if args.gate_mode == "infrastructure" else 1
    return report, status, exit_code


def _cohen_kappa(confusion: pd.DataFrame) -> float:
    n = confusion.values.sum()
    if n == 0:
        return math.nan
    po = float(confusion.values.diagonal().sum()) / float(n)
    row_marginals = confusion.sum(axis=1).values.astype(float)
    col_marginals = confusion.sum(axis=0).values.astype(float)
    pe = float((row_marginals * col_marginals).sum()) / float(n * n)
    if math.isclose(1.0 - pe, 0.0):
        return 1.0 if math.isclose(po, 1.0) else 0.0
    return (po - pe) / (1.0 - pe)


def run_metrics(args: argparse.Namespace) -> tuple[dict, dict, int]:
    out_report = Path(args.output_report)
    out_confusion = Path(args.output_confusion)
    out_transitions = Path(args.output_transitions)
    out_status = Path(args.output_status)
    out_report.parent.mkdir(parents=True, exist_ok=True)
    out_confusion.parent.mkdir(parents=True, exist_ok=True)
    out_transitions.parent.mkdir(parents=True, exist_ok=True)
    out_status.parent.mkdir(parents=True, exist_ok=True)

    master = pd.read_csv(args.master)
    if "irr_item_id" not in master.columns:
        raise ValueError("Master file must contain `irr_item_id`.")
    if "rater1_label" not in master.columns and "label" in master.columns:
        master["rater1_label"] = master["label"]
    if "rater1_label" not in master.columns:
        raise ValueError("Master file must contain `rater1_label`.")

    master["rater1_label"] = master["rater1_label"].map(ensure_allowed_label)
    master = master[master["rater1_label"].isin(ALLOWED_LABELS)].copy()
    rows_master = len(master)

    if not os.path.exists(args.rater2):
        report, status, exit_code = _pending_payload(
            args=args,
            reason="rater2_file_missing",
            master_rows=rows_master,
            scored_rows=0,
        )
        _write_empty_confusion(out_confusion)
        _write_transition_counts(out_transitions, {key: 0 for key in TRANSITIONS})
        out_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
        out_status.write_text(json.dumps(status, indent=2), encoding="utf-8")
        return report, status, exit_code

    r2 = pd.read_csv(args.rater2)
    if "irr_item_id" not in r2.columns or "rater2_label" not in r2.columns:
        report, status, exit_code = _pending_payload(
            args=args,
            reason="rater2_columns_missing",
            master_rows=rows_master,
            scored_rows=0,
        )
        _write_empty_confusion(out_confusion)
        _write_transition_counts(out_transitions, {key: 0 for key in TRANSITIONS})
        out_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
        out_status.write_text(json.dumps(status, indent=2), encoding="utf-8")
        return report, status, exit_code

    r2["rater2_label"] = r2["rater2_label"].map(ensure_allowed_label)
    merged = master[["irr_item_id", "rater1_label"]].merge(
        r2[["irr_item_id", "rater2_label"]],
        on="irr_item_id",
        how="left",
    )
    scored = merged[merged["rater2_label"].isin(ALLOWED_LABELS)].copy()
    rows_scored = len(scored)
    missing_rater2 = rows_master - rows_scored

    if rows_scored == 0 or missing_rater2 > 0:
        reason = "rater2_labels_incomplete"
        report, status, exit_code = _pending_payload(
            args=args,
            reason=reason,
            master_rows=rows_master,
            scored_rows=rows_scored,
        )
        _write_empty_confusion(out_confusion)
        _write_transition_counts(out_transitions, {key: 0 for key in TRANSITIONS})
        out_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
        out_status.write_text(json.dumps(status, indent=2), encoding="utf-8")
        return report, status, exit_code

    confusion = pd.crosstab(
        scored["rater1_label"],
        scored["rater2_label"],
        rownames=["rater1_label"],
        colnames=["rater2_label"],
        dropna=False,
    )
    for label in ALLOWED_LABELS:
        if label not in confusion.index:
            confusion.loc[label, :] = 0
        if label not in confusion.columns:
            confusion.loc[:, label] = 0
    confusion = confusion.loc[list(ALLOWED_LABELS), list(ALLOWED_LABELS)]
    confusion.to_csv(out_confusion)

    kappa = float(_cohen_kappa(confusion))

    transition_counts = {key: 0 for key in TRANSITIONS}
    disagreements = scored[scored["rater1_label"] != scored["rater2_label"]].copy()
    for _, row in disagreements.iterrows():
        key = f"{SHORT[row['rater1_label']]}->{SHORT[row['rater2_label']]}"
        if key in transition_counts:
            transition_counts[key] += 1
    _write_transition_counts(out_transitions, transition_counts)

    class_agreement = {}
    for label in ALLOWED_LABELS:
        row_sum = int(confusion.loc[label].sum())
        tp = int(confusion.loc[label, label])
        class_agreement[label] = float(tp / row_sum) if row_sum > 0 else None

    kappa_status = "pass" if kappa >= float(args.min_kappa) else "fail"
    gate_result = "pass" if kappa_status == "pass" else "fail"

    report = {
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "git_commit": _git_commit(),
        "inputs": {
            "master": args.master,
            "rater2": args.rater2,
            "master_sha256": _sha256_file(args.master),
            "rater2_sha256": _sha256_file(args.rater2),
        },
        "parameters": {
            "min_kappa": float(args.min_kappa),
            "gate_mode": str(args.gate_mode),
        },
        "summary": {
            "status": kappa_status,
            "kappa": kappa,
            "rows_master": int(rows_master),
            "rows_scored": int(rows_scored),
            "rows_disagreement": int(len(disagreements)),
            "class_agreement": class_agreement,
            "transition_counts": transition_counts,
        },
    }

    status = {
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "gate_mode": str(args.gate_mode),
        "gate_result": gate_result,
        "status": kappa_status,
        "min_kappa": float(args.min_kappa),
        "kappa": kappa,
        "rows_master": int(rows_master),
        "rows_scored": int(rows_scored),
    }

    out_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    out_status.write_text(json.dumps(status, indent=2), encoding="utf-8")

    if args.gate_mode == "strict" and kappa < float(args.min_kappa):
        return report, status, 1
    return report, status, 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute IRR metrics and gate status.")
    parser.add_argument("--master", default="data/labels/iteration1/irr/irr_subset_master.csv")
    parser.add_argument(
        "--rater2",
        default="data/labels/iteration1/irr/irr_subset_rater2_completed.csv",
    )
    parser.add_argument(
        "--output-report",
        default="reports/iteration1/phase2_irr/irr_kappa_report.json",
    )
    parser.add_argument(
        "--output-confusion",
        default="reports/iteration1/phase2_irr/irr_confusion_matrix.csv",
    )
    parser.add_argument(
        "--output-transitions",
        default="reports/iteration1/phase2_irr/irr_transition_counts.csv",
    )
    parser.add_argument(
        "--output-status",
        default="reports/iteration1/phase2_irr/irr_status.json",
    )
    parser.add_argument("--min-kappa", type=float, default=0.60)
    parser.add_argument(
        "--gate-mode", choices=("infrastructure", "strict"), default="infrastructure"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report, status, exit_code = run_metrics(args)
    print(
        f"[irr] status={status['status']} gate_result={status['gate_result']} "
        f"rows_scored={status.get('rows_scored', 0)} kappa={status.get('kappa')}"
    )
    print(f"[irr] report -> {args.output_report}")
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
