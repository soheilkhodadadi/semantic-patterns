"""Compatibility shim for the member-owned active-window preliminary classifier."""

import ai_washing_member.classification.classify_active_window_preliminary as _member
from ai_washing_member.classification.classify_active_window_preliminary import (
    _load_metadata,
    _resolve_runtime,
    main,
    parse_args,
    run_classification,
)

__all__ = ["_load_metadata", "_resolve_runtime", "run_classification", "parse_args", "main"]

member = _member
