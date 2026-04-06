"""Compatibility shim for the member-owned historical backfill helpers."""

from ai_washing_member.data.run_historical_backfill import (
    DEFAULT_FORMS,
    DEFAULT_YEARS,
    _load_json,
    _materialize_years,
    _now_utc,
    _scan_year,
    _write_progress,
    _write_year_cache,
    _year_cache_metadata,
    main,
    parse_args,
    run_backfill,
)

__all__ = [
    "DEFAULT_YEARS",
    "DEFAULT_FORMS",
    "_now_utc",
    "_write_progress",
    "_load_json",
    "_year_cache_metadata",
    "_scan_year",
    "_write_year_cache",
    "_materialize_years",
    "run_backfill",
    "parse_args",
    "main",
]
