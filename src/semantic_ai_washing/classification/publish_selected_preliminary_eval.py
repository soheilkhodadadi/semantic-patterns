"""Compatibility shim for the member-owned selected preliminary evaluation publisher."""

import ai_washing_member.classification.publish_selected_preliminary_eval as _member
from ai_washing_member.classification.publish_selected_preliminary_eval import (
    main,
    parse_args,
    run_publish,
)

__all__ = ["run_publish", "parse_args", "main"]

member = _member
