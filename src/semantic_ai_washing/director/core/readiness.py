"""Task and phase readiness inference."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from semantic_ai_washing.director.core.sensors import evaluate_condition
from semantic_ai_washing.director.core.task_graph import TaskGraph
from semantic_ai_washing.director.schemas import (
    ConditionSpec,
    DeferredBlockerRecord,
    PhaseStateSnapshot,
    RoadmapModel,
    TaskStateSnapshot,
    TaskSpec,
)


class ReadinessEvaluator:
    def __init__(
        self,
        repo_root: str,
        graph: TaskGraph,
        model: RoadmapModel,
        deferred_records: list[DeferredBlockerRecord] | None = None,
    ):
        self.repo_root = repo_root
        self.graph = graph
        self.model = model
        self.deferred_records = deferred_records or []
        self._deferred_phase_ids = {
            f"iteration{record.until_iteration}/{record.until_phase}".lower()
            for record in self.deferred_records
            if record.status == "active"
        }
        self._deferred_blocker_ids = {
            record.blocker_id for record in self.deferred_records if record.status == "active"
        }
        self._policies = {policy.policy_id: policy for policy in model.policies}
        self._source_windows = {window.source_window_id: window for window in model.source_windows}

    def evaluate_all(self) -> tuple[list[TaskStateSnapshot], list[PhaseStateSnapshot]]:
        task_states = self._evaluate_task_states()
        phase_states = self._evaluate_phase_states(task_states)
        return task_states, phase_states

    def _evaluate_task_states(self) -> list[TaskStateSnapshot]:
        ordered = self.graph.topological_order()
        states: dict[str, TaskStateSnapshot] = {}

        for task_id in ordered:
            task = self.graph.tasks_by_id[task_id]
            states[task_id] = self._evaluate_task(task, states)

        return [states[task_id] for task_id in ordered]

    def _task_deferred(self, task: TaskSpec) -> bool:
        phase_id = task.phase_id.lower()
        return phase_id in self._deferred_phase_ids or task.task_id in self._deferred_blocker_ids

    def _phase_deferred(self, phase_id: str) -> bool:
        return (
            phase_id.lower() in self._deferred_phase_ids or phase_id in self._deferred_blocker_ids
        )

    def _artifact_exists(self, path: str) -> bool:
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = (Path(self.repo_root) / candidate).resolve()
        return candidate.exists()

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

    def _task_policy_blocks(self, task: TaskSpec) -> list[str]:
        blocked: list[str] = []
        input_paths = [item.path for item in task.inputs]

        heldout_policy = self._policies.get("heldout_frozen")
        if heldout_policy and any("held_out_sentences.csv" in path for path in input_paths):
            if {"training", "retraining", "centroid", "train_split"} & set(task.tags):
                blocked.append(heldout_policy.policy_id)

        irr_policy = self._policies.get("human_human_irr_only")
        if irr_policy and {"model_as_irr", "non_human_irr"} & set(task.tags):
            blocked.append(irr_policy.policy_id)

        api_policy = self._policies.get("openai_assistive_only")
        if api_policy and {"api_canonical_label", "api_promote_canonical"} & set(task.tags):
            blocked.append(api_policy.policy_id)

        sig_policy = self._policies.get("no_significance_optimization")
        if sig_policy and "significance_optimization" in task.tags:
            blocked.append(sig_policy.policy_id)

        return blocked

    def _evaluate_task(
        self,
        task: TaskSpec,
        states: dict[str, TaskStateSnapshot],
    ) -> TaskStateSnapshot:
        missing_dependencies = [
            dep for dep in task.depends_on if dep in states and states[dep].status != "satisfied"
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

        policy_blocks = self._task_policy_blocks(task)
        if policy_blocks:
            return TaskStateSnapshot(
                task_id=task.task_id,
                phase_id=task.phase_id,
                iteration_id=task.iteration_id,
                status="blocked_precondition",
                dependency_ids=list(task.depends_on),
                blocked_policy_ids=policy_blocks,
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

    def _phase_required_outputs(self, phase_id: str) -> list[str]:
        phase = self.graph.phases_by_id[phase_id]
        return [path for path in phase.required_artifacts if path]

    def _phase_missing_outputs(self, phase_id: str) -> list[str]:
        return [
            path
            for path in self._phase_required_outputs(phase_id)
            if not self._artifact_exists(path)
        ]

    def _source_window_context(self, phase_id: str) -> tuple[list[str], list[str], str | None]:
        phase = self.graph.phases_by_id[phase_id]
        if not phase.source_window_id:
            return [], [], None
        window = self._source_windows.get(phase.source_window_id)
        if window is None:
            return (
                [],
                [f"source window `{phase.source_window_id}` not defined"],
                "blocked_precondition",
            )
        notes = [f"source window `{window.source_window_id}` status=`{window.status}`"]
        if window.status == "deferred":
            return [], notes, "deferred"
        if window.availability_condition:
            result = evaluate_condition(window.availability_condition, repo_root=self.repo_root)
            notes.append(
                f"availability check `{window.availability_condition.condition_id}` passed={result['passed']}"
            )
            if not result["passed"]:
                return [], notes, "deferred"
        return [], notes, None

    def _evaluate_phase_states(
        self, task_states: list[TaskStateSnapshot]
    ) -> list[PhaseStateSnapshot]:
        task_state_map = {state.task_id: state for state in task_states}
        ordered = self.graph.phase_topological_order()
        states: dict[str, PhaseStateSnapshot] = {}

        for phase_id in ordered:
            phase = self.graph.phases_by_id[phase_id]
            lifecycle = phase.lifecycle_state
            if lifecycle in {"historical", "superseded", "completed"}:
                states[phase_id] = PhaseStateSnapshot(
                    phase_id=phase_id,
                    iteration_id=phase_id.split("/", 1)[0].replace("iteration", ""),
                    status=lifecycle,
                    lifecycle_state=lifecycle,
                    dependency_ids=list(phase.depends_on),
                    required_artifacts=self._phase_required_outputs(phase_id),
                )
                continue

            missing_dependencies = [
                dep
                for dep in phase.depends_on
                if dep in states and states[dep].status not in {"satisfied", "completed"}
            ]
            if self._phase_deferred(phase_id):
                states[phase_id] = PhaseStateSnapshot(
                    phase_id=phase_id,
                    iteration_id=phase_id.split("/", 1)[0].replace("iteration", ""),
                    status="deferred",
                    lifecycle_state=lifecycle,
                    dependency_ids=list(phase.depends_on),
                    missing_dependencies=missing_dependencies,
                    required_artifacts=self._phase_required_outputs(phase_id),
                )
                continue
            if missing_dependencies:
                states[phase_id] = PhaseStateSnapshot(
                    phase_id=phase_id,
                    iteration_id=phase_id.split("/", 1)[0].replace("iteration", ""),
                    status="waiting_on_deps",
                    lifecycle_state=lifecycle,
                    dependency_ids=list(phase.depends_on),
                    missing_dependencies=missing_dependencies,
                    required_artifacts=self._phase_required_outputs(phase_id),
                )
                continue

            blocked_policy_ids: list[str] = []
            source_window_notes, source_window_extra, source_status = self._source_window_context(
                phase_id
            )
            notes = source_window_notes + source_window_extra
            if source_status == "deferred":
                states[phase_id] = PhaseStateSnapshot(
                    phase_id=phase_id,
                    iteration_id=phase_id.split("/", 1)[0].replace("iteration", ""),
                    status="deferred",
                    lifecycle_state=lifecycle,
                    dependency_ids=list(phase.depends_on),
                    required_artifacts=self._phase_required_outputs(phase_id),
                    source_window_notes=notes,
                )
                continue
            if source_status == "blocked_precondition":
                states[phase_id] = PhaseStateSnapshot(
                    phase_id=phase_id,
                    iteration_id=phase_id.split("/", 1)[0].replace("iteration", ""),
                    status="blocked_precondition",
                    lifecycle_state=lifecycle,
                    dependency_ids=list(phase.depends_on),
                    required_artifacts=self._phase_required_outputs(phase_id),
                    source_window_notes=notes,
                )
                continue

            phase_task_ids = self.graph.phase_task_ids.get(phase_id, [])
            phase_task_states = [
                task_state_map[task_id] for task_id in phase_task_ids if task_id in task_state_map
            ]
            missing_outputs = self._phase_missing_outputs(phase_id)

            if phase_task_states:
                if any(state.status == "blocked_manual" for state in phase_task_states):
                    status = "blocked_manual"
                elif any(state.status == "blocked_quality" for state in phase_task_states):
                    status = "blocked_quality"
                elif any(state.status == "blocked_precondition" for state in phase_task_states):
                    status = "blocked_precondition"
                elif any(state.status == "waiting_on_deps" for state in phase_task_states):
                    status = "waiting_on_deps"
                elif (
                    all(state.status == "satisfied" for state in phase_task_states)
                    and not missing_outputs
                ):
                    status = "satisfied"
                else:
                    status = "ready"
                blocked_policy_ids = sorted(
                    {
                        policy_id
                        for state in phase_task_states
                        for policy_id in state.blocked_policy_ids
                    }
                )
            else:
                status = "satisfied" if not missing_outputs else "ready"

            states[phase_id] = PhaseStateSnapshot(
                phase_id=phase_id,
                iteration_id=phase_id.split("/", 1)[0].replace("iteration", ""),
                status=status,
                lifecycle_state=lifecycle,
                dependency_ids=list(phase.depends_on),
                required_artifacts=self._phase_required_outputs(phase_id),
                missing_outputs=missing_outputs,
                blocked_policy_ids=blocked_policy_ids,
                source_window_notes=notes,
                context={"task_ids": phase_task_ids},
            )

        return [states[phase_id] for phase_id in ordered]
