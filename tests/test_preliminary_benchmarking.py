from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import pytest

from semantic_ai_washing.aggregation.build_preliminary_narrative_measures import run_measure_build
from semantic_ai_washing.classification.benchmark_preliminary_models import run_benchmark
from semantic_ai_washing.classification.classify_active_window_preliminary import (
    run_classification,
)
from ai_washing_member.classification.model_runtime import build_centroid_runtime
from semantic_ai_washing.classification.publish_selected_preliminary_eval import run_publish
from semantic_ai_washing.classification.train_binary_relevance_then_as import (
    run_training as run_binary_training,
)
from semantic_ai_washing.classification.train_logreg_preliminary import (
    run_training as run_logreg_training,
)
from ai_washing_member.classification.train_preliminary_centroids import (
    run_training as run_centroid_training,
)

pytest.importorskip("pyarrow", reason="pyarrow is required for parquet-backed preliminary tests")


def _write_labels_and_split(tmp_path: Path) -> tuple[Path, Path]:
    labels_master = tmp_path / "labels_master.parquet"
    split_registry = tmp_path / "split_registry_v1.csv"
    rows = [
        {
            "sentence_id": "a1",
            "sentence": "Actionable alpha sentence",
            "label": "Actionable",
            "source_cik": "1001",
            "source_year": 2024,
        },
        {
            "sentence_id": "a2",
            "sentence": "Actionable beta sentence",
            "label": "Actionable",
            "source_cik": "1002",
            "source_year": 2024,
        },
        {
            "sentence_id": "s1",
            "sentence": "Speculative alpha sentence",
            "label": "Speculative",
            "source_cik": "1003",
            "source_year": 2024,
        },
        {
            "sentence_id": "s2",
            "sentence": "Speculative beta sentence",
            "label": "Speculative",
            "source_cik": "1004",
            "source_year": 2024,
        },
        {
            "sentence_id": "i1",
            "sentence": "Irrelevant alpha sentence",
            "label": "Irrelevant",
            "source_cik": "1005",
            "source_year": 2024,
        },
        {
            "sentence_id": "i2",
            "sentence": "Irrelevant beta sentence",
            "label": "Irrelevant",
            "source_cik": "1006",
            "source_year": 2024,
        },
        {
            "sentence_id": "v1",
            "sentence": "Validation actionable sentence",
            "label": "Actionable",
            "source_cik": "1007",
            "source_year": 2024,
        },
        {
            "sentence_id": "v2",
            "sentence": "Validation speculative sentence",
            "label": "Speculative",
            "source_cik": "1008",
            "source_year": 2024,
        },
        {
            "sentence_id": "v3",
            "sentence": "Validation irrelevant sentence",
            "label": "Irrelevant",
            "source_cik": "1009",
            "source_year": 2024,
        },
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
    return labels_master, split_registry


def _train_wave1_models(
    tmp_path: Path, labels_master: Path, split_registry: Path
) -> dict[str, Path]:
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


def _label_from_sentence(text: str) -> str:
    lowered = text.lower()
    if "actionable" in lowered:
        return "Actionable"
    if "speculative" in lowered:
        return "Speculative"
    return "Irrelevant"


def test_train_wave1_models_hash_backend(tmp_path):
    labels_master, split_registry = _write_labels_and_split(tmp_path)
    paths = _train_wave1_models(tmp_path, labels_master, split_registry)

    centroid_meta = json.loads(paths["centroid_metadata"].read_text(encoding="utf-8"))
    logreg_meta = json.loads(paths["logreg_metadata"].read_text(encoding="utf-8"))
    binary_meta = json.loads(paths["binary_metadata"].read_text(encoding="utf-8"))

    assert centroid_meta["model_type"] == "centroid_multiclass"
    assert logreg_meta["model_type"] == "logreg_multiclass"
    assert binary_meta["model_type"] == "binary_relevance_then_as"
    assert logreg_meta["summary"]["rows_train"] == 6
    assert binary_meta["summary"]["rows_validation_reserved"] == 3


def test_run_benchmark_pending_primary_when_heldout_v2_missing(tmp_path, monkeypatch):
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
        preds = [_label_from_sentence(sentence) for sentence in sentences]
        scores = [{"Actionable": 0.9, "Speculative": 0.05, "Irrelevant": 0.05} for _ in sentences]
        return preds, scores

    monkeypatch.setattr(
        "semantic_ai_washing.classification.benchmark_preliminary_models.predict_sentences",
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
    assert report["summary"]["primary_benchmark_available"] is False


def test_run_benchmark_selects_winner_and_selected_manifest_drives_classification(
    tmp_path, monkeypatch
):
    labels_master, split_registry = _write_labels_and_split(tmp_path)
    paths = _train_wave1_models(tmp_path, labels_master, split_registry)
    historical = tmp_path / "historical.csv"
    boundary = tmp_path / "boundary.csv"
    held_out_v2 = tmp_path / "held_out_v2.csv"
    for path in (historical, boundary, held_out_v2):
        pd.DataFrame(
            [
                {"sentence": "Actionable benchmark sentence", "label": "Actionable"},
                {"sentence": "Speculative benchmark sentence", "label": "Speculative"},
                {"sentence": "Irrelevant benchmark sentence", "label": "Irrelevant"},
            ]
        ).to_csv(path, index=False)

    def fake_predict(sentences, manifest):
        truth = [_label_from_sentence(sentence) for sentence in sentences]
        model_id = manifest["model_id"]
        if model_id == "mpnet_logreg_prelim_v1":
            preds = truth
        elif model_id == "binary_relevance_then_as_v1":
            preds = ["Irrelevant" if label == "Speculative" else label for label in truth]
        elif model_id == "legacy_two_stage_mpnet_rules":
            preds = ["Irrelevant" for _ in truth]
        else:
            preds = ["Speculative" if label == "Actionable" else label for label in truth]
        scores = []
        for pred in preds:
            mapping = {"Actionable": 0.05, "Speculative": 0.05, "Irrelevant": 0.05}
            mapping[pred] = 0.9
            scores.append(mapping)
        return preds, scores

    monkeypatch.setattr(
        "semantic_ai_washing.classification.benchmark_preliminary_models.predict_sentences",
        fake_predict,
    )

    benchmark_report = run_benchmark(
        argparse.Namespace(
            labels_master=str(labels_master),
            split_registry=str(split_registry),
            primary_benchmark=str(held_out_v2),
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
    assert benchmark_report["status"] == "selected"
    selected = json.loads((tmp_path / "artifacts" / "selected.json").read_text(encoding="utf-8"))
    assert selected["winner"]["model_id"] == "mpnet_logreg_prelim_v1"

    publish_report = run_publish(
        argparse.Namespace(
            selected_manifest=str(tmp_path / "artifacts" / "selected.json"),
            benchmark_matrix=str(tmp_path / "reports" / "matrix.json"),
            output_report=str(tmp_path / "reports" / "selected_eval.json"),
            accuracy_threshold=0.80,
        )
    )
    assert publish_report["status"] == "passed"
    assert publish_report["summary"]["accuracy"] == 1.0

    sentence_root = tmp_path / "processed" / "sentences"
    for year in (2021, 2022, 2023, 2024):
        year_dir = sentence_root / f"year={year}"
        year_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(
            [
                {
                    "sentence_id": f"{year}_1",
                    "sentence": "Actionable production sentence",
                    "source_year": year,
                    "source_cik": f"{year}001",
                    "source_file": f"{year}_a.txt",
                },
                {
                    "sentence_id": f"{year}_2",
                    "sentence": "Speculative roadmap sentence",
                    "source_year": year,
                    "source_cik": f"{year}002",
                    "source_file": f"{year}_b.txt",
                },
            ]
        ).to_parquet(year_dir / "ai_sentences.parquet", index=False)

    runtime_winner = build_centroid_runtime(
        metadata_path=paths["centroid_metadata"],
        centroids_path=paths["centroids"],
    )
    selected_runtime_path = tmp_path / "artifacts" / "selected_runtime.json"
    selected_runtime_path.parent.mkdir(parents=True, exist_ok=True)
    selected_runtime_path.write_text(
        json.dumps(
            {
                "status": "selected",
                "source_window_id": "active_2021_2024",
                "winner": runtime_winner,
                "benchmark_matrix": str(tmp_path / "reports" / "matrix.json"),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    classify_report = run_classification(
        argparse.Namespace(
            input_root=str(sentence_root),
            years=["2021", "2022", "2023", "2024"],
            centroids=str(paths["centroids"]),
            model_metadata=str(paths["centroid_metadata"]),
            selected_model_manifest=str(selected_runtime_path),
            output_root=str(tmp_path / "processed" / "classifications"),
            output_report=str(tmp_path / "reports" / "coverage.json"),
            model_id="prelim_selected_model_v1",
            source_window_id="active_2021_2024",
        )
    )
    assert classify_report["summary"]["model_id"] == "prelim_selected_model_v1"
    assert classify_report["summary"]["selected_model_id"] == "mpnet_prelim_v1"

    measure_report = run_measure_build(
        argparse.Namespace(
            input_root=str(tmp_path / "processed" / "classifications"),
            years=["2021", "2022", "2023", "2024"],
            model_id="prelim_selected_model_v1",
            source_window_id="active_2021_2024",
            selected_model_manifest=str(selected_runtime_path),
            output_ai_metrics=str(tmp_path / "processed" / "aggregates" / "ai_metrics.parquet"),
            output_measures=str(tmp_path / "processed" / "aggregates" / "measures.parquet"),
            output_report=str(tmp_path / "reports" / "measures.json"),
        )
    )
    assert measure_report["summary"]["selected_model_id"] == "mpnet_prelim_v1"
    assert measure_report["summary"]["named_measures_complete"] is True
