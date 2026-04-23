from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.publication_runs.test_15_matched_ai_talking_sample import (
    _build_balance_table,
    _build_outcome_table,
    _match_pairs,
)


def _sample_frame() -> pd.DataFrame:
    rows = []
    for year in [2021, 2022]:
        for sic2 in [35, 36]:
            for i in range(6):
                mismatch = 1 if i < 3 else 0
                rows.append(
                    {
                        "filing_id": f"{year}_{sic2}_{i}",
                        "gvkey": f"{1000 + year + sic2 + i:06d}",
                        "filing_year": year,
                        "sic2": sic2,
                        "PatentMismatch": mismatch,
                        "log_mcap_l1": 4.0 + 0.1 * i + 0.05 * mismatch,
                        "annual_bhar_vw_l1": -0.05 + 0.01 * i,
                        "annual_ret_l1": -0.03 + 0.01 * i,
                        "ln_assets": 8.0 + 0.1 * i,
                        "leverage": 0.1 + 0.02 * i,
                        "cash": 0.05 + 0.01 * i,
                        "roa": -0.02 + 0.01 * i,
                        "car_m1_p1": 0.01 - 0.005 * mismatch + 0.001 * i,
                        "bhar_1m": 0.02 - 0.004 * mismatch + 0.001 * i,
                        "bhar_3m": 0.03 - 0.003 * mismatch + 0.001 * i,
                        "bhar_6m": 0.04 - 0.002 * mismatch + 0.001 * i,
                        "bhar_12m": 0.05 - 0.001 * mismatch + 0.001 * i,
                    }
                )
    return pd.DataFrame(rows)


def test_match_pairs_smoke() -> None:
    sample = _sample_frame()

    pairs_df, summary = _match_pairs(sample)

    assert not pairs_df.empty
    assert summary["matched_pairs"] == len(pairs_df)
    assert {"treated_id", "control_id", "match_distance"} <= set(pairs_df.columns)


def test_balance_and_outcome_tables_smoke() -> None:
    sample = _sample_frame()
    pairs_df, _ = _match_pairs(sample)

    balance_df = _build_balance_table(sample, pairs_df)
    outcome_df = _build_outcome_table(sample, pairs_df)

    assert not balance_df.empty
    assert not outcome_df.empty
    assert "matched_smd" in balance_df.columns
    assert "diff_treat_minus_control" in outcome_df.columns
    assert "CAR[-1,+1]" in set(outcome_df["row_label"])
