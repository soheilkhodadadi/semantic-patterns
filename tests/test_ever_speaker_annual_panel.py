from __future__ import annotations

import pandas as pd

from semantic_ai_washing.aggregation.build_ever_speaker_annual_panel import _prepare_patent_panel


def test_prepare_patent_panel_uses_buffer_years_for_early_lags() -> None:
    patents = pd.DataFrame(
        [
            {"cik": "1", "year": 2014, "patents_total": 1, "patents_ai": 1, "ai_share": 1.0},
            {"cik": "1", "year": 2015, "patents_total": 2, "patents_ai": 2, "ai_share": 1.0},
            {"cik": "1", "year": 2016, "patents_total": 3, "patents_ai": 3, "ai_share": 1.0},
            {"cik": "1", "year": 2017, "patents_total": 4, "patents_ai": 4, "ai_share": 1.0},
        ]
    )

    panel = _prepare_patent_panel(
        patents,
        ciks=pd.Series(["0000000001"]),
        start_year=2016,
        end_year=2017,
        buffer_years=2,
    ).sort_values(["cik", "year"])

    row_2016 = panel.loc[panel["year"] == 2016].iloc[0]
    row_2017 = panel.loc[panel["year"] == 2017].iloc[0]

    assert row_2016["patents_ai"] == 3
    assert row_2016["patents_ai_lag1"] == 2
    assert row_2016["patents_ai_lag2"] == 1
    assert row_2016["patents_ai_lead1"] == 4
    assert row_2017["patents_ai_lag1"] == 3
    assert row_2017["patents_ai_lag2"] == 2


def test_prepare_patent_panel_keeps_zero_rows_for_firms_without_patents() -> None:
    patents = pd.DataFrame(
        columns=["cik", "year", "patents_total", "patents_ai", "ai_share"]
    )

    panel = _prepare_patent_panel(
        patents,
        ciks=pd.Series(["0000000001"]),
        start_year=2016,
        end_year=2016,
        buffer_years=2,
    )

    row = panel.iloc[0]
    assert row["cik"] == "0000000001"
    assert row["year"] == 2016
    assert row["patents_total"] == 0
    assert row["patents_ai"] == 0
