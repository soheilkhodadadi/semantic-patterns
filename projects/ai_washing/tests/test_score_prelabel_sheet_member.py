from __future__ import annotations

import pandas as pd

from ai_washing_member.labeling.score_prelabel_sheet import score_prelabel_sheet


def test_score_prelabel_sheet_member_reports_raw_and_eligible_scores(tmp_path) -> None:
    benchmark_csv = tmp_path / "benchmark.csv"
    assistive_csv = tmp_path / "assistive.csv"

    pd.DataFrame(
        [
            {"sentence_id": "s1", "label": "Actionable"},
            {"sentence_id": "s2", "label": "Irrelevant"},
            {"sentence_id": "s3", "label": "Irrelevant"},
        ]
    ).to_csv(benchmark_csv, index=False)
    pd.DataFrame(
        [
            {
                "sentence_id": "s1",
                "assistive_label": "Actionable",
                "assistive_confidence": "high",
                "assistive_rationale": "fact",
                "source_section": "item_1_business",
                "sentence": "We offer AI-enabled services.",
                "prelabel_eligible": True,
                "skip_reason": "",
            },
            {
                "sentence_id": "s2",
                "assistive_label": "",
                "assistive_confidence": "",
                "assistive_rationale": "",
                "source_section": "other",
                "sentence": "",
                "prelabel_eligible": False,
                "skip_reason": "unmatched_noise",
            },
            {
                "sentence_id": "s3",
                "assistive_label": "Speculative",
                "assistive_confidence": "medium",
                "assistive_rationale": "future",
                "source_section": "item_1_business",
                "sentence": "We may find opportunities with AI.",
                "prelabel_eligible": True,
                "skip_reason": "",
            },
        ]
    ).to_csv(assistive_csv, index=False)

    payload = score_prelabel_sheet(
        benchmark_csv=str(benchmark_csv),
        assistive_csv=str(assistive_csv),
    )

    assert payload["score"]["gate_basis"] == "eligible"
    assert payload["score"]["raw_overall"] == {"matches": 1, "total": 3}
    assert payload["score"]["eligible_overall"] == {"matches": 1, "total": 2}
    assert payload["score"]["overall"] == {"matches": 1, "total": 2}
    assert payload["score"]["excluded_from_gate"]["count"] == 1
