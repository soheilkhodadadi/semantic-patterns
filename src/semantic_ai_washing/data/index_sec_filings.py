"""Compatibility shim for the member-owned SEC index helpers."""

from __future__ import annotations

from ai_washing_member.data import index_sec_filings as _member

SEC_SOURCE_HINT_FILE = _member.SEC_SOURCE_HINT_FILE
OUTPUT_CSV = _member.OUTPUT_CSV
OUTPUT_SOURCE_WINDOWS = _member.OUTPUT_SOURCE_WINDOWS
OUTPUT_SUMMARY = _member.OUTPUT_SUMMARY
ACTIVE_SOURCE_WINDOW_ID = _member.ACTIVE_SOURCE_WINDOW_ID
HISTORICAL_SOURCE_WINDOW_ID = _member.HISTORICAL_SOURCE_WINDOW_ID
SOURCE_ROOT_REF = _member.SOURCE_ROOT_REF
ACTIVE_YEARS = _member.ACTIVE_YEARS
YEAR_DIR_RE = _member.YEAR_DIR_RE
QTR_DIR_RE = _member.QTR_DIR_RE
now_utc_iso = _member.now_utc_iso
dump_json = _member.dump_json
resolve_sec_source = _member.resolve_sec_source
iter_filing_paths = _member.iter_filing_paths
parse_filename = _member.parse_filename
source_window_id_for_year = _member.source_window_id_for_year
build_index_rows = _member.build_index_rows
build_source_windows = _member.build_source_windows
build_summary_report = _member.build_summary_report
write_index_csv = _member.write_index_csv
parse_args = _member.parse_args
main = _member.main

__all__ = [
    "SEC_SOURCE_HINT_FILE",
    "OUTPUT_CSV",
    "OUTPUT_SOURCE_WINDOWS",
    "OUTPUT_SUMMARY",
    "ACTIVE_SOURCE_WINDOW_ID",
    "HISTORICAL_SOURCE_WINDOW_ID",
    "SOURCE_ROOT_REF",
    "ACTIVE_YEARS",
    "YEAR_DIR_RE",
    "QTR_DIR_RE",
    "now_utc_iso",
    "dump_json",
    "resolve_sec_source",
    "iter_filing_paths",
    "parse_filename",
    "source_window_id_for_year",
    "build_index_rows",
    "build_source_windows",
    "build_summary_report",
    "write_index_csv",
    "parse_args",
    "main",
]
