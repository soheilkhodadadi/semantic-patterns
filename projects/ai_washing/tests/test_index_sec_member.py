from __future__ import annotations

import csv
from pathlib import Path

from ai_washing_member.data.index_sec_filings import (
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


def test_member_index_rows_emits_contract_columns(tmp_path: Path) -> None:
    root = tmp_path / "sec_root"
    _touch(root / "2021" / "QTR1" / "20210325_10-K_edgar_data_1832010_0001.txt")
    _touch(root / "2024" / "QTR2" / "20240510_10-Q_edgar_data_1327273_0002.txt")
    _touch(root / "2024" / "QTR2" / "README.txt")

    rows, meta = build_index_rows(root)

    assert len(rows) == 2
    assert meta["scanned_count"] == 3
    assert meta["unmatched_count"] == 1
    assert rows[0]["source_window_id"] == ACTIVE_SOURCE_WINDOW_ID


def test_member_source_windows_and_csv_contract(tmp_path: Path) -> None:
    root = tmp_path / "sec_root"
    _touch(root / "2020" / "QTR4" / "20201231_10-K_edgar_data_1000_0003.txt")
    _touch(root / "2021" / "QTR1" / "20210325_10-K_edgar_data_1832010_0001.txt")
    rows, meta = build_index_rows(root)
    windows = build_source_windows(rows, source_root_name=root.name)
    summary = build_summary_report(
        rows,
        scan_meta=meta,
        source_windows=windows,
        source_root_name=root.name,
        output_csv="data/metadata/available_filings_index.csv",
    )
    output = tmp_path / "data" / "metadata" / "available_filings_index.csv"
    write_index_csv(rows, str(output))

    assert windows["windows"][1]["source_window_id"] == HISTORICAL_SOURCE_WINDOW_ID
    assert summary["year_counts"]["2020"] == 1
    with output.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        loaded_rows = list(reader)
    assert loaded_rows[0]["source_window_id"] in {
        ACTIVE_SOURCE_WINDOW_ID,
        HISTORICAL_SOURCE_WINDOW_ID,
    }
