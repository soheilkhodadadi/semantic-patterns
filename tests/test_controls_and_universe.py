from pathlib import Path

import pandas as pd

from semantic_ai_washing.data.build_active_filing_company_universe import build_universe
from semantic_ai_washing.data.pull_compustat_controls import load_company_list


def test_load_company_list_accepts_cik_only_input(tmp_path: Path) -> None:
    company_list = tmp_path / "company_list.csv"
    pd.DataFrame({"cik": ["1000209", "0000320193"]}).to_csv(company_list, index=False)

    loaded = load_company_list(str(company_list))

    assert loaded["cik"].tolist() == ["0001000209", "0000320193"]
    assert loaded["name_src"].tolist() == ["", ""]
    assert loaded["ticker_src"].tolist() == ["", ""]


def test_build_universe_filters_to_annual_forms_and_year_window(tmp_path: Path) -> None:
    index_csv = tmp_path / "available_filings_index.csv"
    output_csv = tmp_path / "company_universe.csv"
    pd.DataFrame(
        [
            {"cik": "1001", "year": 2021, "form": "10-K", "source_window_id": "active_2021_2024"},
            {
                "cik": "1001",
                "year": 2022,
                "form": "10-K-A",
                "source_window_id": "active_2021_2024",
            },
            {"cik": "1001", "year": 2023, "form": "10-Q", "source_window_id": "active_2021_2024"},
            {"cik": "1002", "year": 2021, "form": "10-K", "source_window_id": "active_2021_2024"},
            {"cik": "1002", "year": 2022, "form": "10-K", "source_window_id": "active_2021_2024"},
            {"cik": "1002", "year": 2023, "form": "10-K", "source_window_id": "other_window"},
            {"cik": "1002", "year": 2024, "form": "10-K", "source_window_id": "active_2021_2024"},
        ]
    ).to_csv(index_csv, index=False)

    summary = build_universe(
        index_csv=str(index_csv),
        output_csv=str(output_csv),
        source_window_id="active_2021_2024",
        years=[2021, 2022, 2023, 2024],
        forms=["10-K", "10-K-A"],
        require_all_years=False,
    )

    universe = pd.read_csv(output_csv, dtype={"cik": str})

    assert summary["firm_count"] == 2
    assert universe["cik"].tolist() == ["0000001001", "0000001002"]
    assert universe.loc[0, "years_present"] == "2021,2022"
    assert universe.loc[1, "years_present"] == "2021,2022,2024"
    assert universe.loc[0, "annual_filing_count"] == 2
    assert universe.loc[1, "annual_filing_count"] == 3
