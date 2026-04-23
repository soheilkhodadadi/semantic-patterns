from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.publication_runs.test_17_real_outcome_dynamics import (
    _build_results_table,
    _fit_model,
    _prepare_sample,
)


def _sample_frame() -> pd.DataFrame:
    rows = []
    for year in range(2020, 2025):
        for firm in range(10):
            mismatch_like = 1 if firm % 5 in (0, 1) else 0
            low_cred_like = 1 if firm % 4 in (0, 1) else 0
            rows.append(
                {
                    "cik": f"{1000 + firm}",
                    "year": year,
                    "sic": 3570 + 10 * (firm % 2),
                    "any_ai_talk": 1,
                    "A_S": 0.3 + 0.15 * (firm % 4),
                    "share_S": 0.1 + 0.2 * (firm % 4),
                    "AI_Focus": 0.4 + 0.04 * firm,
                    "ln_assets": 8.0 + 0.1 * firm,
                    "leverage": 0.2 + 0.01 * firm,
                    "cash": 0.1 + 0.01 * (firm % 3),
                    "roa": 0.05 - 0.015 * mismatch_like + 0.002 * year,
                    "sales_growth": 0.10 - 0.04 * mismatch_like + 0.01 * low_cred_like,
                    "capx_at": 0.04 + 0.002 * low_cred_like,
                    "rd_intensity": 0.06 + 0.01 * low_cred_like + 0.004 * mismatch_like,
                    "log_patents_ai_lead0": 0.2 + 0.1 * (firm % 4),
                    "log_applications_ai_lead0": 0.25 + 0.08 * (firm % 4),
                }
            )
    return pd.DataFrame(rows)


def test_prepare_sample_creates_future_outcomes() -> None:
    sample, summary = _prepare_sample(_sample_frame())

    assert summary["ai_talking_rows"] == len(sample)
    assert "roa_lead1" in sample.columns
    assert "rd_intensity_lead2" in sample.columns
    assert sample["PatentMismatch"].isin([0, 1]).all()


def test_fit_model_and_results_table_smoke() -> None:
    sample, _summary = _prepare_sample(_sample_frame())
    rows = []
    control_map = {
        "roa": ["AI_Focus", "ln_assets", "leverage", "cash"],
        "sales_growth": ["AI_Focus", "ln_assets", "leverage", "cash", "roa"],
        "capx_at": ["AI_Focus", "ln_assets", "leverage", "cash", "roa"],
        "rd_intensity": ["AI_Focus", "ln_assets", "leverage", "cash", "roa"],
    }
    for outcome, controls in control_map.items():
        for horizon in [1, 2]:
            for variant in ["PatentMismatch", "ApplicationMismatch", "LowCredibility"]:
                rows.append(_fit_model(sample, variant, outcome, horizon, controls))

    table_df, keyed = _build_results_table(rows)

    assert "Canonical grant mismatch" in table_df.columns
    assert ("roa", 1, "PatentMismatch") in keyed
    assert ("rd_intensity", 2, "LowCredibility") in keyed
