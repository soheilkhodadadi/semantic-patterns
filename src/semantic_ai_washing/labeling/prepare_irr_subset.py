"""Compatibility shim for the member-owned IRR subset preparation module."""

from ai_washing_member.labeling.prepare_irr_subset import main, parse_args, run_prepare

__all__ = ["run_prepare", "parse_args", "main"]
