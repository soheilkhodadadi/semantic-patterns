from __future__ import annotations

import numpy as np
import pandas as pd

from semantic_ai_washing.analysis.run_filing_event_regressions import (
    MODEL_SPECS,
    build_report,
    run_models,
)


def _sample_frame(rows: int = 24) -> pd.DataFrame:
    filing_year = np.array([2021, 2022, 2023, 2024] * (rows // 4) + [2021] * (rows % 4))
    post = (filing_year >= 2023).astype(int)
    gvkeys = np.array([f"{1000 + (i % 6):06d}" for i in range(rows)])
    permnos = np.array([10000 + (i % 6) for i in range(rows)])
    share_actionable = np.linspace(0.05, 0.45, rows)
    share_speculative = np.linspace(0.35, 0.05, rows)
    noise = np.linspace(-0.02, 0.02, rows)
    car = 0.02 + 0.15 * share_actionable - 0.10 * share_speculative + 0.03 * post + noise
    bhar = 0.05 + 0.40 * share_actionable - 0.25 * share_speculative + 0.08 * post + noise
    return pd.DataFrame(
        {
            "filing_id": [f"f{i:03d}" for i in range(rows)],
            "gvkey": gvkeys,
            "permno": permnos,
            "filing_year": filing_year,
            "car_m1_p1": car,
            "car_m2_p2": car + 0.01,
            "bhar_6m": bhar,
            "share_actionable": share_actionable,
            "share_speculative": share_speculative,
            "share_irrelevant": 1.0 - share_actionable - share_speculative,
            "post_chatgpt": post,
            "ln_assets": np.linspace(8.0, 10.0, rows),
            "leverage": np.linspace(0.1, 0.4, rows),
            "cash": np.linspace(0.05, 0.25, rows),
            "roa": np.linspace(-0.05, 0.10, rows),
            "rd_intensity": np.linspace(0.01, 0.08, rows),
            "capx_at": np.linspace(0.02, 0.09, rows),
            "sales_growth": np.linspace(-0.10, 0.15, rows),
            "sample_car_core": 1,
            "sample_car_extended": 1,
            "sample_bhar_6m_core": 1,
        }
    )


def test_run_models_smoke() -> None:
    df = _sample_frame()
    results, coefficients = run_models(df)

    assert len(results) == len(MODEL_SPECS)
    assert not coefficients.empty
    assert {result.model_id for result in results} == {spec.model_id for spec in MODEL_SPECS}
    headline = next(result for result in results if result.model_id == "car_m1_p1_post_core_hc3")
    assert headline.nobs == len(df)
    assert headline.unique_gvkey == df["gvkey"].nunique()
    assert "share_actionable" in headline.focal_terms
    assert headline.focal_terms["share_actionable"]["coef"] is not None


def test_build_report_reflects_sample_counts() -> None:
    df = _sample_frame()
    results, _ = run_models(df)
    report = build_report(df, results)

    assert report["sample_summary"]["row_count"] == len(df)
    assert report["sample_summary"]["sample_car_core"] == len(df)
    assert report["sample_summary"]["sample_bhar_6m_core"] == len(df)
    assert report["headline_findings"]
