from __future__ import annotations

import argparse
import json

import pandas as pd

from ai_washing_member.labeling.diagnose_irr_disagreements import run_diagnostic


def test_run_diagnostic_publishes_secondary_metrics(tmp_path) -> None:
    master_path = tmp_path / "irr_subset_master.csv"
    rater2_path = tmp_path / "irr_subset_rater2_completed.xlsx"
    adjudication_path = tmp_path / "adjudication.parquet"
    irr_report_path = tmp_path / "irr_report.json"

    pd.DataFrame(
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
        ]
    ).to_csv(master_path, index=False)
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
                "irr_item_id": "i2",
                "resolved_label": "Actionable",
                "disagreement_pair": "Speculative|Actionable",
                "transition": "S->A",
                "resolution_source": "third_adjudicator",
            }
        ]
    ).to_parquet(adjudication_path, index=False)
    irr_report_path.write_text(
        json.dumps({"summary": {"status": "passed", "kappa": 0.71}}, indent=2),
        encoding="utf-8",
    )

    report = run_diagnostic(
        argparse.Namespace(
            master=str(master_path),
            rater2=str(rater2_path),
            adjudication=str(adjudication_path),
            irr_report=str(irr_report_path),
            output_report=str(tmp_path / "diagnostic.json"),
            output_rows=str(tmp_path / "diagnostic_rows.csv"),
        )
    )

    rows = pd.read_csv(tmp_path / "diagnostic_rows.csv")
    assert report["summary"]["headline_irr_status"] == "passed"
    assert report["summary"]["rows_disagreement"] == 1
    assert report["summary"]["binary_relevance_reviewed_items"] == 4
    assert report["summary"]["transition_counts"] == {"S->A": 1}
    assert rows["irr_item_id"].tolist() == ["i2"]
