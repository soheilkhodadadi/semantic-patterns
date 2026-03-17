from pathlib import Path

import pandas as pd

from semantic_ai_washing.patents.build_company_lookup import build_lookup, load_company_source


def test_load_company_source_accepts_cik_only_input(tmp_path: Path):
    src = tmp_path / "company_list.csv"
    pd.DataFrame({"cik": ["1234", "0005678"]}).to_csv(src, index=False)

    base, aliases = load_company_source(str(src))

    assert base["cik"].tolist() == ["0000001234", "0000005678"]
    assert base["name"].tolist() == ["", ""]
    assert aliases.empty


def test_build_lookup_prefers_base_then_crosswalk_then_ticker_map():
    base = pd.DataFrame(
        {
            "cik": ["0000001234", "0000005678", "0000009999"],
            "name": ["Base Co", "", ""],
            "ticker": ["", "", ""],
            "gvkey": ["", "", ""],
            "sic": [pd.NA, pd.NA, pd.NA],
        }
    )
    crosswalk = pd.DataFrame(
        {
            "cik": ["0000001234", "0000005678"],
            "gvkey": ["1001", "1002"],
            "ticker_comp": ["BASE", "CROSS"],
            "name": ["Crosswalk Co", "Crosswalk Only"],
            "sic": [3571, 7370],
        }
    )
    ticker_map = pd.DataFrame(
        {
            "CIK": ["0000005678", "0000009999"],
            "Ticker": ["TICK", "ONLYMAP"],
            "Name": ["Ticker Map Co", "Map Only Co"],
            "SIC": [7371, 2834],
        }
    )

    lookup, aliases = build_lookup(base, crosswalk, ticker_map)
    lookup = lookup.set_index("cik")

    assert lookup.loc["0000001234", "name"] == "Base Co"
    assert lookup.loc["0000001234", "ticker"] == "BASE"
    assert lookup.loc["0000005678", "name"] == "Crosswalk Only"
    assert lookup.loc["0000009999", "name"] == "Map Only Co"
    assert "Crosswalk Co" in set(aliases["alias"])
    assert "Ticker Map Co" in set(aliases["alias"])
