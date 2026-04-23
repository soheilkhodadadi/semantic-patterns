from __future__ import annotations

from datetime import date

import pandas as pd

from semantic_ai_washing.analysis.build_filing_lagged_controls import (
    choose_latest_prior_control,
    derive_controls,
)


def test_choose_latest_prior_control_uses_latest_eligible_datadate() -> None:
    controls = pd.DataFrame(
        {
            "datadate": [date(2021, 12, 31), date(2022, 12, 31), date(2023, 12, 31)],
            "at": [100.0, 120.0, 130.0],
        }
    )
    chosen = choose_latest_prior_control(controls, date(2023, 3, 15))
    assert chosen is not None
    assert chosen["datadate"] == date(2022, 12, 31)


def test_derive_controls_builds_standard_ratios() -> None:
    record = pd.Series(
        {
            "at": 100.0,
            "sale": 50.0,
            "ib": 10.0,
            "ni": 9.0,
            "che": 20.0,
            "dltt": 30.0,
            "dlc": 5.0,
            "capx": 4.0,
            "xrd": 6.0,
            "sales_growth": 0.25,
        }
    )
    derived = derive_controls(record)
    assert round(derived["ln_assets"], 6) == round(4.605170185988092, 6)
    assert derived["leverage"] == 0.35
    assert derived["cash"] == 0.2
    assert derived["rd_intensity"] == 0.12
    assert derived["capx_at"] == 0.04
    assert derived["roa"] == 0.1
    assert derived["sales_growth"] == 0.25
