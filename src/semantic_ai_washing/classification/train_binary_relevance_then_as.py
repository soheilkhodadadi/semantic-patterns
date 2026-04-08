"""Compatibility shim for the member-owned preliminary two-stage classifier training helpers."""

import ai_washing_member.classification.train_binary_relevance_then_as as _member
from ai_washing_member.classification.train_binary_relevance_then_as import (
    main,
    parse_args,
    run_training,
)

__all__ = ["run_training", "parse_args", "main"]

member = _member


if __name__ == "__main__":
    main()
