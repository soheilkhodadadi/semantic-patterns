from __future__ import annotations

import csv
from pathlib import Path

from semantic_ai_washing.analysis.build_filing_event_spine import build_event_spine


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_build_event_spine_filters_forms_and_joins_crosswalk(tmp_path: Path) -> None:
    classified_dir = tmp_path / "classified"
    classified_dir.mkdir()

    (classified_dir / "20240131_10-K_edgar_data_12345_00012345-24-000001_classified.csv").write_text(
        "sentence,label_pred\nExample,Actionable\n",
        encoding="utf-8",
    )
    (classified_dir / "20240201_8-K_edgar_data_98765_00098765-24-000002_classified.csv").write_text(
        "sentence,label_pred\nExample,Speculative\n",
        encoding="utf-8",
    )
    (classified_dir / "ignore_me.csv").write_text("x\n", encoding="utf-8")

    crosswalk = tmp_path / "crosswalk.csv"
    write_csv(
        crosswalk,
        ["cik", "gvkey", "ticker_comp", "name", "sic"],
        [
            {
                "cik": "12345",
                "gvkey": "001234",
                "ticker_comp": "AICO",
                "name": "AI Company",
                "sic": "7372",
            }
        ],
    )

    rows, report = build_event_spine(
        classified_dir=classified_dir,
        crosswalk_path=crosswalk,
        forms=("10-K",),
        start_year=2024,
        end_year=2024,
    )

    assert len(rows) == 1
    row = rows[0]
    assert row["form_type"] == "10-K"
    assert row["filing_date"] == "20240131"
    assert row["filing_year"] == "2024"
    assert row["cik"] == "0000012345"
    assert row["gvkey"] == "001234"
    assert row["ticker_comp"] == "AICO"
    assert row["issuer_name"] == "AI Company"
    assert report["row_count"] == 1
    assert report["form_counts"] == {"10-K": 1}
    assert report["year_counts"] == {"2024": 1}
    assert report["crosswalk_match_count"] == 1
    assert report["crosswalk_match_rate"] == 1.0


def test_build_event_spine_supports_scored_classified_filenames(tmp_path: Path) -> None:
    classified_dir = tmp_path / "classified"
    classified_dir.mkdir()
    (classified_dir / "20231215_10-K-A_edgar_data_7654321_0007654321-23-000003_scored_classified.csv").write_text(
        "sentence,label_pred\nExample,Irrelevant\n",
        encoding="utf-8",
    )

    rows, report = build_event_spine(
        classified_dir=classified_dir,
        crosswalk_path=tmp_path / "missing_crosswalk.csv",
        forms=("10-K-A",),
    )

    assert len(rows) == 1
    row = rows[0]
    assert row["form_type"] == "10-K-A"
    assert row["cik"] == "0007654321"
    assert row["accession_number"] == "0007654321-23-000003"
    assert report["crosswalk_match_count"] == 0
