from __future__ import annotations

import csv
from pathlib import Path

from semantic_ai_washing.patents.extract_sec_header_company_names import (
    extract_sec_header_company_names,
    main,
    parse_header_lines,
)


def _write_filing(path: Path, *, cik: str, name: str, former_names: list[str], form: str) -> None:
    lines = [
        f"CONFORMED SUBMISSION TYPE:\t{form}",
        "FILED AS OF DATE:\t\t20250103",
        f"\t\tCOMPANY CONFORMED NAME:\t\t\t{name}",
        f"\t\tCENTRAL INDEX KEY:\t\t\t{cik}",
        "\t\tSTANDARD INDUSTRIAL CLASSIFICATION:\tTEST",
    ]
    for former in former_names:
        lines.append(f"\t\tFORMER CONFORMED NAME:\t{former}")
    lines.append("")
    lines.append("Body text starts here.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def test_parse_header_lines_extracts_current_and_former_names():
    lines = [
        "CONFORMED SUBMISSION TYPE:\t10-K",
        "FILED AS OF DATE:\t\t20250103",
        "\t\tCOMPANY CONFORMED NAME:\t\t\tKHEOBA CORP.",
        "\t\tCENTRAL INDEX KEY:\t\t\t0001909770",
        "\t\tFORMER CONFORMED NAME:\tKHEOBA HOLDINGS INC.",
        "\t\tFORMER CONFORMED NAME:\tKHEOBA HOLDINGS INC.",
        "\t\tFORMER CONFORMED NAME:\tKHEOBA GROUP LTD.",
    ]

    record = parse_header_lines(lines, source_file="QTR1/example.txt")

    assert len(record.companies) == 1
    company = record.companies[0]
    assert company.cik == "0001909770"
    assert company.name == "KHEOBA CORP."
    assert record.filing_date == "20250103"
    assert record.submission_type == "10-K"
    assert company.normalized_former_names() == [
        "KHEOBA HOLDINGS INC.",
        "KHEOBA GROUP LTD.",
    ]


def test_parse_header_lines_emits_multiple_company_blocks():
    lines = [
        "CONFORMED SUBMISSION TYPE:\t10-K",
        "FILED AS OF DATE:\t\t20250331",
        "\t\tCOMPANY CONFORMED NAME:\t\t\tFrontier Funds",
        "\t\tCENTRAL INDEX KEY:\t\t\t0001261379",
        "\t\tCOMPANY CONFORMED NAME:\t\t\tFrontier Heritage Fund",
        "\t\tCENTRAL INDEX KEY:\t\t\t0001389123",
        "\t\tCOMPANY CONFORMED NAME:\t\t\tFrontier Masters Fund",
        "\t\tCENTRAL INDEX KEY:\t\t\t0001450722",
    ]

    record = parse_header_lines(lines, source_file="QTR1/multi.txt")

    assert [company.cik for company in record.companies] == [
        "0001261379",
        "0001389123",
        "0001450722",
    ]
    assert [company.name for company in record.companies] == [
        "Frontier Funds",
        "Frontier Heritage Fund",
        "Frontier Masters Fund",
    ]


def test_extract_sec_header_company_names_filters_non_10k_and_emits_alias_rows(tmp_path: Path):
    annual = tmp_path / "2025" / "QTR1" / "annual.txt"
    quarter = tmp_path / "2025" / "QTR1" / "quarterly.txt"
    _write_filing(
        annual,
        cik="0001909770",
        name="KHEOBA CORP.",
        former_names=["KHEOBA HOLDINGS INC.", "KHEOBA GROUP LTD."],
        form="10-K",
    )
    _write_filing(
        quarter,
        cik="0002000762",
        name="GMTech Inc.",
        former_names=["GM TECHNOLOGIES INC."],
        form="10-Q",
    )

    rows, records, skipped = extract_sec_header_company_names(
        [(annual, "2025/QTR1/annual.txt"), (quarter, "2025/QTR1/quarterly.txt")]
    )

    assert len(records) == 1
    assert len(skipped) == 1
    assert skipped[0]["reason"] == "form_filtered"
    assert [row["record_type"] for row in rows] == [
        "current_name",
        "former_name",
        "former_name",
    ]
    assert rows[0]["cik"] == "0001909770"
    assert rows[0]["name"] == "KHEOBA CORP."
    assert rows[0]["former_names"] == "KHEOBA HOLDINGS INC.|KHEOBA GROUP LTD."
    assert {row["alias"] for row in rows[1:]} == {
        "KHEOBA HOLDINGS INC.",
        "KHEOBA GROUP LTD.",
    }


def test_cli_scans_root_and_accepts_relative_source_files(tmp_path: Path):
    root = tmp_path / "2025"
    annual = root / "QTR1" / "20250103_10-K_example.txt"
    _write_filing(
        annual,
        cik="0001909770",
        name="KHEOBA CORP.",
        former_names=["KHEOBA HOLDINGS INC."],
        form="10-K",
    )
    out_csv = tmp_path / "out.csv"

    exit_code = main(["--root", str(root), "--out-csv", str(out_csv)])
    assert exit_code == 0

    with out_csv.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert rows[0]["cik"] == "0001909770"
    assert rows[0]["record_type"] == "current_name"
    assert rows[1]["record_type"] == "former_name"

    out_csv_2 = tmp_path / "out_2.csv"
    exit_code = main(
        [
            "--root",
            str(root),
            "--source-file",
            "QTR1/20250103_10-K_example.txt",
            "--out-csv",
            str(out_csv_2),
        ]
    )
    assert exit_code == 0
    with out_csv_2.open(encoding="utf-8") as handle:
        rows_2 = list(csv.DictReader(handle))
    assert len(rows_2) == 2
