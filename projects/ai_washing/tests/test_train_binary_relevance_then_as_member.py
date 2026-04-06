from __future__ import annotations

import argparse

import pandas as pd

from ai_washing_member.classification.train_binary_relevance_then_as import run_training


def test_member_train_binary_relevance_then_as_smoke(tmp_path):
    labels_master = tmp_path / "labels_master.parquet"
    split_registry = tmp_path / "split_registry_v1.csv"
    pd.DataFrame(
        [
            {"sentence_id": "a1", "sentence": "Actionable alpha", "label": "Actionable"},
            {"sentence_id": "a2", "sentence": "Actionable beta", "label": "Actionable"},
            {"sentence_id": "s1", "sentence": "Speculative alpha", "label": "Speculative"},
            {"sentence_id": "s2", "sentence": "Speculative beta", "label": "Speculative"},
            {"sentence_id": "i1", "sentence": "Irrelevant alpha", "label": "Irrelevant"},
            {"sentence_id": "i2", "sentence": "Irrelevant beta", "label": "Irrelevant"},
            {"sentence_id": "v1", "sentence": "Validation actionable", "label": "Actionable"},
            {"sentence_id": "v2", "sentence": "Validation speculative", "label": "Speculative"},
            {"sentence_id": "v3", "sentence": "Validation irrelevant", "label": "Irrelevant"},
        ]
    ).to_parquet(labels_master, index=False)
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

    metadata = run_training(
        argparse.Namespace(
            labels_master=str(labels_master),
            split_registry=str(split_registry),
            relevance_model_output=str(tmp_path / "artifacts" / "relevance_model.pkl"),
            actionable_speculative_model_output=str(tmp_path / "artifacts" / "as_model.pkl"),
            metadata_output=str(tmp_path / "artifacts" / "metadata.json"),
            model_id="member-binary-test",
            source_window_id="active_2021_2024",
            embedding_backend="hash",
            model_name="hash://bow",
            batch_size=8,
            hash_dim=32,
            max_iter=500,
            seed=20260315,
        )
    )

    assert metadata["status"] == "trained"
    assert metadata["model_type"] == "binary_relevance_then_as"
    assert metadata["summary"]["rows_train"] == 6
