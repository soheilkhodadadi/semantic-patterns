"""Compatibility re-exports for shared registry lane helpers.

The canonical implementation now lives in ``semantic_labcore.registry.lanes``.
This module remains as a transition shim so existing
``semantic_ai_washing.labcore.registry.lanes`` imports keep working while the
workspace package becomes authoritative.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PACKAGE_SRC = Path(__file__).resolve().parents[4] / "packages" / "labcore" / "src"
if _PACKAGE_SRC.exists():
    package_src = str(_PACKAGE_SRC)
    if package_src not in sys.path:
        sys.path.insert(0, package_src)

from semantic_labcore.registry.lanes import (  # noqa: E402
    PROJECT_SLUGS,
    ProjectLanes,
    SharedLanes,
    project_lanes,
    shared_lanes,
)

__all__ = [
    "PROJECT_SLUGS",
    "ProjectLanes",
    "SharedLanes",
    "project_lanes",
    "shared_lanes",
]
