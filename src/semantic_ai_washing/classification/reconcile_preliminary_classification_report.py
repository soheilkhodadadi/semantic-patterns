"""Compatibility shim for the member-owned preliminary classification reconciliation helpers."""

import ai_washing_member.classification.reconcile_preliminary_classification_report as _member
from ai_washing_member.classification.reconcile_preliminary_classification_report import (
    main,
    parse_args,
    reconcile_outputs,
)

__all__ = ["reconcile_outputs", "parse_args", "main"]

member = _member
