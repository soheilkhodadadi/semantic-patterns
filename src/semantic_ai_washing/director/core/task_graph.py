"""Task graph compilation and traversal helpers."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

from semantic_ai_washing.director.core.roadmap_model import iter_phase_tasks
from semantic_ai_washing.director.schemas import RoadmapModel, TaskSpec


class TaskGraph:
    def __init__(
        self,
        tasks_by_id: dict[str, TaskSpec],
        downstream: dict[str, list[str]],
        upstream: dict[str, list[str]],
    ):
        self.tasks_by_id = tasks_by_id
        self.downstream = downstream
        self.upstream = upstream

    def topological_order(self, task_ids: list[str] | None = None) -> list[str]:
        scoped_ids = set(task_ids or self.tasks_by_id.keys())
        indegree = {
            task_id: len([dep for dep in self.upstream.get(task_id, []) if dep in scoped_ids])
            for task_id in scoped_ids
        }
        queue = deque(sorted(task_id for task_id, degree in indegree.items() if degree == 0))
        ordered: list[str] = []

        while queue:
            task_id = queue.popleft()
            ordered.append(task_id)
            for child in sorted(
                dep for dep in self.downstream.get(task_id, []) if dep in scoped_ids
            ):
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)

        if len(ordered) != len(scoped_ids):
            remaining = sorted(scoped_ids - set(ordered))
            raise ValueError(f"Task dependency cycle detected: {remaining}")
        return ordered

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

    def critical_path_depth(self, task_id: str) -> int:
        children = self.downstream.get(task_id, [])
        if not children:
            return 1
        return 1 + max(self.critical_path_depth(child) for child in children)

    def as_dict(self) -> dict[str, Any]:
        return {
            "tasks": {
                task_id: task.model_dump(mode="json") for task_id, task in self.tasks_by_id.items()
            },
            "downstream": self.downstream,
            "upstream": self.upstream,
        }


def build_task_graph(model: RoadmapModel) -> TaskGraph:
    tasks = iter_phase_tasks(model)
    tasks_by_id = {task.task_id: task for task in tasks}
    downstream: dict[str, list[str]] = defaultdict(list)
    upstream: dict[str, list[str]] = defaultdict(list)

    for task in tasks:
        upstream[task.task_id] = list(task.depends_on)
        for dep in task.depends_on:
            downstream[dep].append(task.task_id)

    for task_id in tasks_by_id:
        downstream.setdefault(task_id, [])
        upstream.setdefault(task_id, [])

    return TaskGraph(tasks_by_id=tasks_by_id, downstream=dict(downstream), upstream=dict(upstream))
