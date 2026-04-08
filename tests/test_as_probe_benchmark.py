from __future__ import annotations

import csv

from semantic_ai_washing.classification.build_as_probe_benchmark import (
    build_as_probe_benchmark,
)


def test_build_as_probe_benchmark_quotes_sentences_and_builds_blinded_slice(
    tmp_path,
) -> None:
    revised_csv = tmp_path / "revised.csv"
    revised_csv.write_text(
        "\n".join(
            [
                "row_id,sentence,label_reference,revised_label,relevance_precondition,currentness_gate,business_claim_gate",
                '2,"We use AI, ML, and robotics today.",Actionable,Actionable,True,True,True',
                '7,"We intend to invest in AI next year.",Speculative,Speculative,True,False,False',
            ]
        ),
        encoding="utf-8",
    )

    output_csv = tmp_path / "benchmark.csv"
    output_blinded_csv = tmp_path / "benchmark_blinded.csv"

    summary = build_as_probe_benchmark(
        revised_labels_csv=revised_csv,
        output_csv=output_csv,
        output_blinded_csv=output_blinded_csv,
    )

    assert summary["status"] == "passed"
    assert summary["row_count"] == 2
    assert summary["revised_label_counts"] == {
        "Actionable": 1,
        "Speculative": 1,
    }

    with output_csv.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["row_id"] == "2"
    assert rows[0]["sentence"] == "We use AI, ML, and robotics today."
    assert rows[0]["benchmark_role"] == "fixed_as_probe_v2"

    with output_blinded_csv.open(newline="", encoding="utf-8") as handle:
        blinded_rows = list(csv.DictReader(handle))
    assert blinded_rows[0] == {
        "row_id": "2",
        "sentence": "We use AI, ML, and robotics today.",
        "benchmark_role": "fixed_as_probe_v2_blinded",
    }
