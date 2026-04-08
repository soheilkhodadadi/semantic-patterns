from __future__ import annotations

from semantic_ai_washing.classification.build_reviewed_boundary_pack import (
    build_reviewed_boundary_pack,
)


def test_build_reviewed_boundary_pack_merges_existing_and_remaining_labels(
    tmp_path,
) -> None:
    audit_csv = tmp_path / "audit.csv"
    audit_csv.write_text(
        "\n".join(
            [
                "row_id,source,case_kind,priority,sentence,failure_mode_primary,failure_mode_note,label_reference,label_other",
                '1,irr,human,highest,"Current AI use.",current_capability_or_enabled_use,"note",Actionable,Speculative',
                '2,heldout,error,high,"We plan to invest in AI.",future_intent_or_expectation,"note",Speculative,Actionable',
            ]
        ),
        encoding="utf-8",
    )

    existing_csv = tmp_path / "existing.csv"
    existing_csv.write_text(
        "\n".join(
            [
                "row_id,revised_label",
                "1,Actionable",
            ]
        ),
        encoding="utf-8",
    )

    remaining_csv = tmp_path / "remaining.csv"
    remaining_csv.write_text(
        "\n".join(
            [
                "row_id,reviewed_label,reviewed_rationale",
                '2,Speculative,"Future-oriented investment statement."',
            ]
        ),
        encoding="utf-8",
    )

    output_csv = tmp_path / "reviewed.csv"
    output_blinded_csv = tmp_path / "reviewed_blinded.csv"

    summary = build_reviewed_boundary_pack(
        tagged_audit_csv=audit_csv,
        existing_benchmark_csv=existing_csv,
        remaining_labels_csv=remaining_csv,
        output_csv=output_csv,
        output_blinded_csv=output_blinded_csv,
    )

    assert summary["status"] == "passed"
    assert summary["row_count"] == 2
    assert summary["reviewed_label_counts"] == {
        "Actionable": 1,
        "Speculative": 1,
    }
    assert output_csv.exists()
    assert output_blinded_csv.exists()
