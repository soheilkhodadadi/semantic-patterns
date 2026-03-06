"""Load and query the canonical roadmap model."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from semantic_ai_washing.director.schemas import RoadmapModel, TaskSpec


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


def iter_phase_tasks(model: RoadmapModel) -> list[TaskSpec]:
    tasks: list[TaskSpec] = []
    for iteration in model.iterations:
        for phase in iteration.phases:
            tasks.extend(phase.tasks)
    return tasks


def find_iteration(model: RoadmapModel, iteration_id: str):
    for iteration in model.iterations:
        if str(iteration.iteration_id) == str(iteration_id):
            return iteration
    return None


def find_phase(model: RoadmapModel, iteration_id: str, phase_name: str):
    phase_key = f"iteration{iteration_id}/{phase_name}".strip().lower()
    iteration = find_iteration(model, iteration_id)
    if iteration is None:
        return None
    for phase in iteration.phases:
        phase_id = str(phase.phase_id).strip().lower()
        title_key = str(phase.title).strip().lower()
        if phase_id == phase_key or title_key == phase_name.strip().lower():
            return phase
    return None


def roadmap_summary_dict(
    model: RoadmapModel, source_path: str, source_sha256: str
) -> dict[str, Any]:
    tasks = iter_phase_tasks(model)
    dependency_edges = []
    manual_task_count = 0
    quality_check_count = 0
    risk_links = 0

    for task in tasks:
        if task.manual_handoff or task.automation_level == "manual":
            manual_task_count += 1
        quality_check_count += len(task.quality_checks)
        risk_links += len(task.risks)
        for dep in task.depends_on:
            dependency_edges.append({"from": dep, "to": task.task_id})

    return {
        "source_path": source_path,
        "source_sha256": source_sha256,
        "generated_from": "roadmap_model",
        "iterations": [item.model_dump(mode="json") for item in model.iterations],
        "phases": [
            {
                "iteration_id": iteration.iteration_id,
                "phase_id": phase.phase_id,
                "title": phase.title,
                "task_count": len(phase.tasks),
                "depends_on": phase.depends_on,
            }
            for iteration in model.iterations
            for phase in iteration.phases
        ],
        "tasks": [task.model_dump(mode="json") for task in tasks],
        "dependency_edges": dependency_edges,
        "manual_task_count": manual_task_count,
        "quality_check_count": quality_check_count,
        "risk_links": risk_links,
    }
