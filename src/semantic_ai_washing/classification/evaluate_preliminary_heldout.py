"""Compatibility shim for the member-owned preliminary held-out evaluation helpers."""

import ai_washing_member.classification.evaluate_preliminary_heldout as _member
from ai_washing_member.classification.evaluate_preliminary_heldout import (
    _load_metadata,
    _pending_selected_payload,
    main,
    parse_args,
    run_evaluation,
)

__all__ = ["_load_metadata", "_pending_selected_payload", "run_evaluation", "parse_args", "main"]

member = _member
