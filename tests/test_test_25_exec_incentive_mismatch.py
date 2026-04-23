from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.publication_runs.test_25_exec_incentive_mismatch import (
    _prepare_execucomp,
    _prepare_sample,
)


def test_prepare_execucomp_builds_incentive_fields() -> None:
    raw = pd.DataFrame(
        {
            "gvkey": ["1001"],
            "year": [2020],
            "execid": ["E1"],
            "exec_fullname": ["Jane Doe"],
            "ceoann": ["CEO"],
            "pceo": [None],
            "titleann": ["Chief Executive Officer"],
            "title": ["CEO"],
            "salary": [100.0],
            "bonus": [10.0],
            "stock_awards_fv": [40.0],
            "option_awards_fv": [20.0],
            "noneq_incent": [5.0],
            "total_curr": [110.0],
            "tdc1": [200.0],
            "shrown_excl_opts": [5.0],
            "shrown_excl_opts_pct": [1.5],
            "opt_unex_exer_est_val": [25.0],
            "opt_unex_unexer_est_val": [75.0],
            "n_ceo_rows": [1],
        }
    )
    out, summary = _prepare_execucomp(raw)
    assert summary["exec_rows"] == 1
    assert out.loc[0, "equity_award_share"] == 0.3
    assert out.loc[0, "ownership_pct"] == 1.5
    assert out.loc[0, "unvested_option_value"] == 100.0


def test_prepare_sample_matches_lagged_execucomp_rows() -> None:
    panel = pd.DataFrame(
        {
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
    ceo = pd.DataFrame(
        {
            "gvkey": ["1001"],
            "year": [2020],
            "execid": ["E1"],
            "exec_fullname": ["Jane Doe"],
            "equity_award_share": [0.4],
            "ownership_pct": [1.0],
            "log_unvested_option_value": [2.0],
            "log_tdc1": [5.0],
            "n_ceo_rows": [1],
        }
    )
    sample, summary = _prepare_sample(panel, ceo)
    assert summary["lagged_ceo_match_rows"] == 1
    row = sample.loc[sample["year"].eq(2021)].iloc[0]
    assert row["equity_award_share_lag1"] == 0.4
    assert row["ownership_pct_lag1"] == 1.0
