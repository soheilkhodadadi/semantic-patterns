"""Compatibility shim for the member-owned IRR boundary benchmark module."""

from ai_washing_member.labeling.build_irr_boundary_benchmark import (
    OUTPUT_COLUMNS,
    main,
    parse_args,
    run_build,
)

__all__ = ["OUTPUT_COLUMNS", "run_build", "parse_args", "main"]


if __name__ == "__main__":
    main()
