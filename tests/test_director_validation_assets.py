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
    )

    assert output.exists()
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["assets"]["held_out_sentences"]["role"] == "canonical_frozen_evaluation_set"
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
