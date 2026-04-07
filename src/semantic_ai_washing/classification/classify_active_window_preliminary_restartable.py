"""Compatibility shim for the member-owned restartable preliminary classifier."""

import ai_washing_member.classification.classify_active_window_preliminary_restartable as _member
from ai_washing_member.classification.classify_active_window_preliminary_restartable import (
    main,
    parse_args,
    run_classification_restartable,
)

__all__ = ["run_classification_restartable", "parse_args", "main"]

member = _member


if __name__ == "__main__":
    main()
