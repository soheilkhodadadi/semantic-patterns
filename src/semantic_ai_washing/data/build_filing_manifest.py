"""Compatibility shim for filing-manifest helpers."""

from ai_washing_member.data.build_filing_manifest import (
    DEFAULT_CONTROLS,
    DEFAULT_CROSSWALK,
    DEFAULT_INDEX,
    DEFAULT_MANIFEST_ID,
    DEFAULT_OUTPUT,
    DEFAULT_REPORT,
    OUTPUT_COLUMNS,
    REQUIRED_QUARTERS,
    build_manifest,
    compute_manifest_row_id,
    main,
    normalize_cik,
    parse_args,
    write_manifest,
    write_report,
    _prepare_candidates,
)

__all__ = [
    "DEFAULT_CONTROLS",
    "DEFAULT_CROSSWALK",
    "DEFAULT_INDEX",
    "DEFAULT_MANIFEST_ID",
    "DEFAULT_OUTPUT",
    "DEFAULT_REPORT",
    "OUTPUT_COLUMNS",
    "REQUIRED_QUARTERS",
    "build_manifest",
    "compute_manifest_row_id",
    "main",
    "normalize_cik",
    "parse_args",
    "write_manifest",
    "write_report",
    "_prepare_candidates",
]
