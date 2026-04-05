"""Compatibility shim for AI-washing benchmark utility helpers."""

import ai_washing_member.classification.benchmark_utils as _member
from ai_washing_member.classification.benchmark_utils import (
    BINARY_LABELS,
    build_validation_benchmark,
    compute_metrics,
    heldout_overlap_count,
    load_benchmark_frame,
)

__all__ = [
    "BINARY_LABELS",
    "load_benchmark_frame",
    "build_validation_benchmark",
    "heldout_overlap_count",
    "compute_metrics",
]

member = _member
