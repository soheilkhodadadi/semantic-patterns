"""Compatibility re-exports for shared audit helpers.

The canonical implementation now lives in ``semantic_labcore.audit``.
This module remains as a transition shim so existing
``semantic_ai_washing.labcore.audit`` imports keep working while the
workspace package becomes authoritative.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PACKAGE_SRC = Path(__file__).resolve().parents[3] / "packages" / "labcore" / "src"
if _PACKAGE_SRC.exists():
    package_src = str(_PACKAGE_SRC)
    if package_src not in sys.path:
        sys.path.insert(0, package_src)

from semantic_labcore.audit import (  # noqa: E402
    append_jsonl,
    default_provenance,
    payload_hash,
    write_audit_record,
)

__all__ = [
    "append_jsonl",
    "default_provenance",
    "payload_hash",
    "write_audit_record",
]
