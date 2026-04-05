"""Compatibility re-exports for shared security helpers.

The canonical implementation now lives in ``semantic_labcore.security``.
This module remains as a transition shim so existing
``semantic_ai_washing.labcore.security`` imports keep working while the
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

from semantic_labcore.security import (  # noqa: E402
    KEY_PATTERNS,
    ensure_api_key_if_enabled,
    redact_secrets,
    scan_repo_for_secrets,
    scan_text_for_secrets,
    tracked_files,
)

__all__ = [
    "KEY_PATTERNS",
    "ensure_api_key_if_enabled",
    "redact_secrets",
    "scan_repo_for_secrets",
    "scan_text_for_secrets",
    "tracked_files",
]
