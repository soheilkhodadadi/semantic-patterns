"""Resolve shared and project-scoped lab lanes from a repository root."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

PROJECT_SLUGS: Final[tuple[str, ...]] = ("ai_washing", "eri", "allocationlab")


@dataclass(frozen=True)
class SharedLanes:
    """Shared tracked lanes introduced by the lab restructure."""

    lab_docs: Path
    control_plane_docs: Path
    schema_docs: Path
    migration_docs: Path
    onboarding_docs: Path
    registry_reports: Path
    manifests: Path
    processed_data: Path
    doc_output: Path
    figure_output: Path


@dataclass(frozen=True)
class ProjectLanes:
    """Project-scoped tracked lanes introduced by the lab restructure."""

    project: str
    docs: Path
    reports: Path
    processed_data: Path
    doc_output: Path
    figure_output: Path


def _normalize_repo_root(repo_root: str | Path = ".") -> Path:
    return Path(repo_root).expanduser().resolve()


def shared_lanes(repo_root: str | Path = ".") -> SharedLanes:
    """Return the canonical shared tracked lanes for the current lab structure."""

    root = _normalize_repo_root(repo_root)
    return SharedLanes(
        lab_docs=root / "docs" / "lab",
        control_plane_docs=root / "docs" / "lab" / "control_plane",
        schema_docs=root / "docs" / "lab" / "schemas",
        migration_docs=root / "docs" / "lab" / "migration",
        onboarding_docs=root / "docs" / "lab" / "onboarding",
        registry_reports=root / "reports" / "registry",
        manifests=root / "data" / "manifests",
        processed_data=root / "data" / "processed" / "shared",
        doc_output=root / "output" / "doc" / "shared",
        figure_output=root / "output" / "figures" / "shared",
    )


def project_lanes(repo_root: str | Path = ".", project: str = "ai_washing") -> ProjectLanes:
    """Return canonical project-scoped tracked lanes for a supported project slug."""

    if project not in PROJECT_SLUGS:
        supported = ", ".join(PROJECT_SLUGS)
        raise ValueError(f"Unsupported project '{project}'. Expected one of: {supported}")

    root = _normalize_repo_root(repo_root)
    return ProjectLanes(
        project=project,
        docs=root / "docs" / "projects" / project,
        reports=root / "reports" / "projects" / project,
        processed_data=root / "data" / "processed" / "projects" / project,
        doc_output=root / "output" / "doc" / "projects" / project,
        figure_output=root / "output" / "figures" / "projects" / project,
    )
