from __future__ import annotations

import argparse
import json

import pandas as pd

from ai_washing_member.labeling.prepare_irr_subset import run_prepare


def test_run_prepare_writes_subset_and_blinded_handoff(tmp_path) -> None:
    input_path = tmp_path / "labels_master_review.csv"
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
    pd.DataFrame(rows).to_csv(input_path, index=False)

    report = run_prepare(
        argparse.Namespace(
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
    )

    subset = pd.read_parquet(tmp_path / "irr_subset.parquet")
    blinded = pd.read_csv(tmp_path / "irr_subset_rater2_blinded.csv")
    attestation = json.loads((tmp_path / "reports" / "irr_attestation.json").read_text())

    assert len(subset) == 120
    assert report["summary"]["rows_selected"] == 120
    assert report["summary"]["unique_firms"] >= 100
    assert report["summary"]["stratified_100_firms_min"] is True
    assert list(blinded.columns) == ["irr_item_id", "sentence", "rater2_label", "rater2_note"]
    assert attestation["blind_mode"] == "text_only"
