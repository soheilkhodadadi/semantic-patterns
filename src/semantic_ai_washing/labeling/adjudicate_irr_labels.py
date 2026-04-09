"""Compatibility shim for the member-owned IRR adjudication module."""

from ai_washing_member.labeling.adjudicate_irr_labels import (
    main,
    parse_args,
    run_adjudication,
)

__all__ = ["run_adjudication", "parse_args", "main"]


if __name__ == "__main__":
    main()
