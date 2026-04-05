"""Compatibility re-exports for shared runtime helpers.

The canonical implementation now lives in ``semantic_labcore.runtime``.
This module remains as a transition shim so existing
``semantic_ai_washing.labcore.runtime`` imports keep working while the
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

from semantic_labcore.runtime import (  # noqa: E402
    dump_json,
    ensure_dir,
    git_info,
    load_json,
    now_utc_iso,
    repository_root,
    run_command,
    sha256_file,
    sha256_text,
)

__all__ = [
    "dump_json",
    "ensure_dir",
    "git_info",
    "load_json",
    "now_utc_iso",
    "repository_root",
    "run_command",
    "sha256_file",
    "sha256_text",
]
