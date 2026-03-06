"""Deterministic optimization and next-work recommendation engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from semantic_ai_washing.director.core.readiness import ReadinessEvaluator
from semantic_ai_washing.director.core.render import render_optimization_markdown
from semantic_ai_washing.director.core.roadmap_model import (
    load_remediation_library,
    load_roadmap_model,
)
from semantic_ai_washing.director.core.task_graph import build_task_graph
from semantic_ai_washing.director.core.utils import dump_json, now_utc_iso, sha256_file
from semantic_ai_washing.director.schemas import (
    DeferredBlockerRecord,
    OptimizationRecommendation,
    OptimizationReport,
    PhaseStateSnapshot,
    RoadmapPatchProposal,
    TaskStateSnapshot,
)


class DirectorOptimizer:
    def __init__(
        self,
        repo_root: str,
        roadmap_model_path: str,
        remediation_library_path: str,
        optimization_dir: str,
        decisions_dir: str,
        weights: dict[str, int],
        emit_patch: bool = True,
    ):
        self.repo_root = repo_root
        self.roadmap_model_path = Path(roadmap_model_path)
        self.remediation_library_path = Path(remediation_library_path)
        self.optimization_dir = Path(optimization_dir)
        self.optimization_dir.mkdir(parents=True, exist_ok=True)
        self.decisions_dir = Path(decisions_dir)
        self.weights = weights
        self.emit_patch = emit_patch

    def _optimization_id(self, focus_iteration: str = "", focus_phase: str = "") -> str:
        stem = f"{focus_iteration}:{focus_phase}:{now_utc_iso()}"
        return sha256_file(self.roadmap_model_path)[:8] + "-" + stem.encode("utf-8").hex()[:8]

    def _load_deferred(self) -> list[DeferredBlockerRecord]:
        records: list[DeferredBlockerRecord] = []
        for path in sorted(self.decisions_dir.glob("deferred_*.json")):
            records.append(
                DeferredBlockerRecord.model_validate_json(path.read_text(encoding="utf-8"))
            )
        return records

    def _score_task(self, graph, state: TaskStateSnapshot, task) -> float:
        automation_bonus = {"full": 2, "partial": 1, "manual": 0}[task.automation_level]
        manual_effort = task.estimated_effort if task.automation_level == "manual" else 0
        precondition_gap = len(state.failed_preconditions) + len(state.missing_dependencies)
        quality_penalty = 1 if state.failed_quality_checks else 0
        return float(
            self.weights.get("unblock_value", 5) * min(10, graph.downstream_count(task.task_id))
            + self.weights.get("critical_path_depth", 4) * graph.critical_path_depth(task.task_id)
            + self.weights.get("risk_reduction", 3) * int(task.risk_reduction)
            + self.weights.get("automation_bonus", 2) * automation_bonus
            - self.weights.get("manual_effort_penalty", 2) * manual_effort
            - self.weights.get("precondition_gap_penalty", 4) * precondition_gap
            - self.weights.get("quality_failure_penalty", 5) * quality_penalty
        )

    def _score_phase(self, graph, state: PhaseStateSnapshot) -> float:
        precondition_gap = len(state.missing_dependencies) + len(state.missing_outputs)
        quality_penalty = 1 if state.status == "blocked_quality" else 0
        manual_penalty = 1 if state.status == "blocked_manual" else 0
        return float(
            self.weights.get("unblock_value", 5)
            * min(10, graph.phase_downstream_count(state.phase_id))
            + self.weights.get("critical_path_depth", 4)
            * graph.phase_critical_path_depth(state.phase_id)
            - self.weights.get("manual_effort_penalty", 2) * manual_penalty
            - self.weights.get("precondition_gap_penalty", 4) * precondition_gap
            - self.weights.get("quality_failure_penalty", 5) * quality_penalty
        )

    def _patch_proposal(
        self,
        recommendation_id: str,
        source_sha: str,
        blocked_state: TaskStateSnapshot | None,
        task_lookup: dict[str, Any],
        focus_iteration: str,
        focus_phase: str,
    ) -> RoadmapPatchProposal | None:
        if not self.emit_patch or blocked_state is None:
            return None
        task = task_lookup[blocked_state.task_id]
        reroute_targets = list(task.reroute_to)
        if not reroute_targets:
            for condition in task.quality_checks + task.preconditions:
                if condition.condition_id in blocked_state.failed_quality_checks or (
                    condition.condition_id in blocked_state.failed_preconditions
                ):
                    reroute_targets.extend(condition.reroute_to)
        if not reroute_targets:
            return None

        operations = []
        rationale = []
        for target in reroute_targets:
            operations.append(
                {
                    "op": "insert_before_phase",
                    "task_id": target,
                    "before_phase": blocked_state.phase_id,
                    "blocked_task_id": blocked_state.task_id,
                }
            )
            rationale.append(
                f"Task `{blocked_state.task_id}` is blocked; recommend `{target}` before `{blocked_state.phase_id}`."
            )

        return RoadmapPatchProposal(
            proposal_id=recommendation_id,
            source_roadmap_sha256=source_sha,
            focus_iteration=focus_iteration,
            focus_phase=focus_phase,
            operations=operations,
            rationale=rationale,
        )

    def optimize(self, focus_iteration: str = "", focus_phase: str = "") -> OptimizationReport:
        model = load_roadmap_model(self.roadmap_model_path)
        _ = load_remediation_library(self.remediation_library_path)
        graph = build_task_graph(model)
        deferred_records = self._load_deferred()
        evaluator = ReadinessEvaluator(
            repo_root=self.repo_root,
            graph=graph,
            model=model,
            deferred_records=deferred_records,
        )
        task_states, phase_states = evaluator.evaluate_all()
        task_lookup = graph.tasks_by_id

        scoped_tasks = [
            state
            for state in task_states
            if (not focus_iteration or state.iteration_id == focus_iteration)
            and (not focus_phase or state.phase_id.endswith(focus_phase))
        ]
        scoped_phases = [
            state
            for state in phase_states
            if (not focus_iteration or state.iteration_id == focus_iteration)
            and (not focus_phase or state.phase_id.endswith(focus_phase))
        ]
        if not scoped_tasks and not scoped_phases:
            scoped_tasks = task_states
            scoped_phases = phase_states

        for state in scoped_tasks:
            task = task_lookup[state.task_id]
            state.score = self._score_task(graph, state, task)
        for state in scoped_phases:
            state.score = self._score_phase(graph, state)

        ready_tasks = sorted(
            [state for state in scoped_tasks if state.status == "ready"],
            key=lambda item: (-item.score, item.task_id),
        )
        blocked_tasks = sorted(
            [
                state
                for state in scoped_tasks
                if state.status in {"blocked_precondition", "blocked_quality", "blocked_manual"}
            ],
            key=lambda item: (-item.score, item.task_id),
        )
        ready_phases = sorted(
            [
                state
                for state in scoped_phases
                if state.status == "ready"
                and state.lifecycle_state not in {"historical", "superseded", "completed"}
            ],
            key=lambda item: (-item.score, item.phase_id),
        )
        blocked_phases = sorted(
            [
                state
                for state in scoped_phases
                if state.status
                in {"blocked_precondition", "blocked_quality", "blocked_manual", "deferred"}
                and state.lifecycle_state not in {"historical", "superseded", "completed"}
            ],
            key=lambda item: (-item.score, item.phase_id),
        )

        recommendation_id = self._optimization_id(focus_iteration, focus_phase)
        source_sha = sha256_file(self.roadmap_model_path)
        patch = self._patch_proposal(
            recommendation_id=recommendation_id,
            source_sha=source_sha,
            blocked_state=blocked_tasks[0] if blocked_tasks else None,
            task_lookup=task_lookup,
            focus_iteration=focus_iteration,
            focus_phase=focus_phase,
        )
        patch_file = ""
        if patch is not None:
            patch_file = str(
                self.optimization_dir / f"proposed_roadmap_patch_{recommendation_id}.yaml"
            )
            with Path(patch_file).open("w", encoding="utf-8") as handle:
                yaml.safe_dump(patch.as_deterministic_dict(), handle, sort_keys=False)

        recommended_task_ids = [item.task_id for item in ready_tasks[:3]]
        recommended_phase_ids = [item.phase_id for item in ready_phases[:3]]
        if patch is not None:
            for operation in patch.operations:
                task_id = str(operation.get("task_id", ""))
                if task_id and task_id not in recommended_task_ids:
                    recommended_task_ids.append(task_id)

        policy_block_ids = sorted(
            {policy_id for item in blocked_tasks for policy_id in item.blocked_policy_ids}
            | {policy_id for item in blocked_phases for policy_id in item.blocked_policy_ids}
        )
        source_window_notes = []
        for item in blocked_phases[:3] + ready_phases[:3]:
            source_window_notes.extend(item.source_window_notes)

        recommendation = OptimizationRecommendation(
            recommendation_id=recommendation_id,
            focus_iteration=focus_iteration,
            focus_phase=focus_phase,
            recommended_task_ids=recommended_task_ids[:3],
            recommended_phase_ids=recommended_phase_ids[:3],
            blocked_task_ids=[item.task_id for item in blocked_tasks[:3]],
            blocked_phase_ids=[item.phase_id for item in blocked_phases[:3]],
            policy_block_ids=policy_block_ids,
            reorder_operations=patch.operations if patch is not None else [],
            source_window_notes=sorted(set(source_window_notes)),
            rationale=[
                f"Top ready task `{item.task_id}` has score {item.score:.1f}."
                for item in ready_tasks[:3]
            ]
            + [
                f"Top ready phase `{item.phase_id}` has score {item.score:.1f}."
                for item in ready_phases[:3]
            ]
            + [
                f"Blocked task `{item.task_id}` remains `{item.status}`."
                for item in blocked_tasks[:3]
            ]
            + [
                f"Blocked phase `{item.phase_id}` remains `{item.status}`."
                for item in blocked_phases[:3]
            ]
            + (patch.rationale if patch is not None else []),
            proposal_only=True,
            patch_file=patch_file,
        )

        graph_file = self.optimization_dir / f"graph_{recommendation_id}.json"
        readiness_file = self.optimization_dir / f"readiness_{recommendation_id}.json"
        recommendation_file = self.optimization_dir / f"recommendation_{recommendation_id}.json"
        recommendation_markdown = self.optimization_dir / f"recommendation_{recommendation_id}.md"

        dump_json(graph_file, graph.as_dict())
        dump_json(
            readiness_file,
            {
                "generated_at": now_utc_iso(),
                "task_states": [item.as_deterministic_dict() for item in scoped_tasks],
                "phase_states": [item.as_deterministic_dict() for item in scoped_phases],
            },
        )
        dump_json(recommendation_file, recommendation.as_deterministic_dict())
        recommendation_markdown.write_text(
            render_optimization_markdown(
                recommendation=recommendation,
                task_state_rows=[item.as_deterministic_dict() for item in scoped_tasks],
                phase_state_rows=[item.as_deterministic_dict() for item in scoped_phases],
            ),
            encoding="utf-8",
        )

        return OptimizationReport(
            report_id=recommendation_id,
            source_roadmap_sha256=source_sha,
            graph_file=str(graph_file),
            readiness_file=str(readiness_file),
            recommendation_file=str(recommendation_file),
            recommendation_markdown=str(recommendation_markdown),
            patch_file=patch_file,
            task_states=scoped_tasks,
            recommendation=recommendation,
        )
