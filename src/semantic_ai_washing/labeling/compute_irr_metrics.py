"""Compatibility shim for the member-owned IRR metrics module."""

from ai_washing_member.labeling.compute_irr_metrics import main, parse_args, run_metrics

__all__ = ["run_metrics", "parse_args", "main"]


if __name__ == "__main__":
    main()
