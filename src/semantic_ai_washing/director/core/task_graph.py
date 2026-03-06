"""Task and phase graph compilation helpers."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

from semantic_ai_washing.director.core.roadmap_model import (
    iteration_phase_map,
    iter_phase_tasks,
)
from semantic_ai_washing.director.schemas import PhaseSpec, RoadmapModel, TaskSpec


def _topological_order(
    nodes: set[str], upstream: dict[str, list[str]], downstream: dict[str, list[str]]
) -> list[str]:
    indegree = {
        node_id: len([dep for dep in upstream.get(node_id, []) if dep in nodes])
        for node_id in nodes
    }
    queue = deque(sorted(node_id for node_id, degree in indegree.items() if degree == 0))
    ordered: list[str] = []

    while queue:
        node_id = queue.popleft()
        ordered.append(node_id)
        for child in sorted(dep for dep in downstream.get(node_id, []) if dep in nodes):
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)

    if len(ordered) != len(nodes):
        remaining = sorted(nodes - set(ordered))
        raise ValueError(f"Dependency cycle detected: {remaining}")
    return ordered


class TaskGraph:
    def __init__(
        self,
        tasks_by_id: dict[str, TaskSpec],
        downstream: dict[str, list[str]],
        upstream: dict[str, list[str]],
        phases_by_id: dict[str, PhaseSpec],
        phase_downstream: dict[str, list[str]],
        phase_upstream: dict[str, list[str]],
        phase_task_ids: dict[str, list[str]],
    ):
        self.tasks_by_id = tasks_by_id
        self.downstream = downstream
        self.upstream = upstream
        self.phases_by_id = phases_by_id
        self.phase_downstream = phase_downstream
        self.phase_upstream = phase_upstream
        self.phase_task_ids = phase_task_ids

    def topological_order(self, task_ids: list[str] | None = None) -> list[str]:
        scoped_ids = set(task_ids or self.tasks_by_id.keys())
        return _topological_order(scoped_ids, self.upstream, self.downstream)

    def phase_topological_order(self, phase_ids: list[str] | None = None) -> list[str]:
        scoped_ids = set(phase_ids or self.phases_by_id.keys())
        return _topological_order(scoped_ids, self.phase_upstream, self.phase_downstream)

    def downstream_count(self, task_id: str) -> int:
        seen: set[str] = set()
        stack = list(self.downstream.get(task_id, []))
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            stack.extend(self.downstream.get(current, []))
        return len(seen)

    def phase_downstream_count(self, phase_id: str) -> int:
        seen: set[str] = set()
        stack = list(self.phase_downstream.get(phase_id, []))
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            stack.extend(self.phase_downstream.get(current, []))
        return len(seen)

    def critical_path_depth(self, task_id: str) -> int:
        children = self.downstream.get(task_id, [])
        if not children:
            return 1
        return 1 + max(self.critical_path_depth(child) for child in children)

    def phase_critical_path_depth(self, phase_id: str) -> int:
        children = self.phase_downstream.get(phase_id, [])
        if not children:
            return 1
        return 1 + max(self.phase_critical_path_depth(child) for child in children)

    def as_dict(self) -> dict[str, Any]:
        return {
            "tasks": {
                task_id: task.model_dump(mode="json") for task_id, task in self.tasks_by_id.items()
            },
            "downstream": self.downstream,
            "upstream": self.upstream,
            "phases": {
                phase_id: phase.model_dump(mode="json")
                for phase_id, phase in self.phases_by_id.items()
            },
            "phase_downstream": self.phase_downstream,
            "phase_upstream": self.phase_upstream,
            "phase_task_ids": self.phase_task_ids,
        }


def build_task_graph(model: RoadmapModel) -> TaskGraph:
    tasks = iter_phase_tasks(model)
    tasks_by_id = {task.task_id: task for task in tasks}
    phases_by_id = iteration_phase_map(model)
    phase_task_ids = {
        phase.phase_id: [task.task_id for task in phase.tasks] for phase in phases_by_id.values()
    }

    downstream: dict[str, list[str]] = defaultdict(list)
    upstream: dict[str, list[str]] = defaultdict(list)
    phase_downstream: dict[str, list[str]] = defaultdict(list)
    phase_upstream: dict[str, list[str]] = defaultdict(list)

    for phase in phases_by_id.values():
        phase_upstream[phase.phase_id] = list(phase.depends_on)
        for dep in phase.depends_on:
            phase_downstream[dep].append(phase.phase_id)

    for phase in phases_by_id.values():
        task_ids = [task.task_id for task in phase.tasks]
        for task in phase.tasks:
            deps = list(task.depends_on)
            if phase.depends_on and not deps:
                for dep_phase in phase.depends_on:
                    dep_task_ids = phase_task_ids.get(dep_phase, [])
                    deps.extend(dep_task_ids)
            upstream[task.task_id] = sorted(set(deps))
            for dep in upstream[task.task_id]:
                downstream[dep].append(task.task_id)
        for task_id in task_ids:
            downstream.setdefault(task_id, [])
            upstream.setdefault(task_id, [])

    for phase_id in phases_by_id:
        phase_downstream.setdefault(phase_id, [])
        phase_upstream.setdefault(phase_id, [])

    return TaskGraph(
        tasks_by_id=tasks_by_id,
        downstream={k: sorted(set(v)) for k, v in downstream.items()},
        upstream={k: sorted(set(v)) for k, v in upstream.items()},
        phases_by_id=phases_by_id,
        phase_downstream={k: sorted(set(v)) for k, v in phase_downstream.items()},
        phase_upstream={k: sorted(set(v)) for k, v in phase_upstream.items()},
        phase_task_ids=phase_task_ids,
    )
