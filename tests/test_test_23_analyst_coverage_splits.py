from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.publication_runs.test_23_analyst_coverage_splits import (
    _prepare_sample,
)


def test_prepare_sample_builds_expected_coverage_slices() -> None:
    panel = pd.DataFrame(
        {
            "cik": ["0001", "0002", "0003", "0004"],
            "ticker": ["A", "B", "C", "D"],
            "year": [2020, 2020, 2020, 2020],
            "any_ai_talk": [1, 1, 1, 1],
            "PatentMismatch": [1, 0, 1, 0],
            "AI_Focus": [1.0, 1.1, 0.9, 0.8],
            "ln_assets": [2.0, 2.1, 1.9, 1.8],
            "leverage": [0.2, 0.3, 0.2, 0.1],
            "cash": [0.1, 0.1, 0.2, 0.3],
            "roa": [0.05, 0.04, 0.03, 0.02],
            "log_patents_ai_lead1": [0.0, 0.2, 0.3, 0.1],
            "PatentMismatch_lead1": [1, 0, 0, 1],
            "roa_lead2": [0.04, 0.03, 0.02, 0.01],
            "sic2": [35, 35, 36, 36],
        }
    )
    coverage = pd.DataFrame(
        {
            "ticker": ["A", "B", "C", "D"],
            "year": [2020, 2020, 2020, 2020],
            "log_analyst_coverage_t": [0.7, 1.0, 2.0, 3.0],
            "numest": [1, 2, 7, 15],
            "statpers": pd.to_datetime(["2020-12-15"] * 4),
        }
    )
    merged, summary = _prepare_sample(panel, coverage)
    assert summary["coverage_nonmissing"] == 4
    row_a = merged.loc[merged["ticker"].eq("A")].iloc[0]
    row_d = merged.loc[merged["ticker"].eq("D")].iloc[0]
    assert row_a["BottomQuartile"] == 1
    assert row_a["LowerHalf"] == 1
    assert row_d["UpperHalf"] == 1
    assert row_d["TopQuartile"] == 1
