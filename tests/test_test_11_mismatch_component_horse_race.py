from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.publication_runs.test_11_mismatch_component_horse_race import (
    _build_results_table,
    _fit_model,
)


def _sample_frame(rows: int = 24) -> pd.DataFrame:
    data = []
    for i in range(rows):
        filing_year = 2021 + (i % 4)
        gvkey = f"{1000 + (i % 6):06d}"
        low = 1 if i % 3 == 0 else 0
        weak = 1 if i % 4 in (0, 1) else 0
        mismatch = 1 if low and weak else 0
        ai_focus = 0.5 + 0.1 * (i % 5)
        car = 0.01 + 0.004 * mismatch + 0.002 * low - 0.001 * weak + 0.0005 * (i % 4)
        bhar = 0.02 + 0.010 * mismatch + 0.003 * low - 0.002 * weak + 0.0007 * (i % 3)
        data.append(
            {
                "gvkey": gvkey,
                "sic2": 35 + (i % 3),
                "filing_year": filing_year,
                "AI_Focus": ai_focus,
                "ln_assets": 8.0 + 0.1 * i,
                "leverage": 0.1 + 0.01 * (i % 5),
                "cash": 0.05 + 0.01 * (i % 4),
                "roa": 0.01 * ((i % 7) - 2),
                "PatentMismatch": mismatch,
                "LowCredibility": low,
                "WeakPatentRelative": weak,
                "car_m1_p1": car,
                "car_m1_p1_complete": 1,
                "bhar_3m": bhar,
                "bhar_3m_complete": 1,
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
        "interaction",
        "Components + interaction",
        "LowCredibility + WeakPatentRelative + LowCredibility:WeakPatentRelative + AI_Focus + {controls} + C(sic2) + C(filing_year)",
    )

    assert result["nobs"] == len(sample)
    assert "LowCredibility:WeakPatentRelative" in result["params"]
    assert "AI_Focus" in result["params"]


def test_build_results_table_contains_panels() -> None:
    sample = _sample_frame()
    rows = []
    for outcome, label, complete in [
        ("car_m1_p1", "CAR[-1,+1]", "car_m1_p1_complete"),
        ("bhar_3m", "BHAR[+2,+63]", "bhar_3m_complete"),
    ]:
        rows.append(
            _fit_model(
                sample,
                outcome,
                label,
                complete,
                "mismatch_only",
                "Mismatch-only",
                "PatentMismatch + AI_Focus + {controls} + C(sic2) + C(filing_year)",
            )
        )
        rows.append(
            _fit_model(
                sample,
                outcome,
                label,
                complete,
                "components",
                "Components",
                "LowCredibility + WeakPatentRelative + AI_Focus + {controls} + C(sic2) + C(filing_year)",
            )
        )
        rows.append(
            _fit_model(
                sample,
                outcome,
                label,
                complete,
                "interaction",
                "Components + interaction",
                "LowCredibility + WeakPatentRelative + LowCredibility:WeakPatentRelative + AI_Focus + {controls} + C(sic2) + C(filing_year)",
            )
        )

    table_df, keyed = _build_results_table(rows)

    assert set(table_df["panel"]) == {"CAR[-1,+1]", "BHAR[+2,+63]"}
    assert ("bhar_3m", "interaction") in keyed
    assert "Components + interaction" in table_df.columns
