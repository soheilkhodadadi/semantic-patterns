"""Compatibility re-exports for shared registry helpers.

The canonical implementation now lives in ``semantic_labcore.registry``.
This module remains as a transition shim so existing
``semantic_ai_washing.labcore.registry`` imports keep working while the
workspace package becomes authoritative.
"""

from semantic_ai_washing.labcore.registry.adapters import (
    ProjectAdapterContract,
    all_project_adapter_contracts,
    project_adapter_contract,
)
from semantic_ai_washing.labcore.registry.lanes import (
    PROJECT_SLUGS,
    ProjectLanes,
    SharedLanes,
    project_lanes,
    shared_lanes,
)

__all__ = [
    "PROJECT_SLUGS",
    "ProjectAdapterContract",
    "ProjectLanes",
    "SharedLanes",
    "all_project_adapter_contracts",
    "project_lanes",
    "project_adapter_contract",
    "shared_lanes",
]
