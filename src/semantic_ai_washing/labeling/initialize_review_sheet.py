"""Compatibility shim for the member-owned review-sheet initializer."""

from ai_washing_member.labeling.initialize_review_sheet import (
    DEFAULT_SLICE_SIZE,
    initialize_review_sheet,
    main,
    parse_args,
)

__all__ = ["DEFAULT_SLICE_SIZE", "initialize_review_sheet", "parse_args", "main"]


if __name__ == "__main__":
    main()
