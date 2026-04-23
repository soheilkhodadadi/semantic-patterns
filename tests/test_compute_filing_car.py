from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.compute_filing_car import _compute_bhar, _compute_car


def _sample_group() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "relative_day": [-1, 0, 1, 2],
            "abnormal_ret_vw": [0.01, 0.02, -0.01, 0.03],
            "ret": [0.03, 0.01, -0.02, 0.04],
            "vwretd": [0.01, 0.00, -0.01, 0.01],
        }
    )


def test_compute_car_sums_abnormal_returns_when_complete() -> None:
    group = _sample_group()
    value = _compute_car(group, -1, 1)
    assert value is not None
    assert round(value, 6) == 0.02


def test_compute_car_returns_none_when_window_incomplete() -> None:
    group = _sample_group().query("relative_day != 0")
    assert _compute_car(group, -1, 1) is None


def test_compute_bhar_uses_buy_and_hold_difference() -> None:
    group = _sample_group().query("relative_day >= 0 and relative_day <= 2")
    value = _compute_bhar(group, 0, 2)
    assert value is not None
    gross_stock = (1.01) * (0.98) * (1.04)
    gross_market = (1.00) * (0.99) * (1.01)
    assert round(value, 8) == round(gross_stock - gross_market, 8)
