from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.publication_runs.test_30_capital_raising_timing import (
    _build_table,
    _prepare_event_sample,
)


def test_prepare_event_sample_keeps_first_issue_and_active_ai_window() -> None:
    panel = pd.DataFrame(
        {
            "cik": ["1", "1", "1", "1", "2", "2", "2", "2"],
            "permno": [10, 10, 10, 10, 20, 20, 20, 20],
            "year": [2020, 2021, 2022, 2023, 2020, 2021, 2022, 2023],
            "any_ai_talk": [1, 1, 1, 1, 0, 1, 0, 1],
            "LowCredibility": [0, 1, 1, 0, 0, 0, 0, 0],
            "ApplicationMismatch": [0, 1, 1, 0, 0, 0, 0, 0],
            "PatentMismatch": [0, 1, 1, 0, 0, 0, 0, 0],
            "SpecShare": [0.1, 0.3, 0.2, 0.1, 0.0, 0.1, 0.0, 0.2],
            "AI_Focus": [1.0, 2.0, 2.1, 1.8, 0.0, 0.5, 0.0, 0.6],
            "market_cap_year_end": [10, 11, 12, 13, 5, 6, 7, 8],
            "nonbig_year": [False, False, False, False, True, True, True, True],
            "shrout": [100, 120, 140, 140, 100, 100, 120, 120],
            "share_growth_lead1": [0.2, 0.1667, 0.0, None, 0.0, 0.2, 0.0, None],
            "equity_issue_lead1": [1.0, 1.0, 0.0, None, 0.0, 1.0, 0.0, None],
        }
    )
    sample, summary = _prepare_event_sample(panel)
    assert summary["issue_event_firms"] == 2
    assert summary["active_ai_issue_firms"] == 1
    assert sample["cik"].nunique() == 1
    assert sample["cik"].iloc[0] == "1"


def test_build_table_adds_panel_header_rows() -> None:
    frame_a = pd.DataFrame(
        [
            {
                "Panel": "Panel A. Test panel",
                "Outcome": "PatentMismatch",
                "Event year vs. t-1": "0.1000** (0.0400)",
                "t+1 vs. event year": "-0.0500* (0.0300)",
                "t+2 vs. event year": "-0.0400 (0.0300)",
                "Event-year mean": "0.3000",
                "N firms": "100",
            }
        ]
    )
    frame_b = pd.DataFrame(
        [
            {
                "Panel": "Panel B. Test panel",
                "Outcome": "PatentMismatch",
                "Event year vs. t-1": "0.0800** (0.0300)",
                "t+1 vs. event year": "-0.0400* (0.0200)",
                "t+2 vs. event year": "-0.0300 (0.0200)",
                "Event-year mean": "0.2500",
                "N firms": "80",
            }
        ]
    )
    table_df = _build_table([frame_a, frame_b])
    assert table_df.iloc[0]["Panel"].startswith("Panel A")
    assert any(str(value).startswith("Panel B") for value in table_df["Panel"])
