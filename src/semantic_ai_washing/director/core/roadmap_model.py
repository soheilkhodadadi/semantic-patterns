"""Load and query the canonical roadmap model."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from semantic_ai_washing.director.schemas import PhaseSpec, RoadmapModel, TaskSpec


def resolve_model_path(repo_root: str, configured_path: str) -> Path:
    candidate = Path(configured_path)
    if candidate.is_absolute():
        return candidate
    return (Path(repo_root) / candidate).resolve()


def load_roadmap_model(path: str | Path) -> RoadmapModel:
    source = Path(path)
    payload = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
    return RoadmapModel.model_validate(payload)


def load_remediation_library(path: str | Path) -> dict[str, TaskSpec]:
    source = Path(path)
    payload = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
    tasks = payload.get("tasks", [])
    library: dict[str, TaskSpec] = {}
    for item in tasks:
        task = TaskSpec.model_validate(item)
        library[task.task_id] = task
    return library


def iter_phases(model: RoadmapModel) -> list[PhaseSpec]:
    phases: list[PhaseSpec] = []
    for iteration in model.iterations:
        phases.extend(iteration.phases)
    return phases


def iter_phase_tasks(model: RoadmapModel) -> list[TaskSpec]:
    tasks: list[TaskSpec] = []
    for phase in iter_phases(model):
        tasks.extend(phase.tasks)
    return tasks


def iteration_phase_map(model: RoadmapModel) -> dict[str, PhaseSpec]:
    return {phase.phase_id: phase for phase in iter_phases(model)}


def find_iteration(model: RoadmapModel, iteration_id: str):
    for iteration in model.iterations:
        if str(iteration.iteration_id) == str(iteration_id):
            return iteration
    return None


def find_phase(model: RoadmapModel, iteration_id: str, phase_name: str):
    normalized_phase = phase_name.strip().lower()
    phase_key = f"iteration{iteration_id}/{normalized_phase}"
    iteration = find_iteration(model, iteration_id)
    if iteration is None:
        return None
    for phase in iteration.phases:
        phase_id = str(phase.phase_id).strip().lower()
        title_key = str(phase.title).strip().lower()
        short_phase_id = phase_id.split("/", 1)[-1]
        if phase_id in {phase_key, normalized_phase}:
            return phase
        if short_phase_id == normalized_phase or title_key == normalized_phase:
            return phase
    return None


def phase_iteration_id(phase: PhaseSpec) -> str:
    if phase.phase_id.startswith("iteration"):
        head = phase.phase_id.split("/", 1)[0]
        return head.replace("iteration", "")
    return ""


def roadmap_summary_dict(
    model: RoadmapModel, source_path: str, source_sha256: str
) -> dict[str, Any]:
    tasks = iter_phase_tasks(model)
    phases = iter_phases(model)
    dependency_edges = []
    manual_task_count = 0
    quality_check_count = 0
    risk_links = 0

    for phase in phases:
        for dep in phase.depends_on:
            dependency_edges.append({"from": dep, "to": phase.phase_id, "type": "phase"})
        for task in phase.tasks:
            if task.manual_handoff or task.automation_level == "manual":
                manual_task_count += 1
            quality_check_count += len(task.quality_checks)
            risk_links += len(task.risks)
            for dep in task.depends_on:
                dependency_edges.append({"from": dep, "to": task.task_id, "type": "task"})

    return {
        "source_path": source_path,
        "source_sha256": source_sha256,
        "generated_from": "roadmap_model",
        "schema_version": model.schema_version,
        "project": model.project,
        "settings": model.settings,
        "policies": [item.model_dump(mode="json") for item in model.policies],
        "data_layers": [item.model_dump(mode="json") for item in model.data_layers],
        "source_windows": [item.model_dump(mode="json") for item in model.source_windows],
        "tooling_policies": [item.model_dump(mode="json") for item in model.tooling_policies],
        "iterations": [item.model_dump(mode="json") for item in model.iterations],
        "phases": [
            {
                "iteration_id": phase_iteration_id(phase),
                "phase_id": phase.phase_id,
                "title": phase.title,
                "goal": phase.goal,
                "task_count": len(phase.tasks),
                "depends_on": phase.depends_on,
                "lifecycle_state": phase.lifecycle_state,
                "source_window_id": phase.source_window_id,
                "required_artifacts": phase.required_artifacts,
            }
            for phase in phases
        ],
        "tasks": [task.model_dump(mode="json") for task in tasks],
        "dependency_edges": dependency_edges,
        "manual_task_count": manual_task_count,
        "quality_check_count": quality_check_count,
        "risk_links": risk_links,
    }
