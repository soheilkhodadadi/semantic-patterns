from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.publication_runs.test_29_sec_ai_washing_enforcement_did import (
    _build_treatment_panel,
    _build_table,
)


def test_build_treatment_panel_uses_2022_ai_talkers_only() -> None:
    panel = pd.DataFrame(
        {
            "cik": ["1", "1", "1", "2", "2", "2"],
            "year": [2021, 2022, 2023, 2021, 2022, 2023],
            "any_ai_talk": [0, 1, 1, 1, 0, 1],
            "PatentMismatch": [0, 1, 1, 0, 1, 0],
            "LowCredibility": [0, 1, 1, 0, 1, 0],
            "ApplicationMismatch": [0, 0, 1, 0, 1, 0],
            "AI_Focus": [0.0, 1.0, 1.1, 0.2, 0.0, 0.7],
            "SpecShare": [0.0, 0.3, 0.2, 0.1, 0.0, 0.4],
            "A_S": [0.0, 0.4, 0.5, 0.9, 0.0, 0.6],
            "ln_assets_l1": [1.0] * 6,
            "cash_l1": [0.1] * 6,
            "leverage_l1": [0.2] * 6,
            "roa_l1": [0.03] * 6,
            "post_enforcement": [0, 0, 0, 0, 0, 0],
        }
    )
    sample, summary = _build_treatment_panel(panel)
    assert summary["analysis_firms"] == 1
    assert summary["treated_firms_main"] == 1
    assert sample["cik"].nunique() == 1
    assert sample["cik"].iloc[0] == "1"
    assert sample["treat_patent_mismatch_2022"].eq(1).all()


def test_build_table_places_panel_headers_and_cells() -> None:
    did_rows = [
        {
            "outcome": "SpecShare",
            "outcome_label": "Speculative share",
            "treatment_col": "treat_patent_mismatch_2022",
            "nobs": 100,
            "outcome_mean": 0.2,
            "params": {"treat_patent_mismatch_2022_x_post": -0.1},
            "bse": {"treat_patent_mismatch_2022_x_post": 0.05},
            "pvalues": {"treat_patent_mismatch_2022_x_post": 0.04},
        },
        {
            "outcome": "A_S",
            "outcome_label": "A/S ratio",
            "treatment_col": "treat_patent_mismatch_2022",
            "nobs": 100,
            "outcome_mean": 0.5,
            "params": {"treat_patent_mismatch_2022_x_post": 0.2},
            "bse": {"treat_patent_mismatch_2022_x_post": 0.08},
            "pvalues": {"treat_patent_mismatch_2022_x_post": 0.02},
        },
        {
            "outcome": "PatentMismatch",
            "outcome_label": "PatentMismatch",
            "treatment_col": "treat_patent_mismatch_2022",
            "nobs": 100,
            "outcome_mean": 0.1,
            "params": {"treat_patent_mismatch_2022_x_post": -0.15},
            "bse": {"treat_patent_mismatch_2022_x_post": 0.05},
            "pvalues": {"treat_patent_mismatch_2022_x_post": 0.01},
        },
        {
            "outcome": "AI_Focus",
            "outcome_label": "AI Focus",
            "treatment_col": "treat_patent_mismatch_2022",
            "nobs": 100,
            "outcome_mean": 1.2,
            "params": {"treat_patent_mismatch_2022_x_post": 0.1},
            "bse": {"treat_patent_mismatch_2022_x_post": 0.07},
            "pvalues": {"treat_patent_mismatch_2022_x_post": 0.12},
        },
        {
            "outcome": "SpecShare",
            "outcome_label": "SpecShare DID",
            "treatment_col": "treat_low_credibility_2022",
            "treatment_label": "LowCredibility in 2022",
            "nobs": 90,
            "outcome_mean": 0.2,
            "params": {"treat_low_credibility_2022_x_post": -0.09},
            "bse": {"treat_low_credibility_2022_x_post": 0.04},
            "pvalues": {"treat_low_credibility_2022_x_post": 0.03},
        },
        {
            "outcome": "A_S",
            "outcome_label": "A/S DID",
            "treatment_col": "treat_low_credibility_2022",
            "treatment_label": "LowCredibility in 2022",
            "nobs": 90,
            "outcome_mean": 0.4,
            "params": {"treat_low_credibility_2022_x_post": 0.19},
            "bse": {"treat_low_credibility_2022_x_post": 0.07},
            "pvalues": {"treat_low_credibility_2022_x_post": 0.01},
        },
        {
            "outcome": "PatentMismatch",
            "outcome_label": "PatentMismatch DID",
            "treatment_col": "treat_low_credibility_2022",
            "treatment_label": "LowCredibility in 2022",
            "nobs": 90,
            "outcome_mean": 0.1,
            "params": {"treat_low_credibility_2022_x_post": -0.11},
            "bse": {"treat_low_credibility_2022_x_post": 0.05},
            "pvalues": {"treat_low_credibility_2022_x_post": 0.02},
        },
        {
            "outcome": "SpecShare",
            "outcome_label": "SpecShare DID",
            "treatment_col": "treat_application_mismatch_2022",
            "treatment_label": "ApplicationMismatch in 2022",
            "nobs": 88,
            "outcome_mean": 0.2,
            "params": {"treat_application_mismatch_2022_x_post": -0.08},
            "bse": {"treat_application_mismatch_2022_x_post": 0.04},
            "pvalues": {"treat_application_mismatch_2022_x_post": 0.05},
        },
        {
            "outcome": "A_S",
            "outcome_label": "A/S DID",
            "treatment_col": "treat_application_mismatch_2022",
            "treatment_label": "ApplicationMismatch in 2022",
            "nobs": 88,
            "outcome_mean": 0.4,
            "params": {"treat_application_mismatch_2022_x_post": 0.18},
            "bse": {"treat_application_mismatch_2022_x_post": 0.07},
            "pvalues": {"treat_application_mismatch_2022_x_post": 0.02},
        },
        {
            "outcome": "PatentMismatch",
            "outcome_label": "PatentMismatch DID",
            "treatment_col": "treat_application_mismatch_2022",
            "treatment_label": "ApplicationMismatch in 2022",
            "nobs": 88,
            "outcome_mean": 0.1,
            "params": {"treat_application_mismatch_2022_x_post": -0.12},
            "bse": {"treat_application_mismatch_2022_x_post": 0.05},
            "pvalues": {"treat_application_mismatch_2022_x_post": 0.02},
        },
    ]
    event_rows = [
        {
            "outcome": "SpecShare",
            "outcome_label": "Speculative share",
            "nobs": 100,
            "params": {"treat_patent_mismatch_2022_x_2023": -0.05},
            "bse": {"treat_patent_mismatch_2022_x_2023": 0.03},
            "pvalues": {"treat_patent_mismatch_2022_x_2023": 0.09},
        },
        {
            "outcome": "A_S",
            "outcome_label": "A/S ratio",
            "nobs": 100,
            "params": {"treat_patent_mismatch_2022_x_2023": 0.07},
            "bse": {"treat_patent_mismatch_2022_x_2023": 0.04},
            "pvalues": {"treat_patent_mismatch_2022_x_2023": 0.07},
        },
        {
            "outcome": "PatentMismatch",
            "outcome_label": "PatentMismatch",
            "nobs": 100,
            "params": {"treat_patent_mismatch_2022_x_2023": -0.06},
            "bse": {"treat_patent_mismatch_2022_x_2023": 0.03},
            "pvalues": {"treat_patent_mismatch_2022_x_2023": 0.04},
        },
        {
            "outcome": "AI_Focus",
            "outcome_label": "AI Focus",
            "nobs": 100,
            "params": {"treat_patent_mismatch_2022_x_2023": 0.01},
            "bse": {"treat_patent_mismatch_2022_x_2023": 0.04},
            "pvalues": {"treat_patent_mismatch_2022_x_2023": 0.80},
        },
    ]
    summary = {"treated_firms_low_cred": 10, "treated_firms_application": 12}
    table_df, _did_keyed, _event_keyed = _build_table(did_rows, event_rows, summary)
    assert table_df.iloc[0]["Panel"].startswith("Panel A")
    assert "**" in table_df.iloc[1]["Post-2024 DID"]
    assert any(str(value).startswith("Panel B") for value in table_df["Panel"])
