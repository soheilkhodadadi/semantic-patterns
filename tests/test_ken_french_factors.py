from __future__ import annotations

import math

from semantic_ai_washing.analysis.ken_french_factors import (
    parse_ff5_monthly_text,
    parse_momentum_monthly_text,
)
from semantic_ai_washing.analysis.publication_runs.test_09_factor_adjusted_alpha import (
    _fit_factor_model,
)
import pandas as pd


FF5_SAMPLE = """This file was created using the 202602 CRSP database.

,Mkt-RF,SMB,HML,RMW,CMA,RF
202001,   1.23,   0.45,  -0.67,   0.11,  -0.22,   0.10
202002,  -2.00,   1.00,   0.50,  -0.30,   0.20,   0.09

 Annual Factors: January-December
"""


MOM_SAMPLE = """Momentum Factor (Mom)

,Mom
202001,   0.80
202002, -99.99

 Annual Factors: January-December
"""


def test_parse_ff5_monthly_text_scales_to_decimals() -> None:
    df = parse_ff5_monthly_text(FF5_SAMPLE)

    assert list(df["month"].astype(str)) == ["2020-01", "2020-02"]
    assert math.isclose(df.loc[0, "mkt_rf"], 0.0123, rel_tol=1e-9)
    assert math.isclose(df.loc[1, "rf"], 0.0009, rel_tol=1e-9)


def test_parse_momentum_monthly_text_handles_missing_sentinel() -> None:
    df = parse_momentum_monthly_text(MOM_SAMPLE)

    assert math.isclose(df.loc[0, "mom"], 0.0080, rel_tol=1e-9)
    assert pd.isna(df.loc[1, "mom"])


def test_fit_factor_model_returns_alpha_summary() -> None:
    frame = pd.DataFrame(
        {
            "ew_long_short": [0.010, 0.015, 0.009, 0.012, 0.013, 0.011],
            "mkt_rf": [0.01, -0.02, 0.01, 0.00, 0.02, -0.01],
            "smb": [0.00, 0.01, -0.01, 0.02, 0.01, -0.02],
            "hml": [0.01, 0.00, -0.01, 0.01, 0.00, -0.01],
        }
    )

    fit = _fit_factor_model(frame, "ew_long_short", ["mkt_rf", "smb", "hml"])

    assert fit["n_months"] == len(frame)
    assert not math.isnan(fit["alpha"])
    assert not math.isnan(fit["alpha_p"])
