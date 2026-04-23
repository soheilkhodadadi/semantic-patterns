from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.publication_runs.test_12_predictive_return_controls import (
    _build_results_table,
    _fit_model,
)


def _sample_frame(rows: int = 36) -> pd.DataFrame:
    data = []
    for i in range(rows):
        filing_year = 2020 + (i % 4)
        gvkey = f"{1000 + (i % 8):06d}"
        mismatch = 1 if i % 4 in (0, 1) else 0
        a_s = 0.2 + 0.05 * (i % 5)
        ai_focus = 0.4 + 0.08 * (i % 6)
        bhar_3m = 0.01 + 0.012 * mismatch + 0.004 * a_s - 0.002 * ai_focus + 0.0008 * (i % 3)
        bhar_12m = 0.02 + 0.015 * mismatch + 0.003 * a_s - 0.002 * ai_focus + 0.0010 * (i % 4)
        data.append(
            {
                "gvkey": gvkey,
                "sic2": 35 + (i % 3),
                "filing_year": filing_year,
                "PatentMismatch": mismatch,
                "A_S": a_s,
                "AI_Focus": ai_focus,
                "ln_assets": 8.0 + 0.04 * i,
                "leverage": 0.10 + 0.01 * (i % 5),
                "cash": 0.08 + 0.01 * (i % 4),
                "roa": -0.02 + 0.01 * (i % 6),
                "rd_intensity": 0.01 + 0.005 * (i % 4),
                "capx_at": 0.02 + 0.004 * (i % 5),
                "sales_growth": -0.03 + 0.02 * (i % 5),
                "ln_mktcap_year_end": 4.0 + 0.05 * i,
                "annual_ret": -0.10 + 0.04 * (i % 6),
                "annual_bhar_vw": -0.08 + 0.03 * (i % 5),
                "ln_vol": -2.0 + 0.1 * (i % 6),
                "firm_age_market": 3 + (i % 10),
                "log_patents_ai_lag1": 0.2 * (i % 5),
                "bhar_3m": bhar_3m,
                "bhar_3m_complete": 1,
                "bhar_12m": bhar_12m,
                "bhar_12m_complete": 1,
            }
        )
    return pd.DataFrame(data)


def test_fit_model_smoke() -> None:
    sample = _sample_frame()
    result = _fit_model(
        sample,
        "bhar_3m",
        "BHAR[+2,+63]",
        "bhar_3m_complete",
        "market_patent",
        "+ market + patent history",
        [
            "ln_assets",
            "leverage",
            "cash",
            "roa",
            "rd_intensity",
            "capx_at",
            "sales_growth",
            "ln_mktcap_year_end",
            "annual_ret",
            "annual_bhar_vw",
            "ln_vol",
            "firm_age_market",
            "log_patents_ai_lag1",
        ],
    )

    assert result["nobs"] == len(sample)
    assert "PatentMismatch" in result["params"]
    assert "A_S" in result["params"]
    assert "AI_Focus" in result["params"]


def test_build_results_table_contains_both_panels() -> None:
    sample = _sample_frame()
    control_specs = [
        ("core", "Core controls", ["ln_assets", "leverage", "cash", "roa"]),
        (
            "operating",
            "+ operating controls",
            ["ln_assets", "leverage", "cash", "roa", "rd_intensity", "capx_at", "sales_growth"],
        ),
        (
            "market",
            "+ market characteristics",
            [
                "ln_assets",
                "leverage",
                "cash",
                "roa",
                "rd_intensity",
                "capx_at",
                "sales_growth",
                "ln_mktcap_year_end",
                "annual_ret",
                "annual_bhar_vw",
                "ln_vol",
                "firm_age_market",
            ],
        ),
        (
            "market_patent",
            "+ market + patent history",
            [
                "ln_assets",
                "leverage",
                "cash",
                "roa",
                "rd_intensity",
                "capx_at",
                "sales_growth",
                "ln_mktcap_year_end",
                "annual_ret",
                "annual_bhar_vw",
                "ln_vol",
                "firm_age_market",
                "log_patents_ai_lag1",
            ],
        ),
    ]
    rows = []
    for outcome, label, complete in [
        ("bhar_3m", "BHAR[+2,+63]", "bhar_3m_complete"),
        ("bhar_12m", "BHAR[+2,+252]", "bhar_12m_complete"),
    ]:
        for model_id, model_label, controls in control_specs:
            rows.append(
                _fit_model(
                    sample,
                    outcome,
                    label,
                    complete,
                    model_id,
                    model_label,
                    controls,
                )
            )

    table_df, keyed = _build_results_table(rows)

    assert set(table_df["panel"]) == {"BHAR[+2,+63]", "BHAR[+2,+252]"}
    assert ("bhar_3m", "core") in keyed
    assert ("bhar_12m", "market_patent") in keyed
