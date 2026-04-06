"""Compatibility shim for the member-owned IRR sentence audit."""

from ai_washing_member.labeling.audit_sentence_integrity import main, parse_args, run_audit

__all__ = ["run_audit", "parse_args", "main"]
