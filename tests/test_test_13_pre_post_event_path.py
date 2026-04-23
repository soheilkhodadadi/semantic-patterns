from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.publication_runs.test_13_pre_post_event_path import (
    _build_cumulative_path_series,
    _build_window_table,
)


def _sample_monthly_panel() -> pd.DataFrame:
    rows = []
    for filing_num in range(6):
        mismatch = 1 if filing_num % 2 == 0 else 0
        for rel_month in range(-12, 13):
            ret = 0.01 + 0.002 * mismatch + 0.0003 * rel_month + 0.0002 * filing_num
            vwretd = 0.008 + 0.0002 * rel_month + 0.0001 * (filing_num % 3)
            rows.append(
                {
                    "filing_id": f"f{filing_num:02d}",
                    "gvkey": f"{1000 + filing_num:06d}",
                    "PatentMismatch": mismatch,
                    "group_label": "Mismatch" if mismatch else "No mismatch",
                    "rel_month": rel_month,
                    "ret": ret,
                    "vwretd": vwretd,
                }
            )
    return pd.DataFrame(rows)


def test_build_cumulative_path_series_has_expected_columns() -> None:
    monthly_panel = _sample_monthly_panel()

    grouped, figure_series = _build_cumulative_path_series(monthly_panel)

    assert set(grouped["PatentMismatch"]) == {0, 1}
    assert set(figure_series.columns) >= {
        "rel_month",
        "mean_non_mismatch",
        "mean_mismatch",
        "diff_mismatch_minus_non",
        "ci_low",
        "ci_high",
    }
    assert figure_series["rel_month"].min() == -12
    assert figure_series["rel_month"].max() == 12


def test_build_window_table_contains_pre_and_post_panels() -> None:
    monthly_panel = _sample_monthly_panel()

    table_df = _build_window_table(monthly_panel)

    assert set(table_df["panel"]) == {"Pre-filing windows", "Filing and post-filing windows"}
    assert "BHAR[-12,-2]" in set(table_df["window_label"])
    assert "BHAR[+1,+12]" in set(table_df["window_label"])
