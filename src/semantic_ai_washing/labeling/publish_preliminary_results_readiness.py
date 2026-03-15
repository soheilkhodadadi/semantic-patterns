"""Publish a preliminary-results readiness report without weakening publication gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd

from semantic_ai_washing.labeling.common import ensure_allowed_label, normalize_sentence, safe_int


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


def _load_labels_master(path: str | Path) -> pd.DataFrame:
    resolved = Path(path)
    if resolved.suffix.lower() == ".csv":
        frame = pd.read_csv(resolved)
    else:
        frame = pd.read_parquet(resolved)
    if "label" not in frame.columns:
        raise ValueError("Labels master must include `label`.")
    if "sentence" not in frame.columns:
        raise ValueError("Labels master must include `sentence` for held-out overlap checks.")
    frame["label"] = frame["label"].map(ensure_allowed_label)
    return frame[frame["label"].notna()].copy()


def _heldout_overlap_count(labels_master: pd.DataFrame, held_out_path: str | Path) -> int:
    held_out = pd.read_csv(held_out_path)
    if "sentence" not in held_out.columns:
        raise ValueError("Held-out sentences file must include `sentence`.")
    held_out_norms = {
        normalize_sentence(value)
        for value in held_out["sentence"].fillna("").astype(str)
        if normalize_sentence(value)
    }
    label_norms = labels_master["sentence"].fillna("").astype(str).map(normalize_sentence)
    return int(label_norms.isin(held_out_norms).sum())


def run_publish(args: argparse.Namespace) -> dict[str, Any]:
    output_path = Path(args.output_report)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    labels_master = _load_labels_master(args.labels_master)
    irr_report = _load_json(args.irr_report)
    rubric_freeze = _load_json(args.rubric_freeze_report)
    diagnostic = _load_json(args.diagnostic_report)
    split_registry = _load_json(args.split_registry_json)

    class_counts = {
        str(label): int(count)
        for label, count in labels_master["label"].value_counts().sort_index().items()
    }
    heldout_overlap_count = _heldout_overlap_count(labels_master, args.held_out)
    total_adjudicated_labels = int(len(labels_master))
    min_class_count = int(min(class_counts.values())) if class_counts else 0
    split_summary = split_registry.get("summary", {})
    split_registry_frozen = (
        Path(args.split_registry_csv).exists()
        and Path(args.split_registry_json).exists()
        and str(split_registry.get("status", "")).strip() == "frozen"
        and safe_int(split_summary.get("rows_total"), 0) == total_adjudicated_labels
        and safe_int(split_summary.get("heldout_overlap_count"), -1) == 0
        and safe_int(split_summary.get("source_cik_cross_split_count"), -1) == 0
        and safe_int(split_summary.get("sentence_text_id_cross_split_count"), -1) == 0
    )
    rubric_freeze_status = str(rubric_freeze.get("status", "")).strip()
    irr_summary = irr_report.get("summary", {})

    preliminary_results_authorized = bool(
        total_adjudicated_labels >= int(args.min_total_labels)
        and min_class_count >= int(args.min_per_class)
        and heldout_overlap_count == 0
        and split_registry_frozen
        and rubric_freeze_status == "provisional_frozen"
        and int(irr_summary.get("reviewed_items", 0) or 0) >= int(args.min_irr_reviewed_items)
        and str(irr_summary.get("status", "")).strip() in {"passed", "failed"}
    )

    report = {
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "git_commit": _git_commit(),
        "inputs": {
            "labels_master": args.labels_master,
            "irr_report": args.irr_report,
            "diagnostic_report": args.diagnostic_report,
            "held_out": args.held_out,
            "split_registry_csv": args.split_registry_csv,
            "split_registry_json": args.split_registry_json,
            "rubric_freeze_report": args.rubric_freeze_report,
            "labels_master_sha256": _sha256_if_exists(args.labels_master),
            "irr_report_sha256": _sha256_if_exists(args.irr_report),
            "diagnostic_report_sha256": _sha256_if_exists(args.diagnostic_report),
            "held_out_sha256": _sha256_if_exists(args.held_out),
            "split_registry_csv_sha256": _sha256_if_exists(args.split_registry_csv),
            "split_registry_json_sha256": _sha256_if_exists(args.split_registry_json),
            "rubric_freeze_report_sha256": _sha256_if_exists(args.rubric_freeze_report),
        },
        "summary": {
            "preliminary_only": True,
            "source_window_id": str(args.source_window_id),
            "publication_grade_authorized": False,
            "preliminary_results_authorized": preliminary_results_authorized,
            "total_adjudicated_labels": total_adjudicated_labels,
            "min_class_count": min_class_count,
            "class_counts": class_counts,
            "irr_kappa": irr_summary.get("kappa"),
            "irr_reviewed_items": int(irr_summary.get("reviewed_items", 0) or 0),
            "irr_report_status": str(irr_summary.get("status", "")).strip(),
            "heldout_overlap_count": heldout_overlap_count,
            "split_registry_frozen": split_registry_frozen,
            "split_registry_status": str(split_registry.get("status", "")).strip(),
            "split_registry_rows_total": safe_int(split_summary.get("rows_total"), 0),
            "rubric_freeze_status": rubric_freeze_status,
            "diagnostic_rows_disagreement": diagnostic.get("summary", {}).get(
                "rows_disagreement", None
            ),
            "headline_three_class_kappa": diagnostic.get("summary", {}).get(
                "headline_three_class_kappa", irr_summary.get("kappa")
            ),
            "binary_relevance_kappa": diagnostic.get("summary", {}).get("binary_relevance_kappa"),
            "actionable_speculative_conditional_kappa": diagnostic.get("summary", {}).get(
                "actionable_speculative_conditional_kappa"
            ),
        },
    }
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels-master", default="data/labels/v1/labels_master.parquet")
    parser.add_argument("--irr-report", default="reports/labels/irr_report.json")
    parser.add_argument(
        "--diagnostic-report", default="reports/labels/irr_disagreement_diagnostic_v1.json"
    )
    parser.add_argument("--held-out", default="data/validation/held_out_sentences.csv")
    parser.add_argument(
        "--split-registry-csv", default="data/metadata/splits/split_registry_v1.csv"
    )
    parser.add_argument(
        "--split-registry-json", default="data/metadata/splits/split_registry_v1.json"
    )
    parser.add_argument("--rubric-freeze-report", default="reports/labels/rubric_freeze_v2.json")
    parser.add_argument(
        "--output-report", default="reports/models/preliminary_results_readiness_v1.json"
    )
    parser.add_argument("--source-window-id", default="active_2021_2024")
    parser.add_argument("--min-total-labels", type=int, default=500)
    parser.add_argument("--min-per-class", type=int, default=80)
    parser.add_argument("--min-irr-reviewed-items", type=int, default=100)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_publish(args)
    print(
        "[prelim] readiness "
        f"authorized={report['summary']['preliminary_results_authorized']} "
        f"total_labels={report['summary']['total_adjudicated_labels']} "
        f"irr_kappa={report['summary']['irr_kappa']}"
    )
    print(f"[prelim] report -> {args.output_report}")


if __name__ == "__main__":
    main()
