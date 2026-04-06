from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from ai_washing_member.labeling.publish_rubric_freeze import run_publish


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _labels_master_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for firm_idx in range(10):
        source_cik = f"{1000 + firm_idx}"
        manifest_id = f"manifest_{firm_idx % 2}"
        for label_idx, label in enumerate(["Actionable", "Speculative", "Irrelevant"], start=1):
            rows.append(
                {
                    "sentence_id": f"s_{firm_idx}_{label_idx}",
                    "sentence": f"Firm {firm_idx} sentence {label_idx} about AI.",
                    "label": label,
                    "source_cik": source_cik,
                    "manifest_id": manifest_id,
                    "batch_row_id": f"b_{firm_idx}_{label_idx}",
                    "source_year": 2024,
                    "sentence_text_id": f"txt_{firm_idx}_{label_idx}",
                }
            )
    return rows


def test_publish_rubric_freeze_member_preserves_preliminary_attestation(tmp_path):
    labels_master_path = tmp_path / "labels_master.parquet"
    split_registry_json = tmp_path / "split_registry_v1.json"
    irr_report_path = tmp_path / "irr_report.json"
    diagnostic_path = tmp_path / "irr_disagreement_diagnostic_v1.json"
    output_report = tmp_path / "rubric_freeze_v2.json"

    pd.DataFrame(_labels_master_rows()).to_parquet(labels_master_path, index=False)
    _write_json(
        split_registry_json,
        {
            "status": "frozen",
            "summary": {
                "rows_total": 30,
                "rows_by_split": {"train": 24, "validation": 6},
                "label_actuals_validation": {
                    "Actionable": 2,
                    "Speculative": 2,
                    "Irrelevant": 2,
                },
                "heldout_overlap_count": 0,
                "source_cik_cross_split_count": 0,
                "sentence_text_id_cross_split_count": 0,
            },
        },
    )
    _write_json(
        irr_report_path,
        {
            "summary": {
                "status": "failed",
                "kappa": 0.675,
                "reviewed_items": 120,
                "rows_disagreement": 26,
                "third_adjudicator_used": True,
            }
        },
    )
    _write_json(
        diagnostic_path,
        {
            "summary": {
                "headline_irr_status": "failed",
                "headline_three_class_kappa": 0.675,
                "binary_relevance_kappa": 0.7586,
                "actionable_speculative_conditional_kappa": 0.6364,
                "rows_disagreement": 26,
            }
        },
    )

    report = run_publish(
        argparse.Namespace(
            irr_report=str(irr_report_path),
            diagnostic_report=str(diagnostic_path),
            split_registry_json=str(split_registry_json),
            labels_master=str(labels_master_path),
            output_report=str(output_report),
            rubric_version="v2.4",
            source_window_id="active_2021_2024",
        )
    )

    assert report["status"] == "provisional_frozen"
    assert report["preliminary_only"] is True
    assert report["publication_grade_authorized"] is False
    assert report["summary"]["irr_kappa"] == 0.675
