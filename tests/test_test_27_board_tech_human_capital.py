from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.publication_runs.test_27_board_tech_human_capital import (
    _prepare_active_board,
    _prepare_human_capital,
    _prepare_sample,
)


def test_prepare_human_capital_builds_combined_flag() -> None:
    emp = pd.DataFrame(
        {
            "directorid": [1, 2],
            "rolename": ["Chief Technology Officer", "Independent Director"],
        }
    )
    education = pd.DataFrame(
        {
            "directorid": [2],
            "qualification": ["BSc"],
            "fulltextdescription": ["Electrical Engineering"],
        }
    )
    out, summary = _prepare_human_capital(emp, education)
    assert summary["tech_lead_directors"] == 1
    assert summary["stem_directors"] == 1
    assert summary["tech_hc_directors"] == 2
    row_one = out.loc[out["directorid"].eq(1)].iloc[0]
    row_two = out.loc[out["directorid"].eq(2)].iloc[0]
    assert bool(row_one["tech_lead_flag"])
    assert bool(row_two["stem_flag"])


def test_prepare_sample_matches_lagged_boardtech_rows() -> None:
    panel = pd.DataFrame(
        {
            "ticker": ["ABC", "ABC"],
            "gvkey": ["1001", "1001"],
            "year": [2020, 2021],
            "PatentMismatch": [0, 1],
            "LowCredibility": [0, 1],
            "A_S": [0.2, 0.8],
            "AI_Focus": [1.0, 1.0],
            "ln_assets": [2.0, 2.0],
            "cash": [0.1, 0.1],
            "leverage": [0.2, 0.2],
            "roa": [0.03, 0.04],
            "market_cap_year_end": [100.0, 120.0],
            "big": [0, 1],
            "post_chatgpt": [0, 0],
            "any_ai_talk": [1, 1],
        }
    )
    company_map = pd.DataFrame({"companyid": [10], "ticker": ["ABC"]})
    board_roles = pd.DataFrame(
        {
            "companyid": [10, 10],
            "directorid": [1, 2],
            "datestartrole": [pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-01")],
            "dateendrole": [pd.Timestamp("2025-01-01"), pd.Timestamp("2025-01-01")],
        }
    )
    active_board, _summary = _prepare_active_board(panel, company_map, board_roles)
    human_cap = pd.DataFrame(
        {
            "directorid": [1, 2],
            "tech_lead_flag": [True, False],
            "stem_flag": [False, True],
            "tech_hc_flag": [True, True],
        }
    )
    sample, summary = _prepare_sample(panel, active_board, human_cap)
    assert summary["lagged_boardtech_rows"] == 1
    row = sample.loc[sample["year"].eq(2021)].iloc[0]
    assert row["tech_lead_share_lag1"] == 0.5
    assert row["tech_hc_share_lag1"] == 1.0
    assert row["any_tech_hc_lag1"] == 1.0
