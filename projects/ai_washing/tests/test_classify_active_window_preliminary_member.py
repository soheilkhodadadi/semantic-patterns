from __future__ import annotations

import argparse

import pandas as pd
import pytest

from ai_washing_member.classification.classify_active_window_preliminary import run_classification
from ai_washing_member.classification.train_preliminary_centroids import run_training

pytest.importorskip(
    "pyarrow", reason="pyarrow is required for parquet-backed preliminary classification tests"
)


def test_member_classify_active_window_preliminary_smoke(tmp_path):
    labels_master = tmp_path / "labels_master.parquet"
    split_registry = tmp_path / "split_registry_v1.csv"
    heldout_rows = [
        {"sentence_id": "a1", "sentence": "Actionable alpha sentence", "label": "Actionable"},
        {"sentence_id": "a2", "sentence": "Actionable beta sentence", "label": "Actionable"},
        {"sentence_id": "s1", "sentence": "Speculative alpha sentence", "label": "Speculative"},
        {"sentence_id": "s2", "sentence": "Speculative beta sentence", "label": "Speculative"},
        {"sentence_id": "i1", "sentence": "Irrelevant alpha sentence", "label": "Irrelevant"},
        {"sentence_id": "i2", "sentence": "Irrelevant beta sentence", "label": "Irrelevant"},
        {"sentence_id": "v1", "sentence": "Validation actionable sentence", "label": "Actionable"},
        {
            "sentence_id": "v2",
            "sentence": "Validation speculative sentence",
            "label": "Speculative",
        },
        {"sentence_id": "v3", "sentence": "Validation irrelevant sentence", "label": "Irrelevant"},
    ]
    pd.DataFrame(heldout_rows).to_parquet(labels_master, index=False)
    pd.DataFrame(
        [
            {"sentence_id": "a1", "split": "train", "split_version": "v1", "seed": 20260315},
            {"sentence_id": "a2", "split": "train", "split_version": "v1", "seed": 20260315},
            {"sentence_id": "s1", "split": "train", "split_version": "v1", "seed": 20260315},
            {"sentence_id": "s2", "split": "train", "split_version": "v1", "seed": 20260315},
            {"sentence_id": "i1", "split": "train", "split_version": "v1", "seed": 20260315},
            {"sentence_id": "i2", "split": "train", "split_version": "v1", "seed": 20260315},
            {"sentence_id": "v1", "split": "validation", "split_version": "v1", "seed": 20260315},
            {"sentence_id": "v2", "split": "validation", "split_version": "v1", "seed": 20260315},
            {"sentence_id": "v3", "split": "validation", "split_version": "v1", "seed": 20260315},
        ]
    ).to_csv(split_registry, index=False)

    train_root = tmp_path / "artifacts" / "models" / "mpnet_prelim_v1"
    run_training(
        argparse.Namespace(
            labels_master=str(labels_master),
            split_registry=str(split_registry),
            embeddings_output=str(train_root / "embeddings.parquet"),
            centroids_output=str(train_root / "centroids.json"),
            metadata_output=str(train_root / "metadata.json"),
            model_id="mpnet_prelim_v1",
            source_window_id="active_2021_2024",
            embedding_backend="hash",
            model_name="hash://bow",
            batch_size=8,
            hash_dim=32,
        )
    )

    sentence_root = tmp_path / "processed" / "sentences"
    for year in (2021, 2022):
        year_dir = sentence_root / f"year={year}"
        year_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(
            [
                {
                    "sentence_id": f"{year}_1",
                    "sentence": f"Firm {year} deployed AI tools in production.",
                    "source_year": year,
                    "source_cik": f"{year}001",
                    "source_file": f"{year}_a.txt",
                },
                {
                    "sentence_id": f"{year}_2",
                    "sentence": f"Firm {year} plans future AI capabilities.",
                    "source_year": year,
                    "source_cik": f"{year}002",
                    "source_file": f"{year}_b.txt",
                },
            ]
        ).to_parquet(year_dir / "ai_sentences.parquet", index=False)

    report = run_classification(
        argparse.Namespace(
            input_root=str(sentence_root),
            years=["2021", "2022"],
            centroids=str(train_root / "centroids.json"),
            model_metadata=str(train_root / "metadata.json"),
            selected_model_manifest="",
            output_root=str(tmp_path / "processed" / "classifications"),
            output_report=str(tmp_path / "reports" / "active_window_coverage_prelim_v1.json"),
            model_id="mpnet_prelim_v1",
            source_window_id="active_2021_2024",
        )
    )

    assert report["status"] == "passed"
    assert report["summary"]["completed_year_count"] == 2
