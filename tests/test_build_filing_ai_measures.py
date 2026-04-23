from __future__ import annotations

import csv
from pathlib import Path

from semantic_ai_washing.analysis.build_filing_ai_measures import build_filing_ai_measures


SPINE_COLUMNS = [
    "filing_id",
    "source_filename",
    "source_path",
    "filing_date",
    "filing_year",
    "form_type",
    "cik",
    "accession_number",
    "gvkey",
    "ticker_comp",
    "issuer_name",
    "sic",
]


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_build_filing_ai_measures_counts_labels_and_flags(tmp_path: Path) -> None:
    classified_one = tmp_path / "20221129_10-K_edgar_data_111_000111-22-000001_classified.csv"
    classified_one.write_text(
        "sentence,label_pred\n"
        "A,Actionable\n"
        "B,Speculative\n"
        "C,Irrelevant\n"
        "D,Unknown\n",
        encoding="utf-8",
    )

    classified_two = tmp_path / "20230110_10-K_edgar_data_222_000222-23-000002_classified.csv"
    classified_two.write_text(
        "sentence,label_pred\n"
        "E,Actionable\n"
        "F,Actionable\n",
        encoding="utf-8",
    )

    spine = tmp_path / "filing_event_spine.csv"
    write_csv(
        spine,
        SPINE_COLUMNS,
        [
            {
                "filing_id": "f1",
                "source_filename": classified_one.name,
                "source_path": str(classified_one),
                "filing_date": "20221129",
                "filing_year": "2022",
                "form_type": "10-K",
                "cik": "0000000111",
                "accession_number": "000111-22-000001",
                "gvkey": "001111",
                "ticker_comp": "ONE",
                "issuer_name": "One Inc",
                "sic": "7372",
            },
            {
                "filing_id": "f2",
                "source_filename": classified_two.name,
                "source_path": str(classified_two),
                "filing_date": "20230110",
                "filing_year": "2023",
                "form_type": "10-K",
                "cik": "0000000222",
                "accession_number": "000222-23-000002",
                "gvkey": "002222",
                "ticker_comp": "TWO",
                "issuer_name": "Two Inc",
                "sic": "7372",
            },
        ],
    )

    rows, report = build_filing_ai_measures(spine)

    assert len(rows) == 2
    first, second = rows

    assert first["sentence_count"] == "4"
    assert first["n_actionable"] == "1"
    assert first["n_speculative"] == "1"
    assert first["n_irrelevant"] == "1"
    assert first["n_other"] == "1"
    assert first["n_ai_total"] == "3"
    assert first["share_actionable"] == "0.333333"
    assert first["share_speculative"] == "0.333333"
    assert first["share_irrelevant"] == "0.333333"
    assert first["post_chatgpt"] == "0"

    assert second["sentence_count"] == "2"
    assert second["n_actionable"] == "2"
    assert second["n_speculative"] == "0"
    assert second["n_irrelevant"] == "0"
    assert second["n_other"] == "0"
    assert second["n_ai_total"] == "2"
    assert second["share_actionable"] == "1.000000"
    assert second["any_actionable"] == "1"
    assert second["post_chatgpt"] == "1"

    assert report["row_count"] == 2
    assert report["totals"]["sentence_count"] == 6
    assert report["totals"]["n_actionable"] == 3
    assert report["totals"]["n_speculative"] == 1
    assert report["totals"]["n_irrelevant"] == 1
    assert report["totals"]["n_other"] == 1
    assert report["post_chatgpt_filing_count"] == 1


def test_build_filing_ai_measures_handles_empty_classified_file(tmp_path: Path) -> None:
    classified = tmp_path / "20240110_10-K_edgar_data_333_000333-24-000003_classified.csv"
    classified.write_text("sentence,label_pred\n", encoding="utf-8")

    spine = tmp_path / "filing_event_spine.csv"
    write_csv(
        spine,
        SPINE_COLUMNS,
        [
            {
                "filing_id": "f3",
                "source_filename": classified.name,
                "source_path": str(classified),
                "filing_date": "20240110",
                "filing_year": "2024",
                "form_type": "10-K",
                "cik": "0000000333",
                "accession_number": "000333-24-000003",
                "gvkey": "003333",
                "ticker_comp": "THR",
                "issuer_name": "Three Inc",
                "sic": "7372",
            }
        ],
    )

    rows, report = build_filing_ai_measures(spine)
    assert rows[0]["sentence_count"] == "0"
    assert rows[0]["n_ai_total"] == "0"
    assert rows[0]["share_actionable"] == "0.000000"
    assert report["totals"]["sentence_count"] == 0
