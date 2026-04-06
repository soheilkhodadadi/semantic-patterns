"""Compatibility shim for the member-owned IRR disagreement diagnostic module."""

from ai_washing_member.labeling.diagnose_irr_disagreements import main, parse_args, run_diagnostic

__all__ = ["run_diagnostic", "parse_args", "main"]
