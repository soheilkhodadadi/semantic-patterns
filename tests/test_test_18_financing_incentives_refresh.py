from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.publication_runs.test_18_financing_incentives_refresh import (
    _build_results_table,
    _fit_model,
    _prepare_sample,
)


def _sample_frame() -> pd.DataFrame:
    rows = []
    for year in range(2020, 2025):
        for firm in range(12):
            low = 1 if firm % 4 in (0, 1) else 0
            mismatch = 1 if firm % 5 in (0, 1) else 0
            rows.append(
                {
                    "cik": f"{1000 + firm}",
                    "permno": f"{5000 + firm}",
                    "year": year,
                    "sic": 3570 + 10 * (firm % 2),
                    "any_ai_talk": 1,
                    "A_S": 0.25 + 0.12 * (firm % 4),
                    "share_S": 0.1 + 0.18 * (firm % 4),
                    "AI_Focus": 0.4 + 0.03 * firm,
                    "ln_assets": 7.8 + 0.08 * firm,
                    "leverage": 0.2 + 0.01 * firm,
                    "cash": 0.1 + 0.01 * (firm % 3),
                    "roa": 0.05 - 0.01 * mismatch,
                    "market_cap_year_end": 200 + 20 * firm + 50 * mismatch,
                    "shrout": 100 + 3 * firm + 10 * low,
                    "log_patents_ai_lead0": 0.15 + 0.08 * (firm % 4),
                    "log_applications_ai_lead0": 0.2 + 0.07 * (firm % 4),
                }
            )
    return pd.DataFrame(rows)


def test_prepare_sample_builds_outcomes_and_nonbig_flag() -> None:
    sample, summary = _prepare_sample(_sample_frame())

    assert summary["ai_talking_rows"] == len(sample)
    assert "log_q_proxy" in sample.columns
    assert "equity_issue_lead1" in sample.columns
    assert "nonbig" in sample.columns


def test_fit_model_and_results_table_smoke() -> None:
    sample, _summary = _prepare_sample(_sample_frame())
    rows = []
    specs = [
        ("log_mktcap_assets", ["AI_Focus", "ln_assets", "cash", "roa"]),
        ("log_q_proxy", ["AI_Focus", "ln_assets", "cash", "roa"]),
        ("delta_log_q_proxy_lead1", ["AI_Focus", "ln_assets", "cash", "roa"]),
        ("share_growth_lead1", ["AI_Focus", "ln_assets", "leverage", "cash", "roa"]),
        ("equity_issue_lead1", ["AI_Focus", "ln_assets", "leverage", "cash", "roa"]),
    ]
    for subset in ["all", "nonbig"]:
        for outcome, controls in specs:
            for variant in ["PatentMismatch", "ApplicationMismatch", "LowCredibility"]:
                rows.append(_fit_model(sample, subset, variant, outcome, controls))

    table_df, keyed = _build_results_table(rows)

    assert set(table_df["panel"]) == {
        "Panel A. Full AI-talking sample",
        "Panel B. Non-big AI-talking sample",
    }
    assert ("all", "log_q_proxy", "PatentMismatch") in keyed
    assert ("nonbig", "equity_issue_lead1", "LowCredibility") in keyed
