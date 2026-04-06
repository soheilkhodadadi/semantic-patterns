"""Compatibility shim for the member-owned tranche merge helper."""

from ai_washing_member.labeling.merge_labeling_batches import (
    DEFAULT_HELD_OUT,
    DEFAULT_OUTPUT_PARQUET,
    DEFAULT_OUTPUT_REVIEW_CSV,
    DEFAULT_REPORT,
    REQUIRED_COLUMNS,
    main,
    merge_labeling_batches,
    parse_args,
)

__all__ = [
    "DEFAULT_OUTPUT_PARQUET",
    "DEFAULT_OUTPUT_REVIEW_CSV",
    "DEFAULT_REPORT",
    "DEFAULT_HELD_OUT",
    "REQUIRED_COLUMNS",
    "merge_labeling_batches",
    "parse_args",
    "main",
]
