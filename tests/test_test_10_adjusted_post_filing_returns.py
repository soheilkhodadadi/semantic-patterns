from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.publication_runs.test_10_adjusted_post_filing_returns import (
    _add_peer_adjusted_outcome,
    _build_results,
)


def _sample_frame(rows: int = 36) -> pd.DataFrame:
    data = []
    for i in range(rows):
        filing_year = 2021 + (i % 3)
        mismatch = 1 if i % 4 in (0, 1) else 0
        data.append(
            {
                "filing_id": f"f{i:03d}",
                "gvkey": f"{1000 + (i % 8):06d}",
                "PatentMismatch": mismatch,
                "sic2": 35 + (i % 3),
                "filing_year": filing_year,
                "size_bucket": ["S", "M", "L"][i % 3],
                "mom_bucket": ["L", "M", "H"][i % 3],
                "bhar_1m": 0.01 + 0.004 * mismatch + 0.001 * (i % 3),
                "bhar_3m": 0.02 + 0.006 * mismatch + 0.001 * (i % 4),
                "bhar_6m": 0.03 + 0.007 * mismatch + 0.001 * (i % 5),
                "bhar_12m": 0.04 + 0.008 * mismatch + 0.001 * (i % 6),
            }
        )
    return pd.DataFrame(data)


def test_add_peer_adjusted_outcome_smoke() -> None:
    sample = _sample_frame()

    adjusted = _add_peer_adjusted_outcome(sample, "bhar_3m", ["sic2"], "industry")

    assert len(adjusted) == len(sample)
    assert "bhar_3m_industry" in adjusted.columns
    assert "bhar_3m_industry_peer_count" in adjusted.columns
    assert adjusted["bhar_3m_industry_peer_count"].ge(0).all()


def test_build_results_contains_all_panels_and_benchmarks() -> None:
    sample = _sample_frame()
    for outcome in ["bhar_1m", "bhar_3m", "bhar_6m", "bhar_12m"]:
        sample[f"{outcome}_raw"] = sample[outcome]
        sample[f"{outcome}_raw_peer_count"] = pd.NA
        sample = sample.merge(
            _add_peer_adjusted_outcome(sample, outcome, ["sic2"], "industry"),
            on="filing_id",
            how="left",
        )
        sample = sample.merge(
            _add_peer_adjusted_outcome(sample, outcome, ["filing_year", "sic2"], "industry_year"),
            on="filing_id",
            how="left",
        )
        sample = sample.merge(
            _add_peer_adjusted_outcome(
                sample, outcome, ["filing_year", "size_bucket", "mom_bucket"], "characteristic"
            ),
            on="filing_id",
            how="left",
        )

    table_df, figure_df = _build_results(sample)

    assert set(table_df["panel"]) == {
        "BHAR[+2,+21]",
        "BHAR[+2,+63]",
        "BHAR[+2,+126]",
        "BHAR[+2,+252]",
    }
    assert set(figure_df["benchmark_label"]) == {
        "Raw BHAR",
        "Industry-adjusted",
        "Industry-year-adjusted",
        "Characteristic-adjusted",
    }
