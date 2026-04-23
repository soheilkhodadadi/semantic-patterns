from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.publication_runs.test_21_analyst_discernment import (
    _build_analyst_annual,
    _merge_sample,
)


def test_build_analyst_annual_creates_lead1_metrics() -> None:
    raw = pd.DataFrame(
        {
            'ibes_ticker': ['ABC', 'ABC'],
            'statpers': pd.to_datetime(['2020-12-15', '2021-12-20']),
            'statpers_year': [2020, 2021],
            'fpedats': pd.to_datetime(['2021-12-31', '2022-12-31']),
            'numest': [5, 6],
            'numup': [2, 1],
            'numdown': [1, 3],
            'meanest': [2.0, 4.0],
            'stdev': [0.4, 0.8],
        }
    )
    out = _build_analyst_annual(raw)
    assert out['year'].tolist() == [2019, 2020]
    assert 'log_analyst_coverage_lead1' in out.columns
    assert 'analyst_dispersion_scaled_lead1' in out.columns
    assert 'analyst_revision_balance_lead1' in out.columns


def test_merge_sample_tracks_nonmissing_counts() -> None:
    panel = pd.DataFrame(
        {
            'cik': ['0001', '0002'],
            'ticker': ['ABC', 'XYZ'],
            'year': [2020, 2020],
            'any_ai_talk': [1, 1],
        }
    )
    analyst = pd.DataFrame(
        {
            'ticker': ['ABC'],
            'year': [2020],
            'log_analyst_coverage_lead1': [1.5],
            'analyst_dispersion_scaled_lead1': [0.2],
            'analyst_revision_balance_lead1': [0.1],
        }
    )
    merged, summary = _merge_sample(panel, analyst)
    assert len(merged) == 2
    assert summary['coverage_nonmissing'] == 1
    assert summary['dispersion_nonmissing'] == 1
    assert summary['revision_nonmissing'] == 1
