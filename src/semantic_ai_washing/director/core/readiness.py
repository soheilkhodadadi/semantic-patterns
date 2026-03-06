"""Task readiness and completion inference."""

from __future__ import annotations

from typing import Any

from semantic_ai_washing.director.core.sensors import evaluate_condition
from semantic_ai_washing.director.core.task_graph import TaskGraph
from semantic_ai_washing.director.schemas import (
    ConditionSpec,
    DeferredBlockerRecord,
    TaskStateSnapshot,
    TaskSpec,
)


class ReadinessEvaluator:
    def __init__(
        self,
        repo_root: str,
        graph: TaskGraph,
        deferred_records: list[DeferredBlockerRecord] | None = None,
    ):
        self.repo_root = repo_root
        self.graph = graph
        self.deferred_records = deferred_records or []
        self._deferred_phase_ids = {
            f"iteration{record.until_iteration}/{record.until_phase}".lower()
            for record in self.deferred_records
            if record.status == "active"
        }
        self._deferred_blocker_ids = {
            record.blocker_id for record in self.deferred_records if record.status == "active"
        }

    def evaluate_all(self) -> list[TaskStateSnapshot]:
        ordered = self.graph.topological_order()
        states: dict[str, TaskStateSnapshot] = {}

        for task_id in ordered:
            task = self.graph.tasks_by_id[task_id]
            states[task_id] = self._evaluate_task(task, states)

        return [states[task_id] for task_id in ordered]

    def _task_deferred(self, task: TaskSpec) -> bool:
        phase_id = task.phase_id.lower()
        return phase_id in self._deferred_phase_ids or task.task_id in self._deferred_blocker_ids

    def _task_outputs_present(self, task: TaskSpec) -> tuple[bool, list[str]]:
        missing = []
        for artifact in task.outputs:
            if not artifact.required:
                continue
            result = evaluate_condition(
                condition=ConditionSpec(
                    condition_id=f"{task.task_id}:{artifact.artifact_id}:exists",
                    kind="artifact_exists",
                    target=artifact.path,
                    operator="==",
                    expected=True,
                    on_fail="block",
                    message="",
                    reroute_to=[],
                ),
                repo_root=self.repo_root,
            )
            if not result["passed"]:
                missing.append(artifact.path)
        return len(missing) == 0, missing

    def _evaluate_task(
        self,
        task: TaskSpec,
        states: dict[str, TaskStateSnapshot],
    ) -> TaskStateSnapshot:
        missing_dependencies = [
            dep for dep in task.depends_on if states.get(dep) and states[dep].status != "satisfied"
        ]
        if self._task_deferred(task):
            return TaskStateSnapshot(
                task_id=task.task_id,
                phase_id=task.phase_id,
                iteration_id=task.iteration_id,
                status="deferred",
                dependency_ids=list(task.depends_on),
                missing_dependencies=missing_dependencies,
            )

        if missing_dependencies:
            return TaskStateSnapshot(
                task_id=task.task_id,
                phase_id=task.phase_id,
                iteration_id=task.iteration_id,
                status="waiting_on_deps",
                dependency_ids=list(task.depends_on),
                missing_dependencies=missing_dependencies,
            )

        failed_preconditions: list[str] = []
        precondition_context: dict[str, Any] = {}
        for condition in task.preconditions:
            result = evaluate_condition(condition, repo_root=self.repo_root)
            precondition_context[condition.condition_id] = result
            if not result["passed"] and condition.on_fail != "warn":
                failed_preconditions.append(condition.condition_id)
        if failed_preconditions:
            return TaskStateSnapshot(
                task_id=task.task_id,
                phase_id=task.phase_id,
                iteration_id=task.iteration_id,
                status="blocked_precondition",
                dependency_ids=list(task.depends_on),
                failed_preconditions=failed_preconditions,
                context=precondition_context,
            )

        outputs_present, missing_outputs = self._task_outputs_present(task)
        failed_quality_checks: list[str] = []
        quality_context: dict[str, Any] = {}
        for condition in task.quality_checks:
            result = evaluate_condition(condition, repo_root=self.repo_root)
            quality_context[condition.condition_id] = result
            if not result["passed"] and condition.on_fail != "warn":
                failed_quality_checks.append(condition.condition_id)

        if outputs_present and not failed_quality_checks:
            return TaskStateSnapshot(
                task_id=task.task_id,
                phase_id=task.phase_id,
                iteration_id=task.iteration_id,
                status="satisfied",
                dependency_ids=list(task.depends_on),
                context={**precondition_context, **quality_context},
            )

        if failed_quality_checks:
            return TaskStateSnapshot(
                task_id=task.task_id,
                phase_id=task.phase_id,
                iteration_id=task.iteration_id,
                status="blocked_quality",
                dependency_ids=list(task.depends_on),
                failed_quality_checks=failed_quality_checks,
                missing_outputs=missing_outputs,
                context={**precondition_context, **quality_context},
            )

        if task.manual_handoff or task.automation_level == "manual":
            return TaskStateSnapshot(
                task_id=task.task_id,
                phase_id=task.phase_id,
                iteration_id=task.iteration_id,
                status="blocked_manual",
                dependency_ids=list(task.depends_on),
                missing_outputs=missing_outputs,
                context=precondition_context,
            )

        return TaskStateSnapshot(
            task_id=task.task_id,
            phase_id=task.phase_id,
            iteration_id=task.iteration_id,
            status="ready",
            dependency_ids=list(task.depends_on),
            missing_outputs=missing_outputs,
            context=precondition_context,
        )
