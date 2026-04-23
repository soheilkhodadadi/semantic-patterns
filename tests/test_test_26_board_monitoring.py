from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.publication_runs.test_26_board_monitoring import (
    _prepare_board,
    _prepare_sample,
)


def test_prepare_board_builds_monitoring_aggregates() -> None:
    raw = pd.DataFrame(
        {
            "year": [2020, 2020],
            "ticker": ["ABC", "ABC"],
            "female": ["Yes", None],
            "audit_membership": ["Chair", None],
            "comp_membership": [None, "Member"],
            "cg_membership": ["Member", None],
            "nom_membership": [None, None],
            "outside_public_boards": [2, 0],
            "financial_expert": ["Yes", None],
            "non_ceo_leader": ["Lead Dir", None],
            "former_employee_yn": [None, "Yes"],
        }
    )
    agg, summary = _prepare_board(raw)
    assert summary["board_rows"] == 2
    row = agg.iloc[0]
    assert row["female_share"] == 0.5
    assert row["audit_share"] == 0.5
    assert row["cg_share"] == 0.5
    assert row["board_size"] == 2


def test_prepare_sample_matches_lagged_board_rows() -> None:
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
            "sic2": [35, 35],
        }
    )
    board = pd.DataFrame(
        {
            "ticker": ["ABC"],
            "year": [2020],
            "female_share": [0.4],
            "audit_share": [0.3],
            "comp_share": [0.2],
            "cg_share": [0.5],
            "nom_share": [0.1],
            "fin_expert_share": [0.2],
            "non_ceo_leader_share": [0.1],
            "former_employee_share": [0.0],
            "outside_public_boards_avg": [1.5],
            "board_size": [10],
        }
    )
    sample, summary = _prepare_sample(panel, board)
    assert summary["lagged_board_match_rows"] == 1
    row = sample.loc[sample["year"].eq(2021)].iloc[0]
    assert row["audit_share_lag1"] == 0.3
    assert row["cg_share_lag1"] == 0.5
    assert row["board_size_lag1"] == 10
