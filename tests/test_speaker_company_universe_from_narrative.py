from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from semantic_ai_washing.data.build_speaker_company_universe_from_narrative import (
    build_speaker_company_universe,
)


def test_build_speaker_company_universe_combines_and_filters_years(tmp_path: Path) -> None:
    old_path = tmp_path / "old.parquet"
    refresh_path = tmp_path / "refresh.parquet"
    output_csv = tmp_path / "company_list.csv"
    output_report = tmp_path / "report.json"

    pd.DataFrame(
        [
            {"source_cik": "1001", "source_year": 2019},
            {"source_cik": "1001", "source_year": 2020},
            {"source_cik": "1002", "source_year": 2020},
        ]
    ).to_parquet(old_path, index=False)
    pd.DataFrame(
        [
            {"source_cik": "1001", "source_year": 2025},
            {"source_cik": "0000001003", "source_year": 2025},
        ]
    ).to_parquet(refresh_path, index=False)

    summary = build_speaker_company_universe(
        [old_path, refresh_path],
        output_csv=output_csv,
        output_report=output_report,
        min_year=2020,
        max_year=2025,
    )

    out = pd.read_csv(output_csv, dtype={"cik": str})
    assert out["cik"].tolist() == ["0000001001", "0000001002", "0000001003"]
    assert out.loc[out["cik"] == "0000001001", "years_present"].item() == "2020,2025"
    assert bool(out.loc[out["cik"] == "0000001001", "year_2020_present"].item()) is True
    assert bool(out.loc[out["cik"] == "0000001001", "year_2025_present"].item()) is True
    assert summary["firm_count"] == 3
    report = json.loads(output_report.read_text(encoding="utf-8"))
    assert report["year_span"] == [2020, 2025]


def test_build_speaker_company_universe_requires_expected_columns(tmp_path: Path) -> None:
    bad_path = tmp_path / "bad.csv"
    pd.DataFrame([{"cik": "1001", "year": 2025}]).to_csv(bad_path, index=False)

    try:
        build_speaker_company_universe([bad_path], output_csv=tmp_path / "out.csv")
    except ValueError as exc:
        assert "source_cik" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing narrative columns")
