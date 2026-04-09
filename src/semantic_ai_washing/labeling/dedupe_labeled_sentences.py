"""Compatibility shim for the member-owned Phase 1 dedupe helper."""

from ai_washing_member.labeling.dedupe_labeled_sentences import (
    OUTPUT_COLUMNS,
    main,
    parse_args,
    run_dedupe,
)

__all__ = ["OUTPUT_COLUMNS", "run_dedupe", "parse_args", "main"]


if __name__ == "__main__":
    main()
