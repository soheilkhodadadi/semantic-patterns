from __future__ import annotations

from semantic_ai_washing.classification.score_as_probe_variant import (
    score_as_probe_variant,
)


def test_score_as_probe_variant_reports_accuracy_and_mismatches(tmp_path) -> None:
    benchmark_csv = tmp_path / "benchmark.csv"
    benchmark_csv.write_text(
        "\n".join(
            [
                "row_id,sentence,revised_label",
                '1,"Current AI use in workflow.",Actionable',
                '2,"We plan to invest in AI.",Speculative',
            ]
        ),
        encoding="utf-8",
    )

    variant_csv = tmp_path / "variant.csv"
    variant_csv.write_text(
        "\n".join(
            [
                "row_id,predicted_label,variant_id,short_rationale",
                '1,Actionable,variant_a,"Current operating claim, already deployed."',
                '2,Irrelevant,variant_a,No current business claim.',
            ]
        ),
        encoding="utf-8",
    )

    summary = score_as_probe_variant(
        benchmark_csv=benchmark_csv,
        variant_csv=variant_csv,
    )

    assert summary["status"] == "passed"
    assert summary["variant_id"] == "variant_a"
    assert summary["row_count"] == 2
    assert summary["match_count"] == 1
    assert summary["mismatch_count"] == 1
    assert summary["accuracy"] == 0.5
    assert summary["transition_counts"] == {
        "Actionable->Actionable": 1,
        "Speculative->Irrelevant": 1,
    }
    assert summary["mismatch_rows"][0]["row_id"] == "2"
