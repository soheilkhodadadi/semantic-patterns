"""Compatibility shim for AI-washing sentence-table extraction helpers."""

import ai_washing_member.data.extract_sentence_table as _member
from ai_washing_member.data.extract_sentence_table import (
    DEFAULT_KEYWORDS,
    DEFAULT_MANIFEST,
    DEFAULT_MAX_FRAGMENT_SCORE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_OUTPUT,
    DEFAULT_REPORT,
    DEFAULT_SAMPLE_OUTPUT,
    DEFAULT_SAMPLE_OUTPUT as DEFAULT_SAMPLE_CSV_OUTPUT,
    DEFAULT_SEGMENTATION_MODE,
    EXTRACTOR_VERSION,
    INTEGRITY_FLAG_COUNT,
    OUTPUT_COLUMNS,
    _build_row,
    _resolve_source_root,
    _segment_text,
    _serialize_flags,
    _sha1_short,
    _sha256_bytes,
    _sha256_file,
    _token_count,
    _token_count_summary,
    extract_sentence_table,
    main,
    parse_args,
)

__all__ = [
    "DEFAULT_MANIFEST",
    "DEFAULT_OUTPUT",
    "DEFAULT_SAMPLE_OUTPUT",
    "DEFAULT_SAMPLE_CSV_OUTPUT",
    "DEFAULT_REPORT",
    "DEFAULT_KEYWORDS",
    "DEFAULT_MAX_TOKENS",
    "DEFAULT_MAX_FRAGMENT_SCORE",
    "DEFAULT_SEGMENTATION_MODE",
    "EXTRACTOR_VERSION",
    "INTEGRITY_FLAG_COUNT",
    "OUTPUT_COLUMNS",
    "_sha256_bytes",
    "_sha256_file",
    "_sha1_short",
    "_resolve_source_root",
    "_token_count",
    "_serialize_flags",
    "_token_count_summary",
    "_build_row",
    "_segment_text",
    "extract_sentence_table",
    "parse_args",
    "main",
]

# Preserve a direct module handle for lightweight compatibility checks and monkeypatches.
member = _member
