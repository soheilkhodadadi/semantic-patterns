import hashlib

import pandas as pd

from semantic_ai_washing.diagnostics.phase0_baseline import (
    build_failure_taxonomy,
    evaluate_coverage,
    flag_distribution_pathologies,
    read_centroid_metadata,
)
from semantic_ai_washing.tests.evaluate_classifier_on_held_out import (
    build_confusion_matrix_df,
    compute_metrics_dict,
)


def test_metrics_and_confusion_matrix_for_toy_labels():
    true_labels = ["Actionable", "Speculative", "Irrelevant", "Actionable"]
    pred_labels = ["Actionable", "Actionable", "Irrelevant", "Speculative"]

    metrics = compute_metrics_dict(true_labels, pred_labels)
    confusion = build_confusion_matrix_df(true_labels, pred_labels)

    assert metrics["total"] == 4
    assert metrics["correct"] == 2
    assert metrics["accuracy"] == 0.5
    assert confusion.loc["Actionable", "Actionable"] == 1
    assert confusion.loc["Actionable", "Speculative"] == 1
    assert confusion.loc["Irrelevant", "Irrelevant"] == 1


def test_failure_taxonomy_counts_expected_transitions():
    details = pd.DataFrame(
        [
            {"true_label": "Actionable", "predicted_label": "Speculative"},
            {"true_label": "Actionable", "predicted_label": "Irrelevant"},
            {"true_label": "Speculative", "predicted_label": "Actionable"},
            {"true_label": "Irrelevant", "predicted_label": "Speculative"},
            {"true_label": "Actionable", "predicted_label": "Actionable"},
        ]
    )

    taxonomy = build_failure_taxonomy(details)
    counts = {row["transition"]: int(row["count"]) for _, row in taxonomy.iterrows()}

    assert counts["A->S"] == 1
    assert counts["A->I"] == 1
    assert counts["S->A"] == 1
    assert counts["S->I"] == 0
    assert counts["I->A"] == 0
    assert counts["I->S"] == 1


def test_distribution_pathology_flagging_thresholds():
    reasons = flag_distribution_pathologies(0.01, 0.0, 0.99)
    assert "I_share>=0.99" in reasons
    assert "single_class_share>=0.95" in reasons

    normal = flag_distribution_pathologies(0.40, 0.30, 0.30)
    assert normal == []


def test_coverage_checker_detects_mismatch():
    expected = ["a.csv", "b.csv", "c.csv"]
    existing = ["a.csv", "c.csv"]

    coverage = evaluate_coverage(expected, existing)

    assert coverage["expected_count"] == 3
    assert coverage["existing_count"] == 2
    assert coverage["mismatch_count"] == 1
    assert coverage["missing_outputs"] == ["b.csv"]


def test_read_centroid_metadata_returns_hash(tmp_path):
    centroid_file = tmp_path / "centroids_mpnet.json"
    centroid_file.write_text('{"Actionable":[1.0]}', encoding="utf-8")

    metadata = read_centroid_metadata(centroid_file)
    expected_hash = hashlib.sha256(b'{"Actionable":[1.0]}').hexdigest()

    assert metadata["exists"] is True
    assert metadata["path"].endswith("centroids_mpnet.json")
    assert metadata["sha256"] == expected_hash
    assert metadata["size_bytes"] > 0
