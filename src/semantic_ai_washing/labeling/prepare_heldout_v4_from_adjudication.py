"""Compatibility shim for building held_out_v4 from the adjudicated IRR source."""

import ai_washing_member.labeling.prepare_heldout_v4_from_adjudication as _member
from ai_washing_member.labeling.prepare_heldout_v4_from_adjudication import (
    build_heldout_v4,
    main,
    parse_args,
)

__all__ = ["build_heldout_v4", "parse_args", "main"]

member = _member


if __name__ == "__main__":
    main()
