from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.publication_runs.test_16_construct_variant_screen import (
    _add_construct_variants,
    _build_results_table,
    _fit_variant_model,
)


def _sample_frame() -> pd.DataFrame:
    rows = []
    for year in range(2021, 2025):
        for firm in range(8):
            talk = 1
            a_s = 0.4 + 0.1 * (firm % 4)
            spec = 0.2 + 0.15 * (firm % 4)
            patents_t = 0.1 * (firm % 5)
            apps_t = 0.15 * ((firm + 1) % 5)
            mismatch_like = 1 if firm % 4 == 0 else 0
            rows.append(
                {
                    "cik": f"{1000 + firm}",
                    "year": year,
                    "sic": 3570 + 10 * (firm % 2),
                    "any_ai_talk": talk,
                    "A_S": a_s,
                    "share_S": spec,
                    "AI_Focus": 0.4 + 0.05 * firm,
                    "ln_assets": 8.0 + 0.1 * firm,
                    "leverage": 0.2 + 0.01 * firm,
                    "cash": 0.1 + 0.01 * (firm % 3),
                    "roa": 0.05 - 0.002 * firm,
                    "log_patents_ai_lead0": patents_t,
                    "log_patents_ai_lead1": patents_t - 0.08 * mismatch_like,
                    "log_patents_ai_lead2": patents_t - 0.02 * mismatch_like,
                    "log_applications_ai_lead0": apps_t,
                    "log_applications_ai_lead1": apps_t + 0.04 * mismatch_like,
                    "log_applications_ai_lead2": apps_t + 0.08 * mismatch_like,
                }
            )
    return pd.DataFrame(rows)


def test_add_construct_variants_creates_expected_columns() -> None:
    sample = _sample_frame()
    out = _add_construct_variants(sample)

    for column in [
        "LowCredibility",
        "StrictPatentMismatch",
        "ApplicationMismatch",
        "WeakPatentRelative",
        "PatentMismatch",
    ]:
        assert column in out.columns
        assert set(out[column].dropna().unique()).issubset({0, 1})


def test_variant_model_and_results_table_smoke() -> None:
    sample = _add_construct_variants(_sample_frame())
    sample = sample.loc[sample["any_ai_talk"].eq(1)].copy()
    rows = []
    for dependent in [
        "log_patents_ai_lead1",
        "log_patents_ai_lead2",
        "log_applications_ai_lead1",
        "log_applications_ai_lead2",
    ]:
        rows.append(_fit_variant_model(sample, "PatentMismatch", dependent))
        rows.append(_fit_variant_model(sample, "ApplicationMismatch", dependent))
        rows.append(_fit_variant_model(sample, "LowCredibility", dependent))
        rows.append(_fit_variant_model(sample, "WeakPatentRelative", dependent))
        rows.append(_fit_variant_model(sample, "StrictPatentMismatch", dependent))

    table_df, keyed = _build_results_table(rows)

    assert set(table_df["panel"]) == {
        "Panel A. Future AI grant outcomes",
        "Panel B. Future AI application outcomes",
    }
    assert ("log_patents_ai_lead1", "PatentMismatch") in keyed
    assert "Log(1 + AI grants) t+1" in table_df.columns
