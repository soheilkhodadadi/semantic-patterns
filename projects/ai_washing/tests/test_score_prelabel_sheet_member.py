from __future__ import annotations

import pandas as pd

from ai_washing_member.labeling.score_prelabel_sheet import score_prelabel_sheet


def test_score_prelabel_sheet_member_tolerates_missing_source_section(tmp_path) -> None:
    benchmark_csv = tmp_path / "benchmark.csv"
    assistive_csv = tmp_path / "assistive.csv"

    pd.DataFrame(
        [
            {"sentence_id": "s1", "sentence": "Current AI use.", "label": "Actionable"},
            {"sentence_id": "s2", "sentence": "Future AI plan.", "label": "Speculative"},
        ]
    ).to_csv(benchmark_csv, index=False)

    pd.DataFrame(
        [
            {
                "sentence_id": "s1",
                "sentence": "Current AI use.",
                "assistive_label": "Actionable",
                "assistive_confidence": "high",
                "assistive_rationale": "Present factual use.",
            },
            {
                "sentence_id": "s2",
                "sentence": "Future AI plan.",
                "assistive_label": "Speculative",
                "assistive_confidence": "high",
                "assistive_rationale": "Future-facing claim.",
            },
        ]
    ).to_csv(assistive_csv, index=False)

    payload = score_prelabel_sheet(
        benchmark_csv=str(benchmark_csv),
        assistive_csv=str(assistive_csv),
    )

    assert payload["score"]["overall"]["matches"] == 2
    assert payload["score"]["overall"]["total"] == 2
