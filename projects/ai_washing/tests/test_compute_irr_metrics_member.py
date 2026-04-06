from __future__ import annotations

import argparse
import json

import pandas as pd

from ai_washing_member.labeling.compute_irr_metrics import run_metrics


def test_run_metrics_pending_rater2(tmp_path) -> None:
    master_path = tmp_path / "master.csv"
    pd.DataFrame(
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
        ]
    ).to_csv(master_path, index=False)

    (tmp_path / "sampling.json").write_text(
        json.dumps(
            {"summary": {"stratified_100_firms_min": True, "industry_year_balanced": True}}
        ),
        encoding="utf-8",
    )
    (tmp_path / "attestation.json").write_text(
        json.dumps({"human_human_only": True, "third_adjudicator_used": False}),
        encoding="utf-8",
    )

    report, status, code = run_metrics(
        argparse.Namespace(
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
    )

    assert code == 0
    assert status["status"] == "pending_rater2"
    assert report["summary"]["reviewed_items"] == 0
    assert report["summary"]["human_human_only"] is True
