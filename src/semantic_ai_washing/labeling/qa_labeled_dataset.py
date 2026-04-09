"""Compatibility shim for the member-owned Phase 1 QA helper."""

from ai_washing_member.labeling.qa_labeled_dataset import (
    OUTPUT_COLUMNS,
    REQUIRED_COLUMNS,
    main,
    parse_args,
    run_qa,
)

__all__ = ["OUTPUT_COLUMNS", "REQUIRED_COLUMNS", "run_qa", "parse_args", "main"]


if __name__ == "__main__":
    main()
