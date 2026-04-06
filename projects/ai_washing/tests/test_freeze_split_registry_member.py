from __future__ import annotations

import argparse

import pandas as pd

from ai_washing_member.labeling.freeze_split_registry import run_freeze


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


def test_freeze_split_registry_member_produces_grouped_validation_slice(tmp_path):
    labels_master_path = tmp_path / "labels_master.parquet"
    held_out_path = tmp_path / "held_out.csv"
    output_csv = tmp_path / "split_registry_v1.csv"
    output_json = tmp_path / "split_registry_v1.json"

    pd.DataFrame(_labels_master_rows()).to_parquet(labels_master_path, index=False)
    pd.DataFrame([{"sentence": "held out sentence"}]).to_csv(held_out_path, index=False)

    payload = run_freeze(
        argparse.Namespace(
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
    )

    registry = pd.read_csv(output_csv)

    assert payload["status"] == "frozen"
    assert payload["summary"]["validation_row_count"] == 6
    assert registry.groupby("source_cik")["split"].nunique().eq(1).all()
