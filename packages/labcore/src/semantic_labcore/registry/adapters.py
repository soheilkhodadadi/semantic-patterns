"""Canonical project-adapter contracts for the lab's active program lanes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

from semantic_labcore.registry.lanes import PROJECT_SLUGS, project_lanes


@dataclass(frozen=True)
class ProjectAdapterContract:
    """Small control-plane contract for a tracked project adapter."""

    project: str
    mode: str
    purpose: str
    framing_note: Path
    docs: Path
    reports: Path
    processed_data: Path
    doc_output: Path
    figure_output: Path
    local_private_root: Path
    shared_dependencies: tuple[str, ...]


_ADAPTER_METADATA: Final[dict[str, dict[str, object]]] = {
    "ai_washing": {
        "mode": "flagship_publication",
        "purpose": (
            "Reference research adapter for AI-disclosure credibility, patent mismatch, "
            "and manuscript-facing empirical outputs."
        ),
        "shared_dependencies": (
            "semantic_labcore.registry.lanes",
            "semantic_labcore.runtime",
            "semantic_labcore.audit",
        ),
    },
    "eri": {
        "mode": "incubation_reuse_test",
        "purpose": (
            "First serious reuse adapter for disclosure-reliability work outside the AI "
            "domain, with lighter tracked outputs and local-private partner materials."
        ),
        "shared_dependencies": (
            "semantic_labcore.registry.lanes",
            "semantic_labcore.runtime",
            "semantic_labcore.audit",
        ),
    },
    "allocationlab": {
        "mode": "architecture_first",
        "purpose": (
            "Architecture and synthetic-case adapter for a future decision-system program, "
            "kept active without forcing early implementation."
        ),
        "shared_dependencies": (
            "semantic_labcore.registry.lanes",
            "semantic_labcore.runtime",
            "semantic_labcore.audit",
        ),
    },
}


def project_adapter_contract(
    repo_root: str | Path = ".",
    project: str = "ai_washing",
) -> ProjectAdapterContract:
    """Return the canonical adapter contract for a supported project slug."""

    if project not in PROJECT_SLUGS:
        supported = ", ".join(PROJECT_SLUGS)
        raise ValueError(f"Unsupported project '{project}'. Expected one of: {supported}")

    root = Path(repo_root).expanduser().resolve()
    lanes = project_lanes(root, project=project)
    meta = _ADAPTER_METADATA[project]
    return ProjectAdapterContract(
        project=project,
        mode=str(meta["mode"]),
        purpose=str(meta["purpose"]),
        framing_note=lanes.docs / "adapter_framing_v1.md",
        docs=lanes.docs,
        reports=lanes.reports,
        processed_data=lanes.processed_data,
        doc_output=lanes.doc_output,
        figure_output=lanes.figure_output,
        local_private_root=root / "local_private" / "projects" / project,
        shared_dependencies=tuple(str(item) for item in meta["shared_dependencies"]),
    )


def all_project_adapter_contracts(
    repo_root: str | Path = ".",
) -> dict[str, ProjectAdapterContract]:
    """Return the canonical adapter contracts for all tracked project slugs."""

    return {
        project: project_adapter_contract(repo_root, project=project) for project in PROJECT_SLUGS
    }
