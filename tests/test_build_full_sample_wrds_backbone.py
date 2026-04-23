from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.build_full_sample_wrds_backbone import (
    build_firm_year_rows,
    load_crosswalk,
    load_narrative,
)


def test_load_narrative_normalizes_source_columns(tmp_path) -> None:
    path = tmp_path / 'narrative.parquet'
    frame = pd.DataFrame(
        {
            'source_cik': ['123', '0000000456'],
            'source_year': [2024, 2025],
            'source_window_id': ['w1', 'w2'],
            'model_id': ['m1', 'm2'],
            'ai_total': [1, 2],
            'doc_count': [1, 1],
            'n_A': [1, 0],
            'n_S': [0, 1],
            'n_I': [0, 1],
            'n_total': [1, 2],
            'AI_Focus': [0.1, 0.2],
            'log_1p_A': [0.1, 0.0],
            'log_1p_S': [0.0, 0.1],
            'SpecShare': [0.0, 1.0],
            'CredAI': [0.1, -0.2],
            'A_S': [0.1, 0.0],
        }
    )
    frame.to_parquet(path, index=False)

    out = load_narrative(path)

    assert out['cik'].tolist() == ['0000000123', '0000000456']
    assert out['year'].tolist() == [2024, 2025]


def test_load_narrative_accepts_expanded_ever_speaker_schema(tmp_path) -> None:
    path = tmp_path / 'expanded.parquet'
    frame = pd.DataFrame(
        {
            'cik': ['123'],
            'year': [2024],
            'n_A': [0],
            'n_S': [0],
            'n_I': [0],
            'n_total': [0],
            'ai_total': [0],
            'any_ai_talk': [0],
        }
    )
    frame.to_parquet(path, index=False)

    out = load_narrative(path)

    assert out['cik'].tolist() == ['0000000123']
    assert out['year'].tolist() == [2024]
    assert out['source_window_id'].tolist() == ['']
    assert out['model_id'].tolist() == ['']
    assert out['CredAI'].tolist() == [0.0]


def test_load_narrative_requires_firm_year_keys(tmp_path) -> None:
    path = tmp_path / 'broken.parquet'
    pd.DataFrame({'foo': ['bar']}).to_parquet(path, index=False)

    try:
        load_narrative(path)
    except ValueError as exc:
        assert 'cik' in str(exc)
        assert 'year' in str(exc)
    else:
        raise AssertionError('Expected ValueError for missing firm-year keys')


def test_load_crosswalk_and_build_rows(tmp_path) -> None:
    crosswalk_path = tmp_path / 'crosswalk.csv'
    pd.DataFrame(
        {
            'cik': ['123', '456'],
            'gvkey': ['1001', '1002'],
            'sic': ['3571', '3674'],
        }
    ).to_csv(crosswalk_path, index=False)

    narrative = pd.DataFrame(
        {
            'cik': ['0000000123', '0000000456'],
            'year': [2024, 2025],
            'source_window_id': ['w1', 'w2'],
            'model_id': ['m1', 'm2'],
            'ai_total': [1, 2],
            'doc_count': [1, 1],
            'n_A': [1, 0],
            'n_S': [0, 1],
            'n_I': [0, 1],
            'n_total': [1, 2],
            'AI_Focus': [0.1, 0.2],
            'log_1p_A': [0.1, 0.0],
            'log_1p_S': [0.0, 0.1],
            'SpecShare': [0.0, 1.0],
            'CredAI': [0.1, -0.2],
            'A_S': [0.1, 0.0],
        }
    )

    crosswalk = load_crosswalk(crosswalk_path)
    rows = build_firm_year_rows(narrative, crosswalk)

    assert rows[0].gvkey == '1001'
    assert rows[1].sic == '3674'
