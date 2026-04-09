"""Compatibility shim for the member-owned preliminary-results readiness module."""

from ai_washing_member.labeling.publish_preliminary_results_readiness import (
    main,
    parse_args,
    run_publish,
)

__all__ = ["run_publish", "parse_args", "main"]


if __name__ == "__main__":
    main()
