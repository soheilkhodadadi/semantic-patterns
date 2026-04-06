from __future__ import annotations

import argparse
import json

import pandas as pd

from ai_washing_member.classification.benchmark_preliminary_models import run_benchmark
from ai_washing_member.classification.train_binary_relevance_then_as import (
    run_training as run_binary_training,
)
from ai_washing_member.classification.train_logreg_preliminary import (
    run_training as run_logreg_training,
)
from ai_washing_member.classification.train_preliminary_centroids import (
    run_training as run_centroid_training,
)


def _write_labels_and_split(tmp_path):
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
    return labels_master, split_registry


def _train_wave1_models(tmp_path, labels_master, split_registry):
    centroid_root = tmp_path / "artifacts" / "models" / "mpnet_prelim_v1"
    logreg_root = tmp_path / "artifacts" / "models" / "mpnet_logreg_prelim_v1"
    binary_root = tmp_path / "artifacts" / "models" / "binary_relevance_then_as_v1"
    run_centroid_training(
        argparse.Namespace(
            labels_master=str(labels_master),
            split_registry=str(split_registry),
            embeddings_output=str(centroid_root / "embeddings.parquet"),
            centroids_output=str(centroid_root / "centroids.json"),
            metadata_output=str(centroid_root / "metadata.json"),
            model_id="mpnet_prelim_v1",
            source_window_id="active_2021_2024",
            embedding_backend="hash",
            model_name="hash://bow",
            batch_size=8,
            hash_dim=32,
        )
    )
    run_logreg_training(
        argparse.Namespace(
            labels_master=str(labels_master),
            split_registry=str(split_registry),
            model_output=str(logreg_root / "model.pkl"),
            metadata_output=str(logreg_root / "metadata.json"),
            model_id="mpnet_logreg_prelim_v1",
            source_window_id="active_2021_2024",
            embedding_backend="hash",
            model_name="hash://bow",
            batch_size=8,
            hash_dim=32,
            max_iter=500,
            seed=20260315,
        )
    )
    run_binary_training(
        argparse.Namespace(
            labels_master=str(labels_master),
            split_registry=str(split_registry),
            relevance_model_output=str(binary_root / "relevance_model.pkl"),
            actionable_speculative_model_output=str(
                binary_root / "actionable_speculative_model.pkl"
            ),
            metadata_output=str(binary_root / "metadata.json"),
            model_id="binary_relevance_then_as_v1",
            source_window_id="active_2021_2024",
            embedding_backend="hash",
            model_name="hash://bow",
            batch_size=8,
            hash_dim=32,
            max_iter=500,
            seed=20260315,
        )
    )
    return {
        "centroid_metadata": centroid_root / "metadata.json",
        "centroids": centroid_root / "centroids.json",
        "logreg_metadata": logreg_root / "metadata.json",
        "binary_metadata": binary_root / "metadata.json",
    }


def test_member_benchmark_preliminary_models_pending_primary(tmp_path, monkeypatch):
    labels_master, split_registry = _write_labels_and_split(tmp_path)
    paths = _train_wave1_models(tmp_path, labels_master, split_registry)
    historical = tmp_path / "historical.csv"
    boundary = tmp_path / "boundary.csv"
    pd.DataFrame(
        [
            {"sentence": "Actionable historical sentence", "label": "Actionable"},
            {"sentence": "Speculative historical sentence", "label": "Speculative"},
            {"sentence": "Irrelevant historical sentence", "label": "Irrelevant"},
        ]
    ).to_csv(historical, index=False)
    pd.DataFrame(
        [
            {"sentence": "Actionable boundary sentence", "label": "Actionable"},
            {"sentence": "Speculative boundary sentence", "label": "Speculative"},
        ]
    ).to_csv(boundary, index=False)

    def fake_predict(sentences, manifest):
        preds = []
        scores = []
        for sentence in sentences:
            lowered = sentence.lower()
            if "actionable" in lowered:
                pred = "Actionable"
            elif "speculative" in lowered:
                pred = "Speculative"
            else:
                pred = "Irrelevant"
            preds.append(pred)
            mapping = {"Actionable": 0.05, "Speculative": 0.05, "Irrelevant": 0.05}
            mapping[pred] = 0.9
            scores.append(mapping)
        return preds, scores

    monkeypatch.setattr(
        "ai_washing_member.classification.benchmark_preliminary_models.predict_sentences",
        fake_predict,
    )

    report = run_benchmark(
        argparse.Namespace(
            labels_master=str(labels_master),
            split_registry=str(split_registry),
            primary_benchmark=str(tmp_path / "missing_v2.csv"),
            historical_benchmark=str(historical),
            irr_boundary_benchmark=str(boundary),
            centroid_model=str(paths["centroids"]),
            centroid_metadata=str(paths["centroid_metadata"]),
            logreg_metadata=str(paths["logreg_metadata"]),
            binary_metadata=str(paths["binary_metadata"]),
            output_json=str(tmp_path / "reports" / "matrix.json"),
            output_md=str(tmp_path / "reports" / "matrix.md"),
            model_report_dir=str(tmp_path / "reports" / "models"),
            selected_manifest=str(tmp_path / "artifacts" / "selected.json"),
            min_primary_accuracy=0.70,
            min_primary_macro_f1=0.65,
            min_primary_as_accuracy=0.65,
            legacy_tau=0.07,
            legacy_eps_irr=0.03,
            legacy_min_tokens=6,
            legacy_rule_boosts=True,
        )
    )

    assert report["status"] == "pending_primary_benchmark"
    selected = json.loads((tmp_path / "artifacts" / "selected.json").read_text(encoding="utf-8"))
    assert selected["status"] == "pending_primary_benchmark"
