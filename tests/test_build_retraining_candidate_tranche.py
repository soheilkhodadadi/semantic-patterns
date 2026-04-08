from __future__ import annotations

import pandas as pd

from semantic_ai_washing.classification.build_retraining_candidate_tranche import (
    build_retraining_candidate_tranche,
)


def test_build_retraining_candidate_tranche_updates_only_training_eligible_rows(
    tmp_path,
) -> None:
    labels_master = pd.DataFrame(
        [
            {
                "sentence_id": "s1",
                "sentence": "Current AI workflow use.",
                "label": "Actionable",
                "batch_id": "b1",
                "batch_row_id": "r1",
                "source_cik": "1001",
                "source_year": 2024,
            },
            {
                "sentence_id": "s2",
                "sentence": "We may invest in AI later.",
                "label": "Actionable",
                "batch_id": "b1",
                "batch_row_id": "r2",
                "source_cik": "1002",
                "source_year": 2024,
            },
        ]
    )
    labels_master_path = tmp_path / "labels_master.parquet"
    labels_master.to_parquet(labels_master_path, index=False)

    split_registry = pd.DataFrame(
        [
            {"sentence_id": "s1", "split": "train"},
            {"sentence_id": "s2", "split": "validation"},
        ]
    )
    split_registry_path = tmp_path / "split_registry.csv"
    split_registry.to_csv(split_registry_path, index=False)

    reviewed = pd.DataFrame(
        [
            {
                "row_id": 1,
                "source": "irr",
                "case_kind": "human_human_as_disagreement",
                "sentence": "Current AI workflow use.",
                "reviewed_label": "Actionable",
                "reviewed_rationale": "Still actionable.",
            },
            {
                "row_id": 2,
                "source": "irr",
                "case_kind": "human_human_as_disagreement",
                "sentence": "We may invest in AI later.",
                "reviewed_label": "Speculative",
                "reviewed_rationale": "Future-oriented.",
            },
            {
                "row_id": 3,
                "source": "heldout",
                "case_kind": "heldout_model_as_error",
                "sentence": "Competitors may use AI better than us.",
                "reviewed_label": "Irrelevant",
                "reviewed_rationale": "Benchmark-only risk row.",
            },
        ]
    )
    reviewed_path = tmp_path / "reviewed.csv"
    reviewed.to_csv(reviewed_path, index=False)

    tranche_csv = tmp_path / "tranche.csv"
    updated_parquet = tmp_path / "updated.parquet"
    updated_review_csv = tmp_path / "updated_review.csv"

    summary = build_retraining_candidate_tranche(
        labels_master_path=labels_master_path,
        split_registry_path=split_registry_path,
        reviewed_boundary_pack_csv=reviewed_path,
        output_tranche_csv=tranche_csv,
        output_labels_master_parquet=updated_parquet,
        output_labels_master_review_csv=updated_review_csv,
    )

    assert summary["status"] == "passed"
    assert summary["reviewed_boundary_rows"] == 3
    assert summary["training_eligible_rows"] == 2
    assert summary["benchmark_only_rows"] == 1
    assert summary["label_update_rows"] == 1

    updated = pd.read_parquet(updated_parquet)
    updated_map = dict(zip(updated["sentence_id"], updated["label"]))
    assert updated_map["s1"] == "Actionable"
    assert updated_map["s2"] == "Speculative"
