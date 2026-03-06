from __future__ import annotations

import csv
from pathlib import Path

from semantic_ai_washing.data.index_sec_filings import (
    ACTIVE_SOURCE_WINDOW_ID,
    HISTORICAL_SOURCE_WINDOW_ID,
    build_index_rows,
    build_source_windows,
    build_summary_report,
    write_index_csv,
)


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("filing body", encoding="utf-8")


def test_build_index_rows_emits_contract_columns(tmp_path):
    root = tmp_path / "sec_root"
    _touch(root / "2021" / "QTR1" / "20210325_10-K_edgar_data_1832010_0001.txt")
    _touch(root / "2024" / "QTR2" / "20240510_10-Q_edgar_data_1327273_0002.txt")
    _touch(root / "2024" / "QTR2" / "README.txt")

    rows, meta = build_index_rows(root)

    assert len(rows) == 2
    assert meta["scanned_count"] == 3
    assert meta["unmatched_count"] == 1

    first = rows[0]
    assert first["path"] == "2021/QTR1/20210325_10-K_edgar_data_1832010_0001.txt"
    assert first["quarter"] == 1
    assert first["source_root"] == "env:SEC_SOURCE_DIR"
    assert first["source_window_id"] == ACTIVE_SOURCE_WINDOW_ID


def test_source_windows_and_summary_capture_historical_availability(tmp_path):
    root = tmp_path / "sec_root"
    _touch(root / "2020" / "QTR4" / "20201231_10-K_edgar_data_1000_0003.txt")
    _touch(root / "2021" / "QTR1" / "20210325_10-K_edgar_data_1832010_0001.txt")
    _touch(root / "2024" / "QTR2" / "20240510_10-Q_edgar_data_1327273_0002.txt")

    rows, meta = build_index_rows(root)
    windows = build_source_windows(rows, source_root_name=root.name)
    summary = build_summary_report(
        rows,
        scan_meta=meta,
        source_windows=windows,
        source_root_name=root.name,
        output_csv="data/metadata/available_filings_index.csv",
    )

    active_window = windows["windows"][0]
    historical_window = windows["windows"][1]

    assert active_window["source_window_id"] == ACTIVE_SOURCE_WINDOW_ID
    assert active_window["availability_status"] == "incomplete"
    assert historical_window["source_window_id"] == HISTORICAL_SOURCE_WINDOW_ID
    assert historical_window["availability_status"] == "available_for_activation"
    assert summary["year_counts"] == {"2020": 1, "2021": 1, "2024": 1}


def test_write_index_csv_persists_expected_columns(tmp_path):
    rows = [
        {
            "cik": "1832010",
            "year": 2021,
            "quarter": 1,
            "form": "10-K",
            "filename": "20210325_10-K_edgar_data_1832010_0001.txt",
            "path": "2021/QTR1/20210325_10-K_edgar_data_1832010_0001.txt",
            "source_root": "env:SEC_SOURCE_DIR",
            "index_timestamp": "2026-03-05T00:00:00+00:00",
            "source_window_id": ACTIVE_SOURCE_WINDOW_ID,
        }
    ]
    output = tmp_path / "data" / "metadata" / "available_filings_index.csv"

    write_index_csv(rows, str(output))

    with output.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        loaded_rows = list(reader)

    assert reader.fieldnames == [
        "cik",
        "year",
        "quarter",
        "form",
        "filename",
        "path",
        "source_root",
        "index_timestamp",
        "source_window_id",
    ]
    assert loaded_rows[0]["path"] == rows[0]["path"]
    assert loaded_rows[0]["source_window_id"] == ACTIVE_SOURCE_WINDOW_ID
