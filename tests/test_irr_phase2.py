from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from semantic_ai_washing.labeling.adjudicate_irr_labels import run_adjudication
from semantic_ai_washing.labeling.audit_sentence_integrity import run_audit
from semantic_ai_washing.labeling.compute_irr_metrics import run_metrics
from semantic_ai_washing.labeling.prepare_irr_subset import run_prepare


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_audit_sentence_integrity_and_prepare_subset_outputs(tmp_path):
    input_path = tmp_path / "labels_master_review.csv"
    report_path = tmp_path / "reports" / "irr_sentence_quality.json"
    rows = []
    for label_idx, label in enumerate(["Actionable", "Speculative", "Irrelevant"], start=1):
        for firm_idx in range(50):
            rows.append(
                {
                    "batch_row_id": f"b{label_idx}_{firm_idx}",
                    "sentence_id": f"s{label_idx}_{firm_idx}",
                    "sentence": f"Firm {label_idx}-{firm_idx} uses AI capability sentence.",
                    "label": label,
                    "source_year": "2024",
                    "source_form": "10-K",
                    "source_cik": f"{label_idx}{firm_idx:04d}",
                    "source_file": f"file_{label_idx}_{firm_idx}.txt",
                    "sentence_index": firm_idx,
                    "ff12_code": str((firm_idx % 3) + 10),
                    "ff12_name": "Bucket",
                }
            )
    _write_csv(input_path, rows)

    audit = run_audit(
        argparse.Namespace(
            input_csv=str(input_path),
            output_report=str(report_path),
            threshold=0.15,
        )
    )
    assert audit["passed"] is True
    assert audit["fragment_rows"] == 0

    args = argparse.Namespace(
        input=str(input_path),
        output_parquet=str(tmp_path / "irr_subset.parquet"),
        output_master_csv=str(tmp_path / "irr_subset_master.csv"),
        output_blinded_csv=str(tmp_path / "irr_subset_rater2_blinded.csv"),
        output_blinded_xlsx=str(tmp_path / "irr_subset_rater2_blinded.xlsx"),
        output_report=str(tmp_path / "reports" / "irr_subset_sampling_report.json"),
        attestation_output=str(tmp_path / "reports" / "irr_attestation.json"),
        target_size=120,
        class_quota=40,
        min_unique_firms=100,
        seed=20260314,
        blind_mode="text_only",
    )
    report = run_prepare(args)

    subset = pd.read_parquet(tmp_path / "irr_subset.parquet")
    master = pd.read_csv(tmp_path / "irr_subset_master.csv")
    blinded = pd.read_csv(tmp_path / "irr_subset_rater2_blinded.csv")

    assert len(subset) == 120
    assert report["summary"]["rows_selected"] == 120
    assert report["summary"]["unique_firms"] >= 100
    assert report["summary"]["stratified_100_firms_min"] is True
    assert report["summary"]["industry_year_balanced"] is True
    assert subset["rater1_label"].value_counts().to_dict() == {
        "Actionable": 40,
        "Speculative": 40,
        "Irrelevant": 40,
    }
    assert list(blinded.columns) == ["irr_item_id", "sentence", "rater2_label", "rater2_note"]
    assert (tmp_path / "irr_subset_rater2_blinded.xlsx").exists()
    assert (master["sample_id"] == master["batch_row_id"]).all()
    assert (
        json.loads((tmp_path / "reports" / "irr_attestation.json").read_text())["blind_mode"]
        == "text_only"
    )


def test_compute_irr_metrics_pending_rater2(tmp_path):
    master_path = tmp_path / "master.csv"
    _write_csv(
        master_path,
        [
            {
                "irr_item_id": "i1",
                "batch_row_id": "b1",
                "rater1_label": "Actionable",
                "source_cik": "1001",
                "source_year": "2024",
                "ff12_code": "10",
            },
            {
                "irr_item_id": "i2",
                "batch_row_id": "b2",
                "rater1_label": "Speculative",
                "source_cik": "1002",
                "source_year": "2024",
                "ff12_code": "11",
            },
        ],
    )
    _write_json(
        tmp_path / "sampling.json",
        {"summary": {"stratified_100_firms_min": True, "industry_year_balanced": True}},
    )
    _write_json(
        tmp_path / "attestation.json",
        {"human_human_only": True, "third_adjudicator_used": False},
    )

    args = argparse.Namespace(
        master=str(master_path),
        rater2=str(tmp_path / "missing.xlsx"),
        adjudication=str(tmp_path / "missing.parquet"),
        sampling_report=str(tmp_path / "sampling.json"),
        attestation=str(tmp_path / "attestation.json"),
        output_report=str(tmp_path / "report.json"),
        output_confusion=str(tmp_path / "conf.csv"),
        output_transitions=str(tmp_path / "trans.csv"),
        output_status=str(tmp_path / "status.json"),
        min_kappa=0.70,
        gate_mode="infrastructure",
    )
    report, status, code = run_metrics(args)
    assert code == 0
    assert status["status"] == "pending_rater2"
    assert report["summary"]["reviewed_items"] == 0
    assert report["summary"]["human_human_only"] is True
    assert report["summary"]["stratified_100_firms_min"] is True


def test_adjudication_and_compute_finalize_from_xlsx(tmp_path):
    master_path = tmp_path / "master.csv"
    r2_path = tmp_path / "rater2.xlsx"
    adjudication_input = tmp_path / "irr_adjudication_completed.xlsx"
    sampling_path = tmp_path / "sampling.json"
    attestation_path = tmp_path / "attestation.json"
    _write_csv(
        master_path,
        [
            {
                "irr_item_id": "i1",
                "sample_id": "s1",
                "batch_row_id": "b1",
                "sentence_id": "t1",
                "sentence": "Sentence one uses AI.",
                "source_cik": "1001",
                "source_year": "2024",
                "source_form": "10-K",
                "source_file": "f1.txt",
                "sentence_index": 1,
                "ff12_code": "10",
                "ff12_name": "Tech",
                "rater1_label": "Actionable",
            },
            {
                "irr_item_id": "i2",
                "sample_id": "s2",
                "batch_row_id": "b2",
                "sentence_id": "t2",
                "sentence": "Sentence two may use AI.",
                "source_cik": "1002",
                "source_year": "2024",
                "source_form": "10-K",
                "source_file": "f2.txt",
                "sentence_index": 2,
                "ff12_code": "11",
                "ff12_name": "Shops",
                "rater1_label": "Speculative",
            },
            {
                "irr_item_id": "i3",
                "sample_id": "s3",
                "batch_row_id": "b3",
                "sentence_id": "t3",
                "sentence": "Sentence three is generic AI language.",
                "source_cik": "1003",
                "source_year": "2024",
                "source_form": "10-K",
                "source_file": "f3.txt",
                "sentence_index": 3,
                "ff12_code": "12",
                "ff12_name": "Other",
                "rater1_label": "Irrelevant",
            },
        ],
    )
    pd.DataFrame(
        [
            {
                "irr_item_id": "i1",
                "sentence": "Sentence one uses AI.",
                "rater2_label": "Actionable",
            },
            {
                "irr_item_id": "i2",
                "sentence": "Sentence two may use AI.",
                "rater2_label": "Irrelevant",
            },
            {
                "irr_item_id": "i3",
                "sentence": "Sentence three is generic AI language.",
                "rater2_label": "Irrelevant",
            },
        ]
    ).to_excel(r2_path, index=False)
    _write_json(
        sampling_path,
        {"summary": {"stratified_100_firms_min": True, "industry_year_balanced": True}},
    )
    _write_json(
        attestation_path,
        {"human_human_only": True, "third_adjudicator_used": False},
    )

    adj_args = argparse.Namespace(
        master=str(master_path),
        rater2=str(r2_path),
        adjudication_input=str(adjudication_input),
        output_sheet_csv=str(tmp_path / "irr_adjudication_sheet.csv"),
        output_sheet_xlsx=str(tmp_path / "irr_adjudication_sheet.xlsx"),
        output_parquet=str(tmp_path / "adjudication.parquet"),
        output_status=str(tmp_path / "adjudication_status.json"),
        allow_pending=True,
    )
    status_pending, code_pending = run_adjudication(adj_args)
    assert code_pending == 0
    assert status_pending["summary"]["status"] == "pending_adjudication"

    sheet = pd.read_csv(tmp_path / "irr_adjudication_sheet.csv")
    assert len(sheet) == 1
    sheet["final_label"] = sheet["final_label"].fillna("").astype(str)
    sheet["adjudication_note"] = sheet["adjudication_note"].fillna("").astype(str)
    sheet.loc[sheet["irr_item_id"] == "i2", "final_label"] = "Irrelevant"
    sheet.loc[sheet["irr_item_id"] == "i2", "adjudication_note"] = "Confirmed as generic."
    sheet.to_excel(adjudication_input, index=False)

    status_final, code_final = run_adjudication(adj_args)
    assert code_final == 0
    assert status_final["summary"]["status"] == "finalized"

    adjudication = pd.read_parquet(tmp_path / "adjudication.parquet")
    resolved = adjudication.set_index("irr_item_id")["resolved_label"].to_dict()
    assert resolved["i1"] == "Actionable"
    assert resolved["i2"] == "Irrelevant"
    assert resolved["i3"] == "Irrelevant"

    metric_args = argparse.Namespace(
        master=str(master_path),
        rater2=str(r2_path),
        adjudication=str(tmp_path / "adjudication.parquet"),
        sampling_report=str(sampling_path),
        attestation=str(attestation_path),
        output_report=str(tmp_path / "irr_report.json"),
        output_confusion=str(tmp_path / "irr_conf.csv"),
        output_transitions=str(tmp_path / "irr_trans.csv"),
        output_status=str(tmp_path / "irr_status.json"),
        min_kappa=0.0,
        gate_mode="strict",
    )
    report, status, code = run_metrics(metric_args)
    assert code == 0
    assert status["status"] == "passed"
    assert report["summary"]["third_adjudicator_used"] is True
    assert report["summary"]["by_class_kappa_reported"] is True
    assert report["summary"]["rows_disagreement"] == 1
