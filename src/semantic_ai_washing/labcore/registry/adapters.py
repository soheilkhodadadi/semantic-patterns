"""Compatibility re-exports for shared adapter contracts.

The canonical implementation now lives in ``semantic_labcore.registry.adapters``.
This module remains as a transition shim so existing
``semantic_ai_washing.labcore.registry.adapters`` imports keep working while the
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

from semantic_labcore.registry.adapters import (  # noqa: E402
    ProjectAdapterContract,
    all_project_adapter_contracts as _all_project_adapter_contracts,
    project_adapter_contract as _project_adapter_contract,
)


def _legacy_dependency_name(name: str) -> str:
    if name.startswith("semantic_labcore."):
        return name.replace("semantic_labcore.", "semantic_ai_washing.labcore.", 1)
    return name


def project_adapter_contract(
    repo_root: str | Path = ".",
    project: str = "ai_washing",
) -> ProjectAdapterContract:
    """Preserve legacy dependency identities for root-repo callers."""

    contract = _project_adapter_contract(repo_root, project=project)
    return ProjectAdapterContract(
        project=contract.project,
        mode=contract.mode,
        purpose=contract.purpose,
        framing_note=contract.framing_note,
        docs=contract.docs,
        reports=contract.reports,
        processed_data=contract.processed_data,
        doc_output=contract.doc_output,
        figure_output=contract.figure_output,
        local_private_root=contract.local_private_root,
        shared_dependencies=tuple(_legacy_dependency_name(item) for item in contract.shared_dependencies),
    )


def all_project_adapter_contracts(
    repo_root: str | Path = ".",
) -> dict[str, ProjectAdapterContract]:
    """Preserve legacy dependency identities for root-repo callers."""

    return {
        project: project_adapter_contract(repo_root, project=project)
        for project in _all_project_adapter_contracts(repo_root)
    }


__all__ = [
    "ProjectAdapterContract",
    "all_project_adapter_contracts",
    "project_adapter_contract",
]
