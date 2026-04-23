from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.publication_runs.test_32_market_reaction_in_issue_windows import (
    _build_table,
    _prepare_sample,
)


def test_prepare_sample_counts_issue_window_rows() -> None:
    event_panel = pd.DataFrame(
        {
            'cik': ['1', '1', '2'],
            'filing_year': [2021, 2022, 2021],
            'car_m1_p1': [0.01, 0.02, 0.03],
            'bhar_3m': [0.1, 0.2, 0.3],
            'bhar_12m': [0.2, 0.3, 0.4],
            'filing_events': [1, 1, 1],
        }
    )
    annual_panel = pd.DataFrame(
        {
            'cik': ['1', '1', '2'],
            'year': [2021, 2022, 2021],
            'equity_issue_lead1': [1.0, 0.0, 0.0],
            'PatentMismatch': [1, 0, 0],
            'LowCredibility': [1, 0, 0],
            'ApplicationMismatch': [1, 0, 0],
            'A_S': [0.2, 0.4, 0.1],
            'AI_Focus': [1.0, 1.2, 0.5],
            'ln_assets': [2.0, 2.1, 1.7],
            'cash': [0.1, 0.1, 0.2],
            'leverage': [0.2, 0.2, 0.1],
            'roa': [0.03, 0.04, 0.02],
            'nonbig': [False, False, True],
        }
    )
    sample, summary = _prepare_sample(event_panel, annual_panel)
    assert summary['filing_year_rows'] == 3
    assert summary['issue_window_rows'] == 1
    assert summary['issue_window_firms'] == 1


def test_build_table_includes_panel_headers() -> None:
    rows = []
    for subset in ['all', 'nonbig']:
        for outcome in ['car_m1_p1', 'bhar_3m', 'bhar_12m']:
            for predictor in ['PatentMismatch', 'LowCredibility', 'ApplicationMismatch']:
                rows.append(
                    {
                        'subset': subset,
                        'outcome': outcome,
                        'predictor': predictor,
                        'nobs': 100,
                        'outcome_mean': 0.1,
                        'params': {
                            predictor: -0.02,
                            'equity_issue_lead1': 0.01,
                            f'{predictor}:equity_issue_lead1': 0.05,
                        },
                        'bse': {
                            predictor: 0.01,
                            'equity_issue_lead1': 0.02,
                            f'{predictor}:equity_issue_lead1': 0.02,
                        },
                        'pvalues': {
                            predictor: 0.05,
                            'equity_issue_lead1': 0.60,
                            f'{predictor}:equity_issue_lead1': 0.03,
                        },
                    }
                )
    table_df, _ = _build_table(rows)
    assert table_df.iloc[0]['Panel'].startswith('Panel A')
    assert any(str(value).startswith('Panel B') for value in table_df['Panel'])
