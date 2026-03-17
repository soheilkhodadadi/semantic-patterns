from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from semantic_ai_washing.director.tasks.validation_assets import (
    build_validation_asset_registry,
    classify_dataset_relationship,
)


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)


def test_classify_dataset_relationship_detects_historical_duplicate():
    left = pd.DataFrame(
        [
            {"sentence": "AI helps automate workflow.", "label": "Actionable"},
            {"sentence": "We may explore AI later.", "label": "Speculative"},
        ]
    )
    right = pd.DataFrame(
        [
            {"sentence": "AI helps automate workflow", "label": "Actionable"},
            {"sentence": "We may explore AI later.", "label": "Speculative"},
        ]
    )

    relationship = classify_dataset_relationship(left, right)

    assert relationship["relationship"] == "historical_duplicate"
    assert relationship["exact_sentence_label_match"] is True
    assert relationship["normalized_sentence_overlap_count"] == 2


def test_build_validation_asset_registry_writes_expected_roles(tmp_path):
    held_out = tmp_path / "held_out.csv"
    collected = tmp_path / "collected.csv"
    hand_labeled = tmp_path / "hand_labeled.csv"
    output = tmp_path / "reports" / "validation_asset_registry.json"

    _write_csv(
        held_out,
        [
            {"sentence": "AI helps automate workflow.", "label": "Actionable"},
            {"sentence": "We may explore AI later.", "label": "Speculative"},
        ],
    )
    _write_csv(
        collected,
        [
            {"sentence": "AI helps automate workflow", "label": "Actionable"},
            {"sentence": "We may explore AI later.", "label": "Speculative"},
        ],
    )
    _write_csv(
        hand_labeled,
        [
            {
                "sentence": "AI helps automate workflow.",
                "label": "Actionable",
                "embedding": "[0.1, 0.2]",
            }
        ],
    )

    payload = build_validation_asset_registry(
        held_out_path=str(held_out),
        collected_path=str(collected),
        hand_labeled_path=str(hand_labeled),
        output_path=str(output),
        held_out_v2_path=str(tmp_path / "missing_v2.csv"),
        irr_boundary_path=str(tmp_path / "missing_boundary.csv"),
    )

    assert output.exists()
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["assets"]["held_out_sentences"]["role"] == "canonical_frozen_evaluation_set"
    assert (
        saved["assets"]["held_out_sentences_v2"]["role"]
        == "planned_canonical_current_rubric_evaluation_set"
    )
    assert (
        saved["assets"]["collected_ai_sentences_classified_cleaned"]["role"]
        == "historical_duplicate_of_held_out"
    )
    assert (
        saved["assets"]["hand_labeled_with_embeddings_revised"]["role"]
        == "historical_training_seed_with_embeddings"
    )
    assert (
        payload["relationships"]["held_out_vs_collected_cleaned"]["relationship"]
        == "historical_duplicate"
    )


def test_build_validation_asset_registry_v2_roles(tmp_path):
    held_out = tmp_path / "held_out.csv"
    held_out_v2 = tmp_path / "held_out_v2.csv"
    boundary = tmp_path / "irr_boundary.csv"
    collected = tmp_path / "collected.csv"
    hand_labeled = tmp_path / "hand_labeled.csv"
    output = tmp_path / "reports" / "validation_asset_registry_v2.json"

    _write_csv(
        held_out,
        [
            {"sentence": "We deployed AI now.", "label": "Actionable"},
            {"sentence": "We may explore AI later.", "label": "Speculative"},
        ],
    )
    _write_csv(
        held_out_v2,
        [
            {"sentence": "Our AI systems are in production.", "label": "Actionable"},
            {"sentence": "Management plans to expand AI.", "label": "Speculative"},
            {"sentence": "AI market trends are generic.", "label": "Irrelevant"},
        ],
    )
    _write_csv(
        boundary,
        [
            {"sentence": "We are considering AI investments.", "label": "Speculative"},
            {"sentence": "AI regulatory risk is discussed.", "label": "Irrelevant"},
        ],
    )
    _write_csv(
        collected,
        [{"sentence": "Collected sentence.", "label": "Irrelevant"}],
    )
    _write_csv(
        hand_labeled,
        [{"sentence": "Seed sentence.", "label": "Actionable", "embedding": "[0.0]"}],
    )

    payload = build_validation_asset_registry(
        held_out_path=str(held_out),
        held_out_v2_path=str(held_out_v2),
        irr_boundary_path=str(boundary),
        collected_path=str(collected),
        hand_labeled_path=str(hand_labeled),
        output_path=str(output),
    )

    assert payload["assets"]["held_out_sentences"]["role"] == "historical_benchmark_v1"
    assert (
        payload["assets"]["held_out_sentences_v2"]["role"]
        == "canonical_current_rubric_evaluation_set"
    )
    assert payload["assets"]["irr_boundary_benchmark_v1"]["role"] == "boundary_benchmark_v1"
    assert payload["canonical_current_rubric_evaluation_asset"] == str(held_out_v2.resolve())
    assert "held_out_v2_vs_historical_held_out" in payload["relationships"]
    assert "held_out_v2_vs_irr_boundary_benchmark" in payload["relationships"]
