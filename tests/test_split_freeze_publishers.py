from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import pytest

from ai_washing_member.labeling.freeze_split_registry import run_freeze
from semantic_ai_washing.labeling.publish_rubric_freeze import run_publish


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


def test_freeze_split_registry_deterministic_grouped_assignment(tmp_path):
    labels_master_path = tmp_path / "labels_master.parquet"
    held_out_path = tmp_path / "held_out.csv"
    output_csv = tmp_path / "split_registry_v1.csv"
    output_json = tmp_path / "split_registry_v1.json"
    second_csv = tmp_path / "split_registry_v1_second.csv"
    second_json = tmp_path / "split_registry_v1_second.json"

    pd.DataFrame(_labels_master_rows()).to_parquet(labels_master_path, index=False)
    pd.DataFrame([{"sentence": "held out sentence"}]).to_csv(held_out_path, index=False)

    args = argparse.Namespace(
        labels_master=str(labels_master_path),
        held_out=str(held_out_path),
        output_csv=str(output_csv),
        output_json=str(output_json),
        split_version="v1",
        seed=20260315,
        validation_frac=0.20,
        max_class_deviation=5,
        min_validation_rows=None,
        max_validation_rows=None,
    )
    payload = run_freeze(args)
    rerun_payload = run_freeze(
        argparse.Namespace(
            **{
                **vars(args),
                "output_csv": str(second_csv),
                "output_json": str(second_json),
            }
        )
    )

    registry = pd.read_csv(output_csv)
    rerun_registry = pd.read_csv(second_csv)

    assert payload["status"] == "frozen"
    assert payload["summary"]["rows_total"] == 30
    assert payload["summary"]["validation_row_count"] == 6
    assert payload["summary"]["label_targets_validation"] == {
        "Actionable": 2,
        "Speculative": 2,
        "Irrelevant": 2,
    }
    assert payload["summary"]["label_actuals_validation"] == {
        "Actionable": 2,
        "Speculative": 2,
        "Irrelevant": 2,
    }
    assert payload["summary"]["source_cik_cross_split_count"] == 0
    assert payload["summary"]["sentence_text_id_cross_split_count"] == 0
    assert payload["summary"]["heldout_external"] is True
    assert payload["summary"]["heldout_overlap_count"] == 0
    assert list(registry.columns) == [
        "sentence_id",
        "split",
        "split_version",
        "assignment_reason",
        "seed",
        "source_manifest_id",
        "source_cik",
        "label",
        "batch_row_id",
        "sentence_text_id",
        "source_year",
    ]
    assert (
        registry.sort_values("sentence_id")
        .reset_index(drop=True)
        .equals(rerun_registry.sort_values("sentence_id").reset_index(drop=True))
    )
    assert (
        rerun_payload["summary"]["label_actuals_validation"]
        == payload["summary"]["label_actuals_validation"]
    )
    assert registry.groupby("source_cik")["split"].nunique().eq(1).all()


def test_freeze_split_registry_fails_when_grouped_constraints_are_impossible(tmp_path):
    labels_master_path = tmp_path / "labels_master.parquet"
    held_out_path = tmp_path / "held_out.csv"
    output_csv = tmp_path / "split_registry_v1.csv"
    output_json = tmp_path / "split_registry_v1.json"

    pd.DataFrame(_labels_master_rows()).to_parquet(labels_master_path, index=False)
    pd.DataFrame([{"sentence": "held out sentence"}]).to_csv(held_out_path, index=False)

    args = argparse.Namespace(
        labels_master=str(labels_master_path),
        held_out=str(held_out_path),
        output_csv=str(output_csv),
        output_json=str(output_json),
        split_version="v1",
        seed=20260315,
        validation_frac=0.20,
        max_class_deviation=5,
        min_validation_rows=7,
        max_validation_rows=7,
    )

    with pytest.raises(SystemExit):
        run_freeze(args)

    failure_payload = json.loads(output_json.read_text(encoding="utf-8"))
    assert failure_payload["status"] == "failed"
    assert "Grouped source_cik split could not satisfy" in failure_payload["failure_reason"]
    assert not output_csv.exists()


def test_publish_rubric_freeze_preserves_truthful_irr_context(tmp_path):
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
    assert report["summary"]["split_registry_status"] == "frozen"
    assert "0.675" in report["known_limitations"][0]
    assert report["references"]["labels_master"]["sha256"]
    assert report["references"]["split_registry"]["summary_excerpt"]["rows_total"] == 30
    assert report["references"]["irr_report"]["summary_excerpt"]["status"] == "failed"
    assert (
        report["references"]["irr_disagreement_diagnostic"]["summary_excerpt"][
            "headline_three_class_kappa"
        ]
        == 0.675
    )
