"""Shared lab core primitives with intentionally narrow scope."""

from semantic_ai_washing.labcore.registry import (
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
