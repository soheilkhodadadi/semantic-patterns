from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.publication_runs.test_20_comment_letter_cleanup import (
    _build_event_sample,
    _paired_diffs,
)


def _panel() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "cik": ["0001"] * 5 + ["0002"] * 5,
            "year": [2018, 2019, 2020, 2021, 2022] * 2,
            "any_ai_talk": [0, 1, 1, 1, 1, 0, 1, 1, 1, 1],
            "SpecShare": [0.05, 0.30, 0.20, 0.10, 0.08, 0.04, 0.25, 0.18, 0.11, 0.09],
            "A_S": [0.4, 0.7, 0.8, 0.9, 1.0, 0.5, 0.8, 0.9, 1.0, 1.1],
            "PatentMismatch": [0, 1, 0, 0, 0, 0, 1, 1, 0, 0],
            "AI_Focus": [0.4, 1.0, 1.1, 1.3, 1.4, 0.3, 0.9, 1.0, 1.2, 1.3],
        }
    )


def _events() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "cik": ["0001", "0002"],
            "year": [2020, 2020],
            "any_comment": [1, 1],
            "ai_comment_broad": [0, 1],
        }
    )


def test_build_event_sample_keeps_active_ai_disclosers() -> None:
    sample, summary = _build_event_sample(_panel(), _events(), "any_comment")
    assert summary["event_firms"] == 2
    assert summary["active_firms"] == 2
    assert sorted(sample["event_time"].unique().tolist()) == [-2, -1, 0, 1, 2]


def test_paired_diffs_reports_expected_direction() -> None:
    sample, _ = _build_event_sample(_panel(), _events(), "any_comment")
    rows, means, block = _paired_diffs(sample, "Panel A")
    keyed = {(row["outcome"], row["event_time"]): row for row in rows}
    assert keyed[("SpecShare", 1)]["coef"] < 0
    assert keyed[("A_S", 1)]["coef"] > 0
    assert not block.empty
    assert means
