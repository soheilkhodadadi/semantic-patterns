from __future__ import annotations

import argparse
import json

import pandas as pd

from ai_washing_member.classification import (
    reconcile_preliminary_classification_report as member_reconcile,
)


def _write_classified_year(root, *, year: int, model_id: str, rows: int) -> None:
    output_path = root / f"year={year}" / f"model={model_id}" / "classified_sentences.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "sentence_id": f"{year}-{idx}",
                "predicted_label": "Actionable",
                "source_year": year,
            }
            for idx in range(rows)
        ]
    ).to_parquet(output_path, index=False)


def test_member_reconcile_preliminary_classification_report_smoke(tmp_path, monkeypatch):
    input_root = tmp_path / "sentences"
    output_root = tmp_path / "classifications"
    model_id = "binary_relevance_then_as_v1"

    for year, rows in ((2021, 3), (2022, 2)):
        input_year = input_root / f"year={year}"
        input_year.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(
            [
                {"sentence_id": f"{year}-{idx}", "sentence": "Example sentence"}
                for idx in range(rows)
            ]
        ).to_parquet(input_year / "ai_sentences.parquet", index=False)
        _write_classified_year(output_root, year=year, model_id=model_id, rows=rows)

    selected_manifest = tmp_path / "selected_manifest.json"
    selected_manifest.write_text(
        json.dumps({"status": "selected", "model_id": model_id}, indent=2),
        encoding="utf-8",
    )
    metadata_path = tmp_path / "metadata.json"
    metadata_path.write_text(json.dumps({"model_id": model_id}, indent=2), encoding="utf-8")
    centroids_path = tmp_path / "centroids.json"
    centroids_path.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(
        member_reconcile,
        "_resolve_runtime",
        lambda args: (
            {"model_id": model_id},
            {"status": "selected", "model_id": model_id},
            model_id,
            "active_2021_2024",
        ),
    )

    report = member_reconcile.reconcile_outputs(
        argparse.Namespace(
            input_root=str(input_root),
            years=["2021", "2022"],
            centroids=str(centroids_path),
            model_metadata=str(metadata_path),
            selected_model_manifest=str(selected_manifest),
            output_root=str(output_root),
            output_report=str(tmp_path / "coverage.json"),
            progress_report=str(tmp_path / "coverage_progress.json"),
            model_id=model_id,
            source_window_id="active_2021_2024",
            chunk_size=256,
        )
    )

    assert report["status"] == "passed"
    assert report["summary"]["years_completed"] == [2021, 2022]
    assert report["summary"]["total_rows"] == 5
