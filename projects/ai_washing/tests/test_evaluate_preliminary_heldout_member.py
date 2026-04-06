from __future__ import annotations

import argparse

import pandas as pd
import pytest

from ai_washing_member.classification.evaluate_preliminary_heldout import run_evaluation
from ai_washing_member.classification.train_preliminary_centroids import run_training

pytest.importorskip(
    "pyarrow", reason="pyarrow is required for parquet-backed preliminary evaluation tests"
)


def test_member_evaluate_preliminary_heldout_smoke(tmp_path):
    labels_master = tmp_path / "labels_master.parquet"
    split_registry = tmp_path / "split_registry_v1.csv"
    held_out = tmp_path / "held_out_sentences.csv"
    rows = [
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
    pd.DataFrame(rows).to_parquet(labels_master, index=False)
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
    pd.DataFrame(
        [
            {"sentence": "Actionable alpha sentence", "label": "Actionable"},
            {"sentence": "Speculative alpha sentence", "label": "Speculative"},
            {"sentence": "Irrelevant alpha sentence", "label": "Irrelevant"},
        ]
    ).to_csv(held_out, index=False)

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

    report = run_evaluation(
        argparse.Namespace(
            held_out=str(held_out),
            labels_master=str(labels_master),
            centroids=str(train_root / "centroids.json"),
            model_metadata=str(train_root / "metadata.json"),
            selected_model_manifest="",
            output_report=str(tmp_path / "reports" / "heldout_eval_prelim_v1.json"),
            model_id="mpnet_prelim_v1",
            source_window_id="active_2021_2024",
            embedding_backend="hash",
            model_name="hash://bow",
            batch_size=8,
            hash_dim=32,
            accuracy_threshold=0.8,
        )
    )

    assert report["status"] == "passed"
    assert report["summary"]["leakage_detected"] is False
