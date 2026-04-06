"""Compatibility shim for the member-owned preliminary logreg training helpers."""

import ai_washing_member.classification.train_logreg_preliminary as _member
from ai_washing_member.classification.train_logreg_preliminary import (
    main,
    parse_args,
    run_training,
)

__all__ = ["run_training", "parse_args", "main"]

member = _member
