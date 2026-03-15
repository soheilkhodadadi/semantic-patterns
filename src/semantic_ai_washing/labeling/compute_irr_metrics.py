"""Compute human-human IRR metrics and publish truthful status artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

import pandas as pd

from semantic_ai_washing.labeling.common import ALLOWED_LABELS, ensure_allowed_label, load_table

TRANSITIONS = ["A->S", "A->I", "S->A", "S->I", "I->A", "I->S"]
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


def _write_empty_confusion(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(0, index=list(ALLOWED_LABELS), columns=list(ALLOWED_LABELS)).to_csv(
        path, index_label="rater1_label"
    )


def _write_transition_counts(path: Path, counts: dict[str, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [{"transition": key, "count": int(counts.get(key, 0))} for key in TRANSITIONS]
    pd.DataFrame(rows).to_csv(path, index=False)


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


def _load_json(path: str | Path) -> dict:
    resolved = Path(path)
    if not resolved.exists():
        return {}
    return json.loads(resolved.read_text(encoding="utf-8"))


def _load_master(path: str | Path) -> pd.DataFrame:
    master = load_table(path)
    if "irr_item_id" not in master.columns:
        raise ValueError("Master file must contain `irr_item_id`.")
    if "rater1_label" not in master.columns and "label" in master.columns:
        master["rater1_label"] = master["label"]
    if "rater1_label" not in master.columns:
        raise ValueError("Master file must contain `rater1_label` or `label`.")
    if "sample_id" not in master.columns:
        if "batch_row_id" in master.columns:
            master["sample_id"] = master["batch_row_id"]
        else:
            master["sample_id"] = master["irr_item_id"]
    for column in ["source_cik", "source_year", "ff12_code", "sample_id"]:
        if column not in master.columns:
            master[column] = ""
        master[column] = master[column].fillna("").astype(str)
    master["rater1_label"] = master["rater1_label"].map(ensure_allowed_label)
    return master[master["rater1_label"].isin(ALLOWED_LABELS)].copy()


def _load_rater2(path: str | Path) -> pd.DataFrame | None:
    resolved = Path(path)
    if not resolved.exists():
        return None
    frame = load_table(resolved)
    if "irr_item_id" not in frame.columns or "rater2_label" not in frame.columns:
        return None
    out = frame[["irr_item_id", "rater2_label"]].copy()
    out["rater2_label"] = out["rater2_label"].map(ensure_allowed_label)
    if "rater2_note" in frame.columns:
        out["rater2_note"] = frame["rater2_note"].fillna("").astype(str)
    else:
        out["rater2_note"] = ""
    return out


def _load_adjudication(path: str | Path) -> pd.DataFrame | None:
    resolved = Path(path)
    if not resolved.exists():
        return None
    frame = load_table(resolved)
    if "irr_item_id" not in frame.columns:
        return None
    for column in ["resolved_label", "resolution_source", "disagreement_pair"]:
        if column not in frame.columns:
            frame[column] = ""
    frame["resolved_label"] = frame["resolved_label"].map(ensure_allowed_label)
    frame["resolution_source"] = frame["resolution_source"].fillna("").astype(str)
    frame["disagreement_pair"] = frame["disagreement_pair"].fillna("").astype(str)
    return frame[
        ["irr_item_id", "resolved_label", "resolution_source", "disagreement_pair"]
    ].copy()


def _sampling_flags(path: str | Path) -> tuple[bool, bool]:
    payload = _load_json(path)
    summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
    return (
        bool(summary.get("stratified_100_firms_min", False)),
        bool(summary.get("industry_year_balanced", False)),
    )


def _attestation_flags(path: str | Path) -> dict[str, object]:
    payload = _load_json(path)
    return {
        "human_human_only": bool(payload.get("human_human_only", True)),
        "third_adjudicator_used": bool(payload.get("third_adjudicator_used", False)),
        "blind_mode": payload.get("blind_mode", "text_only"),
        "handoff_formats": payload.get("handoff_formats", ["csv", "xlsx"]),
    }


def _build_report(
    *,
    args: argparse.Namespace,
    master_rows: int,
    scored_rows: int,
    firms_reviewed: int,
    status_name: str,
    kappa: float | None,
    rows_disagreement: int,
    transition_counts: dict[str, int],
    by_class_kappa: dict[str, float | None],
    stratified_100_firms_min: bool,
    industry_year_balanced: bool,
    human_human_only: bool,
    third_adjudicator_used: bool,
    pending_reason: str = "",
) -> tuple[dict, dict, int]:
    if status_name in {"pending_rater2", "pending_adjudication"}:
        gate_result = "deferred"
    elif kappa is not None and kappa >= float(args.min_kappa):
        gate_result = "pass"
    else:
        gate_result = "fail"

    report = {
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "git_commit": _git_commit(),
        "inputs": {
            "master": args.master,
            "rater2": args.rater2,
            "adjudication": args.adjudication,
            "sampling_report": args.sampling_report,
            "attestation": args.attestation,
            "master_sha256": _sha256_if_exists(args.master),
            "rater2_sha256": _sha256_if_exists(args.rater2),
            "adjudication_sha256": _sha256_if_exists(args.adjudication),
            "sampling_report_sha256": _sha256_if_exists(args.sampling_report),
            "attestation_sha256": _sha256_if_exists(args.attestation),
        },
        "parameters": {
            "min_kappa": float(args.min_kappa),
            "gate_mode": str(args.gate_mode),
        },
        "summary": {
            "status": status_name,
            "reviewed_items": int(scored_rows),
            "kappa": kappa,
            "human_human_only": bool(human_human_only),
            "stratified_100_firms_min": bool(stratified_100_firms_min),
            "industry_year_balanced": bool(industry_year_balanced),
            "by_class_kappa_reported": all(value is not None for value in by_class_kappa.values()),
            "third_adjudicator_used": bool(third_adjudicator_used),
            "firms_reviewed": int(firms_reviewed),
            "rows_disagreement": int(rows_disagreement),
            "rows_master": int(master_rows),
            "transition_counts": transition_counts,
            "by_class_kappa": by_class_kappa,
            "pending_reason": pending_reason,
        },
        "artifacts": {
            "confusion_matrix": args.output_confusion,
            "transition_counts": args.output_transitions,
            "status_file": args.output_status,
        },
    }
    status = {
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "gate_mode": str(args.gate_mode),
        "gate_result": gate_result,
        "status": status_name,
        "min_kappa": float(args.min_kappa),
        "kappa": kappa,
        "rows_master": int(master_rows),
        "rows_scored": int(scored_rows),
        "rows_disagreement": int(rows_disagreement),
        "firms_reviewed": int(firms_reviewed),
    }
    exit_code = 0 if args.gate_mode == "infrastructure" or gate_result != "fail" else 1
    return report, status, exit_code


def run_metrics(args: argparse.Namespace) -> tuple[dict, dict, int]:
    out_report = Path(args.output_report)
    out_confusion = Path(args.output_confusion)
    out_transitions = Path(args.output_transitions)
    out_status = Path(args.output_status)
    for path in [out_report, out_confusion, out_transitions, out_status]:
        path.parent.mkdir(parents=True, exist_ok=True)

    master = _load_master(args.master)
    rows_master = int(len(master))
    stratified_100_firms_min, industry_year_balanced = _sampling_flags(args.sampling_report)
    attestation = _attestation_flags(args.attestation)

    rater2 = _load_rater2(args.rater2)
    if rater2 is None:
        _write_empty_confusion(out_confusion)
        _write_transition_counts(out_transitions, {key: 0 for key in TRANSITIONS})
        report, status, exit_code = _build_report(
            args=args,
            master_rows=rows_master,
            scored_rows=0,
            firms_reviewed=0,
            status_name="pending_rater2",
            kappa=None,
            rows_disagreement=0,
            transition_counts={key: 0 for key in TRANSITIONS},
            by_class_kappa={label: None for label in ALLOWED_LABELS},
            stratified_100_firms_min=stratified_100_firms_min,
            industry_year_balanced=industry_year_balanced,
            human_human_only=bool(attestation["human_human_only"]),
            third_adjudicator_used=bool(attestation["third_adjudicator_used"]),
            pending_reason="rater2_file_missing_or_invalid",
        )
        out_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
        out_status.write_text(json.dumps(status, indent=2), encoding="utf-8")
        return report, status, exit_code

    master_for_merge = master.drop(
        columns=[col for col in ["rater2_label", "rater2_note"] if col in master.columns],
        errors="ignore",
    )
    merged = master_for_merge.merge(rater2, on="irr_item_id", how="left")
    merged["rater2_label"] = merged["rater2_label"].fillna("")
    merged["rater2_note"] = merged["rater2_note"].fillna("")
    scored = merged[merged["rater2_label"].isin(ALLOWED_LABELS)].copy()
    rows_scored = int(len(scored))
    missing_rater2 = rows_master - rows_scored
    if rows_scored == 0 or missing_rater2 > 0:
        _write_empty_confusion(out_confusion)
        _write_transition_counts(out_transitions, {key: 0 for key in TRANSITIONS})
        firms_reviewed = int(scored["source_cik"].replace("", pd.NA).dropna().nunique())
        report, status, exit_code = _build_report(
            args=args,
            master_rows=rows_master,
            scored_rows=rows_scored,
            firms_reviewed=firms_reviewed,
            status_name="pending_rater2",
            kappa=None,
            rows_disagreement=0,
            transition_counts={key: 0 for key in TRANSITIONS},
            by_class_kappa={label: None for label in ALLOWED_LABELS},
            stratified_100_firms_min=stratified_100_firms_min,
            industry_year_balanced=industry_year_balanced,
            human_human_only=bool(attestation["human_human_only"]),
            third_adjudicator_used=bool(attestation["third_adjudicator_used"]),
            pending_reason="rater2_labels_incomplete",
        )
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

    disagreements = scored[scored["rater1_label"] != scored["rater2_label"]].copy()
    transition_counts = {key: 0 for key in TRANSITIONS}
    for _, row in disagreements.iterrows():
        key = f"{SHORT[row['rater1_label']]}->{SHORT[row['rater2_label']]}"
        transition_counts[key] += 1
    _write_transition_counts(out_transitions, transition_counts)

    by_class_kappa: dict[str, float | None] = {}
    for label in ALLOWED_LABELS:
        binary = pd.DataFrame(
            {
                "r1": scored["rater1_label"].eq(label).map({True: label, False: f"not_{label}"}),
                "r2": scored["rater2_label"].eq(label).map({True: label, False: f"not_{label}"}),
            }
        )
        binary_confusion = pd.crosstab(binary["r1"], binary["r2"], dropna=False)
        for key in [label, f"not_{label}"]:
            if key not in binary_confusion.index:
                binary_confusion.loc[key, :] = 0
            if key not in binary_confusion.columns:
                binary_confusion.loc[:, key] = 0
        binary_confusion = binary_confusion.loc[[label, f"not_{label}"], [label, f"not_{label}"]]
        by_class_kappa[label] = float(_cohen_kappa(binary_confusion))

    kappa = float(_cohen_kappa(confusion))
    firms_reviewed = int(scored["source_cik"].replace("", pd.NA).dropna().nunique())

    adjudication = _load_adjudication(args.adjudication)
    resolved_disagreements = 0
    unresolved_disagreements = int(len(disagreements))
    third_adjudicator_used = bool(attestation["third_adjudicator_used"])
    status_name = "passed" if kappa >= float(args.min_kappa) else "failed"
    pending_reason = ""
    if not disagreements.empty:
        if adjudication is None:
            status_name = "pending_adjudication"
            pending_reason = "adjudication_file_missing"
        else:
            disagreement_ids = set(disagreements["irr_item_id"].astype(str))
            resolved = adjudication[
                adjudication["irr_item_id"].astype(str).isin(disagreement_ids)
                & adjudication["resolved_label"].isin(ALLOWED_LABELS)
            ].copy()
            resolved_disagreements = int(len(resolved))
            unresolved_disagreements = int(len(disagreements) - resolved_disagreements)
            if unresolved_disagreements > 0:
                status_name = "pending_adjudication"
                pending_reason = "adjudication_incomplete"
            elif resolved_disagreements > 0:
                third_adjudicator_used = True

    report, status, exit_code = _build_report(
        args=args,
        master_rows=rows_master,
        scored_rows=rows_scored,
        firms_reviewed=firms_reviewed,
        status_name=status_name,
        kappa=kappa,
        rows_disagreement=int(len(disagreements)),
        transition_counts=transition_counts,
        by_class_kappa=by_class_kappa,
        stratified_100_firms_min=stratified_100_firms_min,
        industry_year_balanced=industry_year_balanced,
        human_human_only=bool(attestation["human_human_only"]),
        third_adjudicator_used=third_adjudicator_used,
        pending_reason=pending_reason,
    )
    report["summary"]["resolved_disagreements"] = int(resolved_disagreements)
    report["summary"]["unresolved_disagreements"] = int(unresolved_disagreements)
    status["resolved_disagreements"] = int(resolved_disagreements)
    status["unresolved_disagreements"] = int(unresolved_disagreements)

    out_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    out_status.write_text(json.dumps(status, indent=2), encoding="utf-8")
    return report, status, exit_code


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute IRR metrics and truthful workflow status."
    )
    parser.add_argument("--master", default="data/labels/v1/irr_subset_master.csv")
    parser.add_argument("--rater2", default="data/labels/v1/irr_subset_rater2_completed.xlsx")
    parser.add_argument("--adjudication", default="data/labels/v1/adjudication.parquet")
    parser.add_argument(
        "--sampling-report",
        default="reports/labels/irr_subset_sampling_report.json",
    )
    parser.add_argument("--attestation", default="reports/labels/irr_attestation.json")
    parser.add_argument("--output-report", default="reports/labels/irr_report.json")
    parser.add_argument(
        "--output-confusion",
        default="reports/labels/irr_confusion_matrix.csv",
    )
    parser.add_argument(
        "--output-transitions",
        default="reports/labels/irr_transition_counts.csv",
    )
    parser.add_argument("--output-status", default="reports/labels/irr_status.json")
    parser.add_argument("--min-kappa", type=float, default=0.70)
    parser.add_argument(
        "--gate-mode", choices=("infrastructure", "strict"), default="infrastructure"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    _, status, exit_code = run_metrics(args)
    print(
        f"[irr] status={status['status']} gate_result={status['gate_result']} "
        f"rows_scored={status.get('rows_scored', 0)} kappa={status.get('kappa')}"
    )
    print(f"[irr] report -> {args.output_report}")
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
