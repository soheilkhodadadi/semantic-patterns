from __future__ import annotations

import argparse
import json

import pandas as pd

from ai_washing_member.labeling.publish_preliminary_results_readiness import run_publish


def test_run_publish_keeps_publication_gate_false(tmp_path) -> None:
    labels_master_path = tmp_path / "labels_master.parquet"
    held_out_path = tmp_path / "held_out.csv"
    split_registry_csv = tmp_path / "split_registry_v1.csv"
    split_registry_json = tmp_path / "split_registry_v1.json"
    rubric_freeze_path = tmp_path / "rubric_freeze_v2.json"
    irr_report_path = tmp_path / "irr_report.json"
    diagnostic_path = tmp_path / "irr_disagreement_diagnostic_v1.json"

    rows = []
    for idx in range(200):
        rows.append({"label": "Actionable", "sentence": f"Actionable sentence {idx}"})
    for idx in range(180):
        rows.append({"label": "Speculative", "sentence": f"Speculative sentence {idx}"})
    for idx in range(171):
        rows.append({"label": "Irrelevant", "sentence": f"Irrelevant sentence {idx}"})
    pd.DataFrame(rows).to_parquet(labels_master_path, index=False)
    pd.DataFrame([{"sentence": "held out sentence"}]).to_csv(held_out_path, index=False)
    pd.DataFrame([{"sample_id": "s1", "split": "train"}]).to_csv(split_registry_csv, index=False)
    split_registry_json.write_text(
        json.dumps(
            {
                "status": "frozen",
                "summary": {
                    "rows_total": 551,
                    "heldout_overlap_count": 0,
                    "source_cik_cross_split_count": 0,
                    "sentence_text_id_cross_split_count": 0,
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    rubric_freeze_path.write_text(
        json.dumps({"status": "provisional_frozen"}, indent=2),
        encoding="utf-8",
    )
    irr_report_path.write_text(
        json.dumps(
            {"summary": {"status": "failed", "kappa": 0.675, "reviewed_items": 120}}, indent=2
        ),
        encoding="utf-8",
    )
    diagnostic_path.write_text(
        json.dumps(
            {
                "summary": {
                    "rows_disagreement": 26,
                    "headline_three_class_kappa": 0.675,
                    "binary_relevance_kappa": 0.79,
                    "actionable_speculative_conditional_kappa": 0.74,
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    report = run_publish(
        argparse.Namespace(
            labels_master=str(labels_master_path),
            irr_report=str(irr_report_path),
            diagnostic_report=str(diagnostic_path),
            held_out=str(held_out_path),
            split_registry_csv=str(split_registry_csv),
            split_registry_json=str(split_registry_json),
            rubric_freeze_report=str(rubric_freeze_path),
            output_report=str(tmp_path / "preliminary_results_readiness_v1.json"),
            source_window_id="active_2021_2024",
            min_total_labels=500,
            min_per_class=80,
            min_irr_reviewed_items=100,
        )
    )

    assert report["summary"]["preliminary_only"] is True
    assert report["summary"]["publication_grade_authorized"] is False
    assert report["summary"]["preliminary_results_authorized"] is True
    assert report["summary"]["source_window_id"] == "active_2021_2024"
    assert report["summary"]["total_adjudicated_labels"] == 551
    assert report["summary"]["min_class_count"] == 171
    assert report["summary"]["irr_kappa"] == 0.675
    assert report["summary"]["heldout_overlap_count"] == 0
    assert report["summary"]["split_registry_frozen"] is True
    assert report["summary"]["split_registry_status"] == "frozen"
    assert report["summary"]["split_registry_rows_total"] == 551
    assert report["summary"]["rubric_freeze_status"] == "provisional_frozen"
