from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.build_refresh_ever_speaker_panel import (
    build_annual_market_features,
    build_controls_from_funda,
    build_ever_speaker_scaffold,
    build_identity_lookup,
    merge_panel,
)


def test_build_identity_lookup_uses_fallback_layers(tmp_path) -> None:
    primary = tmp_path / "primary.csv"
    secondary = tmp_path / "secondary.csv"
    sec = tmp_path / "sec.csv"

    pd.DataFrame(
        [
            {"cik": "0000000001", "name": "Primary Co", "name_clean": "primary", "ticker": "PRI", "gvkey": "1001", "sic": "3571", "name_source": "primary"},
            {"cik": "0000000002", "name": "", "name_clean": "", "ticker": "", "gvkey": "", "sic": "", "name_source": ""},
        ]
    ).to_csv(primary, index=False)
    pd.DataFrame(
        [
            {"cik": "0000000002", "name": "Secondary Co", "name_clean": "secondary", "ticker": "SEC", "gvkey": "1002", "sic": "3572", "name_source": "secondary"},
        ]
    ).to_csv(secondary, index=False)
    pd.DataFrame(
        [
            {"CIK": "3", "Ticker": "THR", "Name": "Third Co", "Exchange": "NYSE", "SIC": "3573"},
        ]
    ).to_csv(sec, index=False)

    lookup = build_identity_lookup(
        ["0000000001", "0000000002", "0000000003"],
        primary_lookup_path=primary,
        secondary_lookup_path=secondary,
        sec_fallback_path=sec,
    )

    row1 = lookup.loc[lookup["cik"] == "0000000001"].iloc[0]
    row2 = lookup.loc[lookup["cik"] == "0000000002"].iloc[0]
    row3 = lookup.loc[lookup["cik"] == "0000000003"].iloc[0]

    assert row1["name"] == "Primary Co"
    assert row1["gvkey"] == "1001"
    assert row2["name"] == "Secondary Co"
    assert row2["gvkey"] == "1002"
    assert row3["name"] == "Third Co"
    assert row3["ticker"] == "THR"
    assert row3["identity_name_source"] == "sec_ticker_list"


def test_build_ever_speaker_scaffold_expands_zero_talk_years(tmp_path) -> None:
    narrative = pd.DataFrame(
        [
            {
                "cik": "0000000001",
                "year": 2024,
                "doc_count": 1,
                "n_total": 2,
                "n_A": 2,
                "n_S": 0,
                "n_I": 0,
                "ai_total": 2,
                "source_window_id": "w2024",
                "model_id": "m2024",
            },
            {
                "cik": "0000000002",
                "year": 2025,
                "doc_count": 1,
                "n_total": 1,
                "n_A": 0,
                "n_S": 1,
                "n_I": 0,
                "ai_total": 1,
                "source_window_id": "w2025",
                "model_id": "m2025",
            },
        ]
    )
    identity = pd.DataFrame(
        [
            {
                "cik": "0000000001",
                "name": "One Co",
                "name_clean": "one",
                "ticker": "ONE",
                "gvkey": "1001",
                "sic": "3571",
                "identity_name_source": "primary",
            },
            {
                "cik": "0000000002",
                "name": "Two Co",
                "name_clean": "two",
                "ticker": "TWO",
                "gvkey": "1002",
                "sic": "3572",
                "identity_name_source": "primary",
            },
        ]
    )
    patents = tmp_path / "patents.csv"
    applications = tmp_path / "applications.csv"
    pd.DataFrame(
        [
            {"cik": "1", "year": 2024, "patents_total": 1, "patents_ai": 1, "ai_share": 1.0},
            {"cik": "2", "year": 2025, "patents_total": 2, "patents_ai": 0, "ai_share": 0.0},
        ]
    ).to_csv(patents, index=False)
    pd.DataFrame(
        [
            {"cik": "1", "year": 2024, "applications_total": 1, "applications_ai": 1, "ai_share_applications": 1.0},
            {"cik": "2", "year": 2025, "applications_total": 3, "applications_ai": 1, "ai_share_applications": 1 / 3},
        ]
    ).to_csv(applications, index=False)

    panel = build_ever_speaker_scaffold(
        narrative,
        start_year=2024,
        end_year=2025,
        identity_lookup=identity,
        patents_path=patents,
        applications_path=applications,
        patent_buffer_years=1,
    )

    assert len(panel) == 4
    assert panel["any_ai_talk"].sum() == 2
    row = panel.loc[(panel["cik"] == "0000000001") & (panel["year"] == 2025)].iloc[0]
    assert row["any_ai_talk"] == 0
    assert row["ai_total"] == 0
    assert row["source_window_id"] == "w2025"
    assert row["model_id"] == "m2025"


def test_build_annual_market_features_compounds_returns() -> None:
    msf = pd.DataFrame(
        [
            {"permno": "1001", "permco": "5001", "date": "2024-01-31", "ret": 0.10, "retx": 0.10, "prc": 10.0, "shrout": 100.0, "vol": 1000.0},
            {"permno": "1001", "permco": "5001", "date": "2024-02-29", "ret": 0.20, "retx": 0.20, "prc": 12.0, "shrout": 100.0, "vol": 1200.0},
            {"permno": "1001", "permco": "5001", "date": "2025-01-31", "ret": 0.05, "retx": 0.05, "prc": 13.0, "shrout": 100.0, "vol": 900.0},
        ]
    )
    msi = pd.DataFrame(
        [
            {"date": "2024-01-31", "vwretd": 0.05, "ewretd": 0.04, "sprtrn": 0.03},
            {"date": "2024-02-29", "vwretd": 0.02, "ewretd": 0.01, "sprtrn": 0.00},
            {"date": "2025-01-31", "vwretd": 0.01, "ewretd": 0.01, "sprtrn": 0.01},
        ]
    )

    annual = build_annual_market_features(msf, msi)
    row_2024 = annual.loc[(annual["permno"] == "1001") & (annual["year"] == 2024)].iloc[0]
    row_2025 = annual.loc[(annual["permno"] == "1001") & (annual["year"] == 2025)].iloc[0]

    assert round(row_2024["annual_ret"], 6) == round((1.1 * 1.2) - 1.0, 6)
    assert round(row_2024["annual_vwretd"], 6) == round((1.05 * 1.02) - 1.0, 6)
    assert row_2024["market_cap_year_end"] == 1200.0
    assert row_2024["firm_age_market"] == 1
    assert row_2025["firm_age_market"] == 2


def test_merge_panel_normalizes_numeric_like_wrds_keys() -> None:
    scaffold = pd.DataFrame(
        [
            {
                "cik": "0000000001",
                "year": 2024,
                "gvkey": "1001",
                "sic": "3571",
                "any_ai_talk": 1,
            }
        ]
    )
    backbone = pd.DataFrame(
        [
            {
                "cik": "0000000001",
                "year": 2024,
                "gvkey": 1001.0,
                "permno": 2002.0,
                "permco": 3003.0,
                "sic": 3571.0,
                "wrds_bridge_status": "matched",
                "valid_candidate_count": 1,
                "linktype": "LC",
                "linkprim": "P",
                "linkdt": "2020-01-01",
                "linkenddt": "",
            }
        ]
    )
    controls = pd.DataFrame([{"gvkey": "1001", "year": 2024, "ln_assets": 9.0}])
    market = pd.DataFrame(
        [{"permno": "2002", "permco": "3003", "year": 2024, "annual_ret": 0.1}]
    )

    panel = merge_panel(scaffold, backbone, controls, market)
    row = panel.iloc[0]

    assert row["gvkey"] == "1001"
    assert row["permno"] == "2002"
    assert row["ln_assets"] == 9.0
    assert row["annual_ret"] == 0.1


def test_build_controls_from_funda_normalizes_zero_padded_gvkey() -> None:
    funda = pd.DataFrame(
        [
            {
                "gvkey": "001004",
                "datadate": "2016-05-31",
                "fyear": 2015,
                "fyr": 5,
                "indfmt": "INDL",
                "consol": "C",
                "datafmt": "STD",
                "popsrc": "D",
                "at": 100.0,
                "sale": 120.0,
                "ib": 10.0,
                "ni": 10.0,
                "che": 20.0,
                "dltt": 30.0,
                "dlc": 5.0,
                "capx": 4.0,
                "xrd": 6.0,
                "emp": 1.0,
            }
        ]
    )

    controls = build_controls_from_funda(funda)

    assert controls.loc[0, "gvkey"] == "1004"
