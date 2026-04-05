"""Compatibility re-exports for director audit helpers.

The shared implementations now live in ``semantic_ai_washing.labcore.audit``.
This module remains as a compatibility shim so existing director imports do not
break during the staged migration.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from semantic_ai_washing.labcore.audit import (
    append_jsonl,
    payload_hash,
    write_audit_record,
)
from semantic_ai_washing.labcore.audit import default_provenance as _default_provenance


def default_provenance(repo_root: str | Path = ".") -> dict[str, Any]:
    """Preserve the director provenance identity during migration."""

    return _default_provenance(
        repo_root,
        tool="semantic_ai_washing.director",
        schema_version="1.0.0",
    )


__all__ = [
    "append_jsonl",
    "default_provenance",
    "payload_hash",
    "write_audit_record",
]
