"""Compatibility shim for publishing selected selective-defer runtime manifests."""

import ai_washing_member.classification.publish_selective_defer_runtime as _member
from ai_washing_member.classification.publish_selective_defer_runtime import (
    main,
    parse_args,
    run_publish,
)

__all__ = ["run_publish", "parse_args", "main"]

member = _member


if __name__ == "__main__":
    main()
