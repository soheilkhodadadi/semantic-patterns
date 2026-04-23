from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.publication_runs.test_24_scitech_appointment_response import (
    _prepare_events,
    _prepare_sample,
)


def test_prepare_events_flags_technology_lead_titles() -> None:
    raw = pd.DataFrame(
        {
            "company_fkey": ["0000000001", "0000000001", "0000000002"],
            "action": ["Appointed", "Appointed", "Appointed"],
            "title_report": [
                "Chief Technology Officer",
                "Director",
                "Chief Medical Officer",
            ],
            "title_standard": [None, None, None],
            "is_scitech_pers": [1, 1, 1],
            "is_c_level": [1, 0, 1],
            "is_bdmem_pers": [0, 1, 0],
            "eff_date": pd.to_datetime(["2021-01-10", "2021-02-01", None]),
            "file_date": pd.to_datetime(["2021-01-11", "2021-02-03", "2021-03-01"]),
        }
    )
    event_panel, summary = _prepare_events(raw)
    assert summary["tech_lead_rows"] == 1
    row = event_panel.loc[(event_panel["cik"] == "0000000001") & (event_panel["year"] == 2021)].iloc[0]
    assert row["scitech_appoint"] == 1
    assert row["c_level_scitech_appoint"] == 1
    assert row["tech_lead_appoint"] == 1
    assert row["board_scitech_appoint"] == 1


def test_prepare_sample_builds_future_windows() -> None:
    panel = pd.DataFrame(
        {
            "cik": ["0001", "0001", "0001"],
            "year": [2020, 2021, 2022],
            "any_ai_talk": [1, 1, 1],
            "PatentMismatch": [1, 0, 1],
            "LowCredibility": [1, 0, 1],
            "A_S": [0.5, 0.6, 0.7],
            "AI_Focus": [1.0, 1.0, 1.0],
            "ln_assets": [2.0, 2.0, 2.0],
            "cash": [0.1, 0.1, 0.1],
            "leverage": [0.2, 0.2, 0.2],
            "roa": [0.05, 0.04, 0.03],
            "sic2": [35, 35, 35],
        }
    )
    events = pd.DataFrame(
        {
            "cik": ["0001", "0001"],
            "year": [2021, 2022],
            "scitech_appoint": [1, 0],
            "c_level_scitech_appoint": [0, 1],
            "tech_lead_appoint": [1, 0],
            "board_scitech_appoint": [0, 0],
        }
    )
    sample, summary = _prepare_sample(panel, events)
    assert summary["t1_t2_any_scitech"] == 1
    row = sample.loc[sample["year"].eq(2020)].iloc[0]
    assert row["scitech_appoint_lead1"] == 1
    assert row["c_level_scitech_appoint_lead2"] == 1
    assert row["tech_lead_appoint_t1_t2"] == 1
