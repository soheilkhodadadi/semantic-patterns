"""Publish a provisional rubric-freeze report for preliminary internal results."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd

from semantic_ai_washing.labeling.common import ensure_allowed_label, load_table


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
        raise FileNotFoundError(f"Required JSON artifact missing: {resolved}")
    return json.loads(resolved.read_text(encoding="utf-8"))


def _load_labels_master(path: str | Path) -> pd.DataFrame:
    frame = load_table(path)
    if "label" not in frame.columns:
        raise ValueError("Labels master must include `label`.")
    frame = frame.copy()
    frame["label"] = frame["label"].map(ensure_allowed_label)
    frame = frame[frame["label"].notna()].copy()
    if frame.empty:
        raise ValueError("Labels master does not contain any canonical labels.")
    return frame


def _format_kappa(value: Any) -> str:
    if value is None or value == "":
        return "unknown"
    return f"{float(value):.3f}"


def run_publish(args: argparse.Namespace) -> dict[str, Any]:
    output_path = Path(args.output_report)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    irr_report = _load_json(args.irr_report)
    diagnostic = _load_json(args.diagnostic_report)
    split_registry = _load_json(args.split_registry_json)
    labels_master = _load_labels_master(args.labels_master)

    if str(split_registry.get("status", "")).strip() != "frozen":
        raise ValueError("Split registry JSON must report `status = frozen`.")

    irr_summary = irr_report.get("summary", {})
    diagnostic_summary = diagnostic.get("summary", {})
    split_summary = split_registry.get("summary", {})
    class_counts = {
        str(label): int(count)
        for label, count in labels_master["label"].value_counts().sort_index().items()
    }

    report = {
        "status": "provisional_frozen",
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "git_commit": _git_commit(),
        "rubric_version": str(args.rubric_version),
        "source_window_id": str(args.source_window_id),
        "preliminary_only": True,
        "publication_grade_authorized": False,
        "attestation_mode": "role_only",
        "freeze_purpose": (
            "stabilize label semantics and split discipline for preliminary internal results"
        ),
        "canonical_publication_gate_status": "blocked",
        "known_limitations": [
            f"Final human-human IRR remains {_format_kappa(irr_summary.get('kappa'))}.",
            "Canonical retraining remains blocked by the > 0.7 human-human IRR gate.",
            "Later rubric changes are allowed only through a future review-driven cycle.",
        ],
        "governance_statement": (
            "Predictive validity or regression significance must not be used to retune the "
            "rubric without a separate review-driven methodology cycle."
        ),
        "references": {
            "labels_master": {
                "path": str(args.labels_master),
                "sha256": _sha256_if_exists(args.labels_master),
                "rows_total": int(len(labels_master)),
                "class_counts": class_counts,
            },
            "split_registry": {
                "path": str(args.split_registry_json),
                "sha256": _sha256_if_exists(args.split_registry_json),
                "summary_excerpt": {
                    "status": split_registry.get("status", ""),
                    "rows_total": split_summary.get("rows_total"),
                    "rows_by_split": split_summary.get("rows_by_split", {}),
                    "label_actuals_validation": split_summary.get("label_actuals_validation", {}),
                    "heldout_overlap_count": split_summary.get("heldout_overlap_count"),
                    "source_cik_cross_split_count": split_summary.get(
                        "source_cik_cross_split_count"
                    ),
                    "sentence_text_id_cross_split_count": split_summary.get(
                        "sentence_text_id_cross_split_count"
                    ),
                },
            },
            "irr_report": {
                "path": str(args.irr_report),
                "sha256": _sha256_if_exists(args.irr_report),
                "summary_excerpt": {
                    "status": irr_summary.get("status", ""),
                    "kappa": irr_summary.get("kappa"),
                    "reviewed_items": irr_summary.get("reviewed_items"),
                    "rows_disagreement": irr_summary.get("rows_disagreement"),
                    "third_adjudicator_used": irr_summary.get("third_adjudicator_used"),
                },
            },
            "irr_disagreement_diagnostic": {
                "path": str(args.diagnostic_report),
                "sha256": _sha256_if_exists(args.diagnostic_report),
                "summary_excerpt": {
                    "headline_irr_status": diagnostic_summary.get("headline_irr_status", ""),
                    "headline_three_class_kappa": diagnostic_summary.get(
                        "headline_three_class_kappa"
                    ),
                    "binary_relevance_kappa": diagnostic_summary.get("binary_relevance_kappa"),
                    "actionable_speculative_conditional_kappa": diagnostic_summary.get(
                        "actionable_speculative_conditional_kappa"
                    ),
                    "rows_disagreement": diagnostic_summary.get("rows_disagreement"),
                },
            },
        },
        "summary": {
            "status": "provisional_frozen",
            "rubric_version": str(args.rubric_version),
            "source_window_id": str(args.source_window_id),
            "preliminary_only": True,
            "publication_grade_authorized": False,
            "canonical_publication_gate_status": "blocked",
            "labels_master_rows": int(len(labels_master)),
            "class_counts": class_counts,
            "split_registry_status": split_registry.get("status", ""),
            "split_rows_total": split_summary.get("rows_total"),
            "split_rows_by_split": split_summary.get("rows_by_split", {}),
            "split_label_actuals_validation": split_summary.get("label_actuals_validation", {}),
            "irr_status": irr_summary.get("status", ""),
            "irr_kappa": irr_summary.get("kappa"),
            "irr_reviewed_items": irr_summary.get("reviewed_items"),
            "rows_disagreement": irr_summary.get("rows_disagreement"),
            "binary_relevance_kappa": diagnostic_summary.get("binary_relevance_kappa"),
            "actionable_speculative_conditional_kappa": diagnostic_summary.get(
                "actionable_speculative_conditional_kappa"
            ),
        },
    }

    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--irr-report", default="reports/labels/irr_report.json")
    parser.add_argument(
        "--diagnostic-report", default="reports/labels/irr_disagreement_diagnostic_v1.json"
    )
    parser.add_argument(
        "--split-registry-json", default="data/metadata/splits/split_registry_v1.json"
    )
    parser.add_argument("--labels-master", default="data/labels/v1/labels_master.parquet")
    parser.add_argument("--output-report", default="reports/labels/rubric_freeze_v2.json")
    parser.add_argument("--rubric-version", default="v2.4")
    parser.add_argument("--source-window-id", default="active_2021_2024")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_publish(args)
    print(
        "[rubric-freeze] published "
        f"status={report['status']} "
        f"irr_kappa={report['summary']['irr_kappa']}"
    )
    print(f"[rubric-freeze] report -> {args.output_report}")


if __name__ == "__main__":
    main()
