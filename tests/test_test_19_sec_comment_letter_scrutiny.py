from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.publication_runs.test_19_sec_comment_letter_scrutiny import (
    _aggregate_events,
    _normalize_cik,
    _normalize_ticker,
    _match_comment_letters,
    _prepare_sample,
)
from semantic_ai_washing.analysis.publication_runs.test_16_construct_variant_screen import (
    _add_construct_variants,
)


def _panel_frame() -> pd.DataFrame:
    rows = []
    for year in range(2021, 2025):
        rows.append(
            {
                "cik": "1000",
                "ticker": "AAA",
                "name": "Alpha",
                "year": year,
                "sic": 3571,
                "sic2": 35,
                "any_ai_talk": 1,
                "A_S": 0.6,
                "share_S": 0.30,
                "SpecShare": 0.30,
                "AI_Focus": 0.5,
                "ln_assets": 8.0,
                "cash": 0.12,
                "leverage": 0.22,
                "roa": 0.05,
                "log_patents_ai_lead0": 0.10,
                "log_applications_ai_lead0": 0.12,
            }
        )
    for year in range(2021, 2025):
        rows.append(
            {
                "cik": "2000",
                "ticker": "BBB",
                "name": "Beta",
                "year": year,
                "sic": 3571,
                "sic2": 35,
                "any_ai_talk": 1,
                "A_S": 0.2,
                "share_S": 0.10,
                "SpecShare": 0.10,
                "AI_Focus": 0.4,
                "ln_assets": 8.3,
                "cash": 0.10,
                "leverage": 0.25,
                "roa": 0.07,
                "log_patents_ai_lead0": 0.25,
                "log_applications_ai_lead0": 0.20,
            }
        )
    panel = pd.DataFrame(rows)
    return panel


def _raw_comments() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "file_date": pd.Timestamp("2023-05-10"),
                "company_name": "Alpha",
                "best_edgar_ticker": "AAA",
                "list_ciks_reclet": "0000001000",
                "list_cl_issue_phrase": "Artificial intelligence disclosure",
                "list_cl_issue_taxgrp": "Whole Letter Description",
                "cl_text": "Please explain your artificial intelligence claims in greater detail.",
            },
            {
                "file_date": pd.Timestamp("2024-06-12"),
                "company_name": "Beta",
                "best_edgar_ticker": "BBB",
                "list_ciks_reclet": "",
                "list_cl_issue_phrase": "",
                "list_cl_issue_taxgrp": "",
                "cl_text": "The Office of Technology reviewed your AI claims.",
            },
        ]
    )


def test_match_comment_letters_uses_cik_then_ticker_fallback() -> None:
    panel = _add_construct_variants(_panel_frame()).copy()
    panel["cik"] = panel["cik"].map(_normalize_cik)
    panel["ticker"] = panel["ticker"].map(_normalize_ticker)

    matched, summary = _match_comment_letters(_raw_comments(), panel)

    assert summary["matched_rows"] == 2
    assert set(matched["match_method"]) == {"cik_list", "ticker_fallback"}
    assert matched["ai_phrase_narrow"].sum() >= 1
    assert matched["ai_phrase_broad"].sum() == 2


def test_prepare_sample_builds_t_t1_windows() -> None:
    panel = _add_construct_variants(_panel_frame()).copy()
    panel["cik"] = panel["cik"].map(_normalize_cik)
    panel["ticker"] = panel["ticker"].map(_normalize_ticker)
    matched, _summary = _match_comment_letters(_raw_comments(), panel)
    event_panel, _counts = _aggregate_events(matched)
    sample, sample_summary = _prepare_sample(panel, event_panel)

    alpha_2022 = sample.loc[(sample["cik"] == "0000001000") & (sample["year"] == 2022)].iloc[0]
    alpha_2023 = sample.loc[(sample["cik"] == "0000001000") & (sample["year"] == 2023)].iloc[0]
    beta_2023 = sample.loc[(sample["cik"] == "0000002000") & (sample["year"] == 2023)].iloc[0]

    assert alpha_2022["ai_comment_narrow_t_t1"] == 1
    assert alpha_2023["ai_comment_narrow_t_t1"] == 1
    assert beta_2023["ai_comment_broad_t_t1"] == 1
    assert sample_summary["outcome_counts"]["ai_comment_broad_t_t1"] >= 1
