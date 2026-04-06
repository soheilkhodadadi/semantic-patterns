from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from ai_washing_member.labeling.adjudicate_irr_labels import run_adjudication
from ai_washing_member.labeling.audit_sentence_integrity import run_audit
from ai_washing_member.labeling.compute_irr_metrics import run_metrics
from ai_washing_member.labeling.diagnose_irr_disagreements import run_diagnostic
from ai_washing_member.labeling.prepare_irr_subset import run_prepare
from ai_washing_member.labeling.publish_preliminary_results_readiness import run_publish


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
                "rater2_label": "",
                "rater2_note": "",
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
                "rater2_label": "",
                "rater2_note": "",
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
                "rater2_label": "",
                "rater2_note": "",
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


def test_diagnose_irr_disagreements_publishes_secondary_metrics(tmp_path):
    master_path = tmp_path / "irr_subset_master.csv"
    rater2_path = tmp_path / "irr_subset_rater2_completed.xlsx"
    adjudication_path = tmp_path / "adjudication.parquet"
    irr_report_path = tmp_path / "irr_report.json"

    _write_csv(
        master_path,
        [
            {
                "irr_item_id": "i1",
                "sample_id": "s1",
                "batch_row_id": "b1",
                "sentence_id": "t1",
                "sentence": "Sentence one reports deployed AI capabilities.",
                "source_cik": "1001",
                "source_year": "2024",
                "ff12_code": "10",
                "ff12_name": "Tech",
                "rater1_label": "Actionable",
            },
            {
                "irr_item_id": "i2",
                "sample_id": "s2",
                "batch_row_id": "b2",
                "sentence_id": "t2",
                "sentence": "Sentence two says AI may improve operations.",
                "source_cik": "1002",
                "source_year": "2024",
                "ff12_code": "11",
                "ff12_name": "Retail",
                "rater1_label": "Speculative",
            },
            {
                "irr_item_id": "i3",
                "sample_id": "s3",
                "batch_row_id": "b3",
                "sentence_id": "t3",
                "sentence": "Sentence three says the firm uses AI in production.",
                "source_cik": "1003",
                "source_year": "2024",
                "ff12_code": "10",
                "ff12_name": "Tech",
                "rater1_label": "Speculative",
            },
            {
                "irr_item_id": "i4",
                "sample_id": "s4",
                "batch_row_id": "b4",
                "sentence_id": "t4",
                "sentence": "Sentence four is generic AI positioning language.",
                "source_cik": "1004",
                "source_year": "2024",
                "ff12_code": "12",
                "ff12_name": "Other",
                "rater1_label": "Irrelevant",
            },
        ],
    )
    pd.DataFrame(
        [
            {"irr_item_id": "i1", "rater2_label": "Actionable"},
            {"irr_item_id": "i2", "rater2_label": "Actionable"},
            {"irr_item_id": "i3", "rater2_label": "Speculative"},
            {"irr_item_id": "i4", "rater2_label": "Irrelevant"},
        ]
    ).to_excel(rater2_path, index=False)
    pd.DataFrame(
        [
            {
                "irr_item_id": "i1",
                "resolved_label": "Actionable",
                "disagreement_pair": "",
                "transition": "",
                "resolution_source": "agreement",
            },
            {
                "irr_item_id": "i2",
                "resolved_label": "Speculative",
                "disagreement_pair": "Speculative vs Actionable",
                "transition": "S->A",
                "resolution_source": "third_adjudicator",
            },
            {
                "irr_item_id": "i3",
                "resolved_label": "Speculative",
                "disagreement_pair": "",
                "transition": "",
                "resolution_source": "agreement",
            },
            {
                "irr_item_id": "i4",
                "resolved_label": "Irrelevant",
                "disagreement_pair": "",
                "transition": "",
                "resolution_source": "agreement",
            },
        ]
    ).to_parquet(adjudication_path, index=False)
    _write_json(irr_report_path, {"summary": {"status": "failed", "kappa": 0.675}})

    report = run_diagnostic(
        argparse.Namespace(
            master=str(master_path),
            rater2=str(rater2_path),
            adjudication=str(adjudication_path),
            irr_report=str(irr_report_path),
            output_report=str(tmp_path / "irr_disagreement_diagnostic_v1.json"),
            output_rows=str(tmp_path / "irr_disagreement_rows_v1.csv"),
        )
    )

    assert report["summary"]["headline_irr_status"] == "failed"
    assert report["summary"]["headline_three_class_kappa"] == 0.675
    assert report["summary"]["reviewed_items"] == 4
    assert report["summary"]["rows_disagreement"] == 1
    assert report["summary"]["unresolved_disagreements"] == 0
    assert report["summary"]["binary_relevance_kappa"] == 1.0
    assert report["summary"]["actionable_speculative_conditional_items"] == 3
    assert round(report["summary"]["actionable_speculative_conditional_kappa"], 6) == 0.4
    assert report["summary"]["rater1_vs_final_agreement"] == 1.0
    assert report["summary"]["rater2_vs_final_agreement"] == 0.75
    assert report["summary"]["transition_counts"] == {"S->A": 1}
    rows = pd.read_csv(tmp_path / "irr_disagreement_rows_v1.csv")
    assert rows["irr_item_id"].tolist() == ["i2"]


def test_publish_preliminary_results_readiness_keeps_publication_gate_false(tmp_path):
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
    _write_csv(held_out_path, [{"sentence": "held out sentence"}])
    _write_csv(split_registry_csv, [{"sample_id": "s1", "split": "train"}])
    _write_json(
        split_registry_json,
        {
            "status": "frozen",
            "summary": {
                "rows_total": 551,
                "heldout_overlap_count": 0,
                "source_cik_cross_split_count": 0,
                "sentence_text_id_cross_split_count": 0,
            },
        },
    )
    _write_json(rubric_freeze_path, {"status": "provisional_frozen"})
    _write_json(
        irr_report_path, {"summary": {"status": "failed", "kappa": 0.675, "reviewed_items": 120}}
    )
    _write_json(
        diagnostic_path,
        {
            "summary": {
                "rows_disagreement": 26,
                "headline_three_class_kappa": 0.675,
                "binary_relevance_kappa": 0.79,
                "actionable_speculative_conditional_kappa": 0.74,
            }
        },
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
