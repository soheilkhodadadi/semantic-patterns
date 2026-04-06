"""Compatibility shim for the member-owned Phase 1 sample builder."""

from ai_washing_member.labeling.build_labeling_sample import (
    OUTPUT_COLUMNS,
    main,
    parse_args,
    run_build,
)

__all__ = ["OUTPUT_COLUMNS", "run_build", "parse_args", "main"]
