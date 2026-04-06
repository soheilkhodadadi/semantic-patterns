"""Compatibility re-exports for director security helpers.

The canonical director-facing implementations now live in
``semantic_director.security``. This module remains as a compatibility shim so
existing imports do not break during the staged migration.
"""

from semantic_director.security import (
    KEY_PATTERNS,
    ensure_openai_key_if_enabled,
    redact_secrets,
    scan_repo_for_secrets,
    scan_text_for_secrets,
)


__all__ = [
    "KEY_PATTERNS",
    "ensure_openai_key_if_enabled",
    "redact_secrets",
    "scan_repo_for_secrets",
    "scan_text_for_secrets",
]
