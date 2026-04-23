from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.publication_runs.test_22_analyst_monitoring_interaction import (
    _load_current_coverage,
    _prepare_sample,
)


def test_load_current_coverage_uses_snapshot_year(tmp_path) -> None:
    source = tmp_path / 'analyst.parquet'
    df = pd.DataFrame(
        {
            'ticker': ['ABC'],
            'ibes_snapshot_year': [2021],
            'log_analyst_coverage_lead1': [1.5],
            'numest': [5],
            'statpers': pd.to_datetime(['2021-12-15']),
        }
    )
    df.to_parquet(source, index=False)
    out = _load_current_coverage(source)
    assert out.loc[0, 'year'] == 2021
    assert out.loc[0, 'log_analyst_coverage_t'] == 1.5


def test_prepare_sample_builds_high_coverage_interaction() -> None:
    panel = pd.DataFrame(
        {
            'cik': ['0001', '0001', '0002', '0002'],
            'ticker': ['ABC', 'ABC', 'XYZ', 'XYZ'],
            'year': [2020, 2021, 2020, 2021],
            'any_ai_talk': [1, 1, 1, 1],
            'PatentMismatch': [1, 0, 0, 1],
            'AI_Focus': [1.0, 1.1, 0.8, 0.9],
            'ln_assets': [2.0, 2.0, 1.5, 1.5],
            'leverage': [0.3, 0.3, 0.2, 0.2],
            'cash': [0.1, 0.1, 0.2, 0.2],
            'roa': [0.05, 0.06, 0.04, 0.03],
            'log_patents_ai_lead1': [0.0, 0.5, 0.1, 0.2],
        }
    )
    coverage = pd.DataFrame(
        {
            'ticker': ['ABC', 'XYZ'],
            'year': [2020, 2020],
            'log_analyst_coverage_t': [2.0, 1.0],
            'numest': [7, 3],
            'statpers': pd.to_datetime(['2020-12-15', '2020-12-15']),
        }
    )
    merged, summary = _prepare_sample(panel, coverage)
    assert summary['coverage_nonmissing'] == 2
    row = merged.loc[(merged['ticker'] == 'ABC') & (merged['year'] == 2020)].iloc[0]
    assert row['HighAnalystCoverage'] == 1
    assert row['PM_x_HighCoverage'] == 1
