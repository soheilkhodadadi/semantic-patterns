from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.publication_runs.test_28_public_13f_institutional_discernment import (
    _link_panel_to_cusip,
    _prepare_ownership_panel,
)


def test_link_panel_to_cusip_picks_matching_name_window() -> None:
    panel = pd.DataFrame(
        {
            "gvkey": ["1001"],
            "permno": [12345],
            "ticker": ["ABC"],
            "year": [2020],
            "year_end_market_date": [pd.Timestamp("2020-12-31")],
            "PatentMismatch": [1],
            "LowCredibility": [1],
            "A_S": [0.5],
            "AI_Focus": [1.0],
            "ln_assets": [2.0],
            "cash": [0.1],
            "leverage": [0.2],
            "roa": [0.03],
            "market_cap_year_end": [100.0],
            "shrout": [1000.0],
            "big": [False],
            "post_chatgpt": [0],
        }
    )
    stocknames = pd.DataFrame(
        {
            "permno": [12345, 12345],
            "namedt": [pd.Timestamp("2019-01-01"), pd.Timestamp("2020-06-01")],
            "nameenddt": [pd.Timestamp("2020-05-31"), pd.Timestamp("2021-12-31")],
            "ticker": ["ABC", "ABC"],
            "ncusip": ["11111111", "22222222"],
            "cusip": ["11111111", "22222222"],
        }
    )
    linked, summary = _link_panel_to_cusip(panel, stocknames)
    assert summary["linked_rows"] == 1
    assert linked.iloc[0]["ncusip8"] == "22222222"


def test_prepare_ownership_panel_builds_t1_and_delta() -> None:
    linked_panel = pd.DataFrame(
        {
            "gvkey": ["1001", "1001"],
            "permno": [12345, 12345],
            "ticker": ["ABC", "ABC"],
            "year": [2020, 2021],
            "ncusip8": ["22222222", "22222222"],
            "shrout": [1000.0, 1200.0],
            "PatentMismatch": [0, 1],
            "LowCredibility": [0, 1],
            "A_S": [0.2, 0.8],
            "AI_Focus": [1.0, 1.0],
            "ln_assets": [2.0, 2.0],
            "cash": [0.1, 0.1],
            "leverage": [0.2, 0.2],
            "roa": [0.03, 0.04],
            "big": [False, True],
            "post_chatgpt": [0, 0],
        }
    )
    q4_metrics = pd.DataFrame(
        {
            "year": [2020, 2021],
            "ncusip8": ["22222222", "22222222"],
            "total_13f_shares": [500_000.0, 900_000.0],
            "n_13f_holders": [10, 15],
            "hhi_13f": [0.20, 0.15],
            "top1_holder_share": [0.30, 0.25],
        }
    )
    sample, summary = _prepare_ownership_panel(linked_panel, q4_metrics)
    assert summary["ownership_t1_rows"] == 1
    row = sample.loc[sample["year"].eq(2020)].iloc[0]
    assert round(row["io_share_13f_q4"], 6) == 0.5
    assert round(row["io_share_13f_t1"], 6) == 0.75
    assert round(row["delta_io_share_13f_t1"], 6) == 0.25
