"""Iteration and phase review generation, approval, and patch application."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from semantic_ai_washing.director.core.branching import (
    boundary_phase_id,
    closeout_branch_plan,
    current_branch,
    kickoff_checks,
    normalize_branching_policy,
    review_artifact_paths,
)
from semantic_ai_washing.director.core.config import DirectorPaths
from semantic_ai_washing.director.core.readiness import ReadinessEvaluator
from semantic_ai_washing.director.core.render import (
    render_branch_plan_markdown,
    render_review_markdown,
    render_starter_prompt_markdown,
)
from semantic_ai_washing.director.core.roadmap_model import (
    find_phase,
    find_iteration,
    load_roadmap_model,
)
from semantic_ai_washing.director.core.task_graph import build_task_graph
from semantic_ai_washing.director.core.utils import git_info, load_json, now_utc_iso, sha256_file
from semantic_ai_washing.director.schemas import (
    DeferredBlockerRecord,
    IterationReview,
    KickoffReport,
    PhaseReview,
    ReviewApproval,
    ReviewChangeProposal,
    ReviewFinding,
    StarterPromptArtifact,
)


class ReviewEngine:
    def __init__(
        self,
        repo_root: str,
        paths: DirectorPaths,
        roadmap_model_path: str,
        iteration_log_path: str,
    ):
        self.repo_root = Path(repo_root)
        self.paths = paths
        self.roadmap_model_path = Path(roadmap_model_path)
        self.iteration_log_path = Path(iteration_log_path)

    def _model(self):
        return load_roadmap_model(self.roadmap_model_path)

    def _load_deferred(self) -> list[DeferredBlockerRecord]:
        records: list[DeferredBlockerRecord] = []
        for path in sorted(self.paths.decisions_dir.glob("deferred_*.json")):
            records.append(
                DeferredBlockerRecord.model_validate_json(path.read_text(encoding="utf-8"))
            )
        return records

    def _evaluator(self):
        model = self._model()
        graph = build_task_graph(model)
        return (
            model,
            graph,
            ReadinessEvaluator(
                repo_root=str(self.repo_root),
                graph=graph,
                model=model,
                deferred_records=self._load_deferred(),
            ),
        )

    def _review_id(self, iteration_id: str, phase_id: str = "") -> str:
        stem = f"{iteration_id}:{phase_id}:{now_utc_iso()}"
        return sha256_file(self.roadmap_model_path)[:8] + "-" + stem.encode("utf-8").hex()[:8]

    def _runbook_files(self) -> list[Path]:
        return sorted(self.paths.plans_dir.glob("runbook_*.yaml"), key=lambda p: p.stat().st_mtime)

    def _state_file(self, runbook_id: str) -> Path:
        return self.paths.runs_dir / f"execution_state_{runbook_id}.json"

    def _result_file(self, runbook_id: str) -> Path:
        return self.paths.runs_dir / f"execution_result_{runbook_id}.json"

    def _load_scoped_runs(self, iteration_id: str, phase_id: str = "") -> list[dict[str, Any]]:
        scoped: list[dict[str, Any]] = []
        for runbook_file in self._runbook_files():
            runbook = yaml.safe_load(runbook_file.read_text(encoding="utf-8")) or {}
            if str(runbook.get("iteration_id", "")) != str(iteration_id):
                continue
            if (
                phase_id
                and str(runbook.get("phase_name", "")).strip().lower()
                != phase_id.split("/", 1)[-1].lower()
            ):
                continue
            runbook_id = str(runbook.get("runbook_id", ""))
            state = load_json(self._state_file(runbook_id), default={}) or {}
            result = load_json(self._result_file(runbook_id), default={}) or {}
            scoped.append(
                {
                    "runbook": runbook,
                    "runbook_file": str(runbook_file),
                    "state": state,
                    "state_file": str(self._state_file(runbook_id)),
                    "result": result,
                    "result_file": str(self._result_file(runbook_id)),
                }
            )
        return scoped

    @staticmethod
    def _parse_iso(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    def _duration_seconds(self, start: str | None, end: str | None) -> float:
        start_dt = self._parse_iso(start)
        end_dt = self._parse_iso(end)
        if start_dt is None or end_dt is None:
            return 0.0
        return max(0.0, (end_dt - start_dt).total_seconds())

    def _normalized_command_stem(self, blocker: dict[str, Any]) -> str:
        message = str(blocker.get("message", ""))
        if "Step command failed: " in message:
            command = message.split("Step command failed: ", 1)[1].strip()
            try:
                first = command.split()[0]
            except IndexError:
                return message or "unknown"
            return Path(first).name or first
        return message or "unknown"

    def _phase_status_map(
        self, iteration_id: str, phase_id: str = ""
    ) -> dict[str, dict[str, Any]]:
        model = self._model()
        iteration = find_iteration(model, iteration_id)
        if iteration is None:
            return {}
        runs = self._load_scoped_runs(iteration_id, phase_id=phase_id)
        by_phase: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for item in runs:
            phase_name = str(item["runbook"].get("phase_name", ""))
            full_phase_id = f"iteration{iteration_id}/{phase_name}"
            by_phase[full_phase_id].append(item)
        summary: dict[str, dict[str, Any]] = {}
        for phase in iteration.phases:
            if phase_id and phase.phase_id != phase_id:
                continue
            scoped_runs = sorted(
                by_phase.get(phase.phase_id, []),
                key=lambda item: str(item["state"].get("updated_at", "")),
            )
            latest = scoped_runs[-1] if scoped_runs else None
            if (
                phase.lifecycle_state in {"historical", "superseded", "completed", "deferred"}
                and latest is None
            ):
                status = phase.lifecycle_state
            elif latest is None:
                status = "unstarted"
            else:
                latest_result = latest.get("result", {})
                latest_state = latest.get("state", {})
                status = latest_result.get("status") or latest_state.get("status") or "unknown"
            summary[phase.phase_id] = {
                "phase_id": phase.phase_id,
                "title": phase.title,
                "goal": phase.goal,
                "lifecycle_state": phase.lifecycle_state,
                "status": status,
                "run_count": len(scoped_runs),
                "latest_runbook_id": latest["runbook"].get("runbook_id", "") if latest else "",
                "latest_state_file": latest["state_file"] if latest else "",
                "latest_result_file": latest["result_file"] if latest else "",
            }
        return summary

    def _timing_summary(self, runs: list[dict[str, Any]]) -> dict[str, Any]:
        total_automated = 0.0
        total_validation = 0.0
        slowest_command = {"command": "", "seconds": 0.0, "phase_id": ""}
        phase_runtime: dict[str, float] = defaultdict(float)
        rerun_count = 0
        seen_phase_runs: Counter[str] = Counter()

        for item in runs:
            phase_id = f"iteration{item['runbook'].get('iteration_id', '')}/{item['runbook'].get('phase_name', '')}"
            seen_phase_runs[phase_id] += 1
            if seen_phase_runs[phase_id] > 1:
                rerun_count += 1
            for step in (item.get("state", {}).get("step_results", {}) or {}).values():
                command_result = step.get("command_result") or {}
                seconds = self._duration_seconds(
                    command_result.get("started_at"), command_result.get("finished_at")
                )
                if seconds <= 0:
                    continue
                total_automated += seconds
                phase_runtime[phase_id] += seconds
                if str(step.get("title", "")).startswith("Validation command"):
                    total_validation += seconds
                if seconds > slowest_command["seconds"]:
                    slowest_command = {
                        "command": command_result.get("command", ""),
                        "seconds": round(seconds, 3),
                        "phase_id": phase_id,
                    }

        slowest_phase = {"phase_id": "", "seconds": 0.0}
        if phase_runtime:
            phase_id, seconds = max(phase_runtime.items(), key=lambda item: item[1])
            slowest_phase = {"phase_id": phase_id, "seconds": round(seconds, 3)}

        return {
            "total_automated_runtime_seconds": round(total_automated, 3),
            "total_validation_runtime_seconds": round(total_validation, 3),
            "slowest_phase": slowest_phase,
            "slowest_command": slowest_command,
            "rerun_count": rerun_count,
        }

    def _blocker_summary(
        self, runs: list[dict[str, Any]]
    ) -> tuple[dict[str, Any], list[ReviewFinding]]:
        blockers: list[dict[str, Any]] = []
        for item in runs:
            blocker = item.get("state", {}).get("blocker")
            if blocker:
                blockers.append(blocker)
        blocker_types = Counter(
            str(blocker.get("blocker_type", "unknown")) for blocker in blockers
        )
        grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        findings: list[ReviewFinding] = []
        for blocker in blockers:
            signature = (
                str(blocker.get("blocker_type", "unknown")),
                self._normalized_command_stem(blocker),
            )
            grouped[signature].append(blocker)
        repeated = []
        for (blocker_type, stem), items in sorted(grouped.items()):
            repeated.append(
                {
                    "blocker_type": blocker_type,
                    "signature": stem,
                    "count": len(items),
                    "blocker_ids": [item.get("blocker_id", "") for item in items],
                }
            )
            if len(items) > 1:
                findings.append(
                    ReviewFinding(
                        scope="phase"
                        if len({item.get("step_id") for item in items}) == 1
                        else "iteration",
                        finding_id=f"{blocker_type}-{stem}",
                        category="runtime_contract"
                        if blocker_type == "runtime"
                        else "manual_workflow",
                        severity="high" if blocker_type in {"runtime", "manual"} else "medium",
                        summary=f"Repeated blocker `{stem}` occurred {len(items)} times.",
                        evidence_refs=[item.get("blocker_id", "") for item in items],
                        recommended_action="Review preconditions, request shape, and gate ordering before retrying the same step.",
                    )
                )
        return {
            "blocker_count": len(blockers),
            "by_type": dict(blocker_types),
            "repeated_signatures": repeated,
        }, findings

    def _manual_summary(self, iteration_id: str, phase_id: str = "") -> dict[str, Any]:
        model, _, evaluator = self._evaluator()
        task_states, _ = evaluator.evaluate_all()
        iteration = find_iteration(model, iteration_id)
        if iteration is None:
            return {
                "manual_task_count": 0,
                "blocked_manual_count": 0,
                "satisfied_manual_count": 0,
                "tasks": [],
            }
        manual_tasks = []
        for state in task_states:
            task = next(
                (
                    task
                    for phase in iteration.phases
                    for task in phase.tasks
                    if task.task_id == state.task_id
                ),
                None,
            )
            if task is None:
                continue
            if phase_id and task.phase_id != phase_id:
                continue
            if task.manual_handoff or task.automation_level == "manual":
                manual_tasks.append(
                    {
                        "task_id": task.task_id,
                        "phase_id": task.phase_id,
                        "status": state.status,
                        "outputs": [artifact.path for artifact in task.outputs],
                    }
                )
        return {
            "manual_task_count": len(manual_tasks),
            "blocked_manual_count": sum(
                1 for item in manual_tasks if item["status"] == "blocked_manual"
            ),
            "satisfied_manual_count": sum(
                1 for item in manual_tasks if item["status"] == "satisfied"
            ),
            "tasks": manual_tasks,
        }

    def _quality_summary(
        self, iteration_id: str, phase_summary: dict[str, Any]
    ) -> tuple[dict[str, Any], list[ReviewFinding]]:
        findings: list[ReviewFinding] = []
        highlights: dict[str, Any] = {}
        report_paths: list[str] = []
        for item in phase_summary.values():
            phase_id = item["phase_id"]
            phase = find_phase(self._model(), iteration_id, phase_id.split("/", 1)[-1])
            if phase is None:
                continue
            for artifact in phase.required_artifacts:
                if artifact.endswith(".json") and Path(artifact).exists():
                    report_paths.append(artifact)
        for path in sorted(set(report_paths)):
            payload = load_json(path, default={}) or {}
            selected = {}
            for key in [
                "fragment_rate",
                "status",
                "selection",
                "quality",
                "summary",
            ]:
                if key in payload:
                    selected[key] = payload[key]
            if selected:
                highlights[path] = selected
            if path.endswith("pilot_2024_sentence_quality.json"):
                fragment_rate = float(payload.get("fragment_rate", 0.0) or 0.0)
                if fragment_rate > 0.0 and fragment_rate <= 0.15:
                    findings.append(
                        ReviewFinding(
                            scope="iteration",
                            finding_id="sentence-quality-threshold",
                            category="data_quality",
                            severity="low",
                            summary=(
                                f"Sentence pilot quality passed, but fragment_rate={fragment_rate:.6f} should remain a tracked gate in later iterations."
                            ),
                            evidence_refs=[path],
                            recommended_action="Keep sentence-quality gates before labeling and IRR tasks.",
                        )
                    )
            if path.endswith("labeling_batch_v1_summary.json"):
                quotas = (payload.get("selection", {}) or {}).get("quarter_quotas_used", {})
                if quotas and len(set(quotas.values())) > 1:
                    findings.append(
                        ReviewFinding(
                            scope="iteration",
                            finding_id="availability-aware-quartering",
                            category="gate_overconstraint",
                            severity="medium",
                            summary="Strict equal quarter quotas were infeasible after leakage-safe filtering; availability-aware redistribution was required.",
                            evidence_refs=[path],
                            recommended_action="Preserve availability-aware quota logic in future manual labeling stages.",
                        )
                    )
        return {"reports": highlights}, findings

    @staticmethod
    def _phase_iteration_number(phase_id: str) -> int | None:
        if not phase_id.startswith("iteration"):
            return None
        head = phase_id.split("/", 1)[0].replace("iteration", "")
        return int(head) if head.isdigit() else None

    def _stakeholder_alignment(
        self, iteration_id: str
    ) -> tuple[dict[str, Any], list[str], list[str], list[str]]:
        model, _, evaluator = self._evaluator()
        _, phase_states = evaluator.evaluate_all()
        phase_statuses = {state.phase_id: state.status for state in phase_states}
        current_iteration = int(iteration_id)
        by_priority = Counter()
        by_status = Counter()
        due_unsatisfied = 0
        requirement_rows: list[dict[str, Any]] = []
        unmet_requirements: list[str] = []
        deferred_requirements: list[str] = []
        publication_blockers: list[str] = []

        for requirement in model.stakeholder_alignment.requirements:
            mapped_statuses = [
                phase_statuses.get(phase_id, "unmapped") for phase_id in requirement.mapped_phases
            ]
            if mapped_statuses and all(
                status in {"satisfied", "completed", "historical", "superseded"}
                for status in mapped_statuses
            ):
                status = "satisfied"
            elif mapped_statuses and all(status == "deferred" for status in mapped_statuses):
                status = "deferred"
            elif mapped_statuses and any(
                status in {"satisfied", "completed", "historical", "superseded"}
                for status in mapped_statuses
            ):
                status = "in_progress"
            else:
                status = "open"

            target_iteration = (
                int(requirement.target_iteration)
                if str(requirement.target_iteration).isdigit()
                else 0
            )
            due_now = target_iteration > 0 and target_iteration <= current_iteration

            by_priority[requirement.priority] += 1
            by_status[status] += 1
            if status == "deferred":
                deferred_requirements.append(requirement.requirement_id)
            if due_now and status != "satisfied":
                due_unsatisfied += 1
                if requirement.priority in {"non-negotiable", "publication-critical"}:
                    unmet_requirements.append(requirement.requirement_id)
                    publication_blockers.append(
                        f"{requirement.requirement_id}: {requirement.summary}"
                    )

            requirement_rows.append(
                {
                    "requirement_id": requirement.requirement_id,
                    "priority": requirement.priority,
                    "target_iteration": requirement.target_iteration,
                    "status": status,
                    "mapped_phases": list(requirement.mapped_phases),
                    "mapped_statuses": mapped_statuses,
                }
            )

        summary = {
            "source_artifact": model.stakeholder_alignment.source_artifact,
            "active_development_scope": model.stakeholder_alignment.active_development_scope,
            "publication_target_scope": model.stakeholder_alignment.publication_target_scope,
            "desired_horizon": model.stakeholder_alignment.desired_horizon,
            "counts_by_priority": dict(by_priority),
            "counts_by_status": dict(by_status),
            "due_unsatisfied_count": due_unsatisfied,
            "requirement_statuses": requirement_rows,
        }
        return summary, unmet_requirements, deferred_requirements, publication_blockers

    def _carryover_blockers(self, iteration_id: str) -> list[dict[str, Any]]:
        carryover: list[dict[str, Any]] = []
        for path in sorted(self.paths.decisions_dir.glob("deferred_*.json")):
            payload = load_json(path, default={}) or {}
            if payload.get("status") != "active":
                continue
            if int(str(payload.get("until_iteration", "0") or 0)) >= int(iteration_id):
                payload["path"] = str(path)
                carryover.append(payload)
        return carryover

    def _starter_prompt(
        self, iteration_id: str, phase_summary: dict[str, Any]
    ) -> StarterPromptArtifact:
        model = self._model()
        next_iteration_id = str(int(iteration_id) + 1)
        next_iteration = find_iteration(model, next_iteration_id)
        next_phase = (
            boundary_phase_id(next_iteration_id, "kickoff") if next_iteration is not None else ""
        )
        commits = []
        for item in self._load_scoped_runs(iteration_id):
            commit = str((item.get("state", {}).get("git", {}) or {}).get("commit", ""))
            if commit and commit not in commits:
                commits.append(commit)
        artifacts = []
        for item in phase_summary.values():
            state_file = item.get("latest_state_file", "")
            result_file = item.get("latest_result_file", "")
            if state_file:
                artifacts.append(state_file)
            if result_file:
                artifacts.append(result_file)
        prompt_path = review_artifact_paths(self.paths.reviews_dir, iteration_id)["starter_prompt"]
        return StarterPromptArtifact(
            iteration_id=iteration_id,
            generated_at=now_utc_iso(),
            recommended_new_chat=bool(
                self._model().branching_policy.suggest_new_chat_at_iteration_boundary
            ),
            prompt_markdown_path=str(prompt_path),
            stable_checkpoint_commits=commits,
            key_artifacts=artifacts[:12],
            next_phase=next_phase,
            constraints=[
                "Do not start the next iteration before review approval.",
                "Use the iteration integration branch as the default working base.",
            ],
        )

    def _roadmap_changes(
        self,
        iteration_id: str,
        findings: list[ReviewFinding],
        focus_phase: str = "",
    ) -> tuple[list[ReviewChangeProposal], dict[str, Any]]:
        changes: list[ReviewChangeProposal] = []
        operations: list[dict[str, Any]] = []
        rationale: list[str] = []
        for path in sorted(self.paths.optimization_dir.glob("proposed_roadmap_patch_*.yaml")):
            payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if payload.get("focus_iteration") and str(payload.get("focus_iteration")) != str(
                iteration_id
            ):
                continue
            for idx, operation in enumerate(payload.get("operations", []) or []):
                change_id = f"optimizer-{path.stem}-{idx + 1}"
                changes.append(
                    ReviewChangeProposal(
                        change_id=change_id,
                        source="optimizer_patch",
                        operation=operation,
                        target=str(
                            operation.get("before_phase") or operation.get("task_id") or "roadmap"
                        ),
                        rationale=(payload.get("rationale") or ["optimizer proposal"])[0],
                    )
                )
                operations.append(operation)
                rationale.append((payload.get("rationale") or ["optimizer proposal"])[0])
        next_iteration_id = str(int(iteration_id) + 1)
        for finding in findings:
            operation = None
            if finding.finding_id == "availability-aware-quartering":
                operation = {
                    "op": "append_iteration_entry_criteria",
                    "iteration_id": next_iteration_id,
                    "value": (
                        "Use availability-aware quarter redistribution when leakage-safe filtering "
                        "makes strict equal quarter quotas infeasible."
                    ),
                }
            elif finding.finding_id == "sentence-quality-threshold":
                operation = {
                    "op": "append_iteration_entry_criteria",
                    "iteration_id": next_iteration_id,
                    "value": "Maintain sentence-quality gate <= 0.15 before manual labeling and IRR.",
                }
            if operation is None:
                continue
            change_id = f"review-{finding.finding_id}"
            if any(change.change_id == change_id for change in changes):
                continue
            changes.append(
                ReviewChangeProposal(
                    change_id=change_id,
                    source="review_inference",
                    operation=operation,
                    target=f"iteration{next_iteration_id}",
                    rationale=finding.recommended_action,
                )
            )
            operations.append(operation)
            rationale.append(f"Review inference: {finding.summary}")
        if not changes:
            rationale.append("No additional roadmap mutations proposed from this review.")
        patch = {
            "schema_version": "1.0.0",
            "proposal_id": self._review_id(iteration_id, focus_phase),
            "source_roadmap_sha256": sha256_file(self.roadmap_model_path),
            "focus_iteration": iteration_id,
            "focus_phase": focus_phase,
            "operations": operations,
            "rationale": rationale,
        }
        return changes, patch

    def _branch_closeout(self, iteration_id: str) -> dict[str, Any]:
        policy = normalize_branching_policy(self._model())
        return closeout_branch_plan(policy, iteration_id, current_branch(str(self.repo_root)))

    def _next_iteration_payload(
        self, iteration_id: str, starter: StarterPromptArtifact
    ) -> dict[str, Any]:
        model = self._model()
        next_iteration_id = str(int(iteration_id) + 1)
        next_iteration = find_iteration(model, next_iteration_id)
        if next_iteration is None:
            return {
                "iteration_id": "",
                "recommended_phase": "",
                "entry_criteria": [],
                "authorized": False,
            }
        return {
            "iteration_id": next_iteration_id,
            "recommended_phase": starter.next_phase,
            "entry_criteria": list(next_iteration.entry_criteria),
            "authorized": False,
        }

    def generate_review(
        self, iteration_id: str, phase_name: str = ""
    ) -> IterationReview | PhaseReview:
        model = self._model()
        phase_id = ""
        if phase_name:
            phase = find_phase(model, iteration_id, phase_name)
            if phase is None:
                raise ValueError(f"Unknown phase for iteration {iteration_id}: {phase_name}")
            phase_id = phase.phase_id
        runs = self._load_scoped_runs(iteration_id, phase_id=phase_id)
        phase_summary = self._phase_status_map(iteration_id, phase_id=phase_id)
        blocker_summary, blocker_findings = self._blocker_summary(runs)
        quality_summary, quality_findings = self._quality_summary(iteration_id, phase_summary)
        (
            stakeholder_summary,
            unmet_stakeholder_requirements,
            deferred_stakeholder_requirements,
            publication_readiness_blockers,
        ) = self._stakeholder_alignment(iteration_id)
        starter = self._starter_prompt(iteration_id, phase_summary)
        roadmap_changes, patch = self._roadmap_changes(
            iteration_id, blocker_findings + quality_findings, focus_phase=phase_id
        )
        branch_closeout = self._branch_closeout(iteration_id)
        artifacts = review_artifact_paths(self.paths.reviews_dir, iteration_id, phase_id=phase_id)
        prompt_markdown = render_starter_prompt_markdown(starter)
        artifacts["starter_prompt"].write_text(prompt_markdown, encoding="utf-8")
        artifacts["branch_plan"].write_text(
            render_branch_plan_markdown(
                branch_closeout, starter.next_phase, starter.prompt_markdown_path
            ),
            encoding="utf-8",
        )
        with artifacts["patch_yaml"].open("w", encoding="utf-8") as handle:
            yaml.safe_dump(patch, handle, sort_keys=False)

        common_payload = dict(
            review_id=self._review_id(iteration_id, phase_id=phase_id),
            iteration_id=iteration_id,
            generated_at=now_utc_iso(),
            git=git_info(str(self.repo_root)),
            inputs={
                "roadmap_model": str(self.roadmap_model_path),
                "iteration_log": str(self.iteration_log_path),
                "run_count": len(runs),
            },
            phase_summary={
                "phases": list(phase_summary.values()),
                "completed": sorted(
                    phase_id
                    for phase_id, item in phase_summary.items()
                    if item["status"] == "passed"
                ),
                "blocked": sorted(
                    phase_id
                    for phase_id, item in phase_summary.items()
                    if str(item["status"]).startswith("blocked")
                ),
                "deferred": sorted(
                    phase_id
                    for phase_id, item in phase_summary.items()
                    if item["status"] in {"deferred", "deferred_blocked"}
                ),
                "historical": sorted(
                    phase_id
                    for phase_id, item in phase_summary.items()
                    if item["lifecycle_state"] in {"historical", "superseded"}
                ),
            },
            blocker_summary=blocker_summary,
            timing_summary=self._timing_summary(runs),
            manual_summary=self._manual_summary(iteration_id, phase_id=phase_id),
            quality_summary=quality_summary,
            stakeholder_alignment_summary=stakeholder_summary,
            unmet_stakeholder_requirements=unmet_stakeholder_requirements,
            deferred_stakeholder_requirements=deferred_stakeholder_requirements,
            publication_readiness_blockers=publication_readiness_blockers,
            findings=blocker_findings + quality_findings,
            roadmap_changes=roadmap_changes,
            carryover_blockers=self._carryover_blockers(iteration_id),
            branch_closeout=branch_closeout,
            next_iteration=self._next_iteration_payload(iteration_id, starter),
            artifacts={key: str(path) for key, path in artifacts.items()},
            status="draft",
        )

        if phase_id:
            review = PhaseReview(phase_id=phase_id, **common_payload)
        else:
            review = IterationReview(**common_payload)
        artifacts["review_json"].write_text(
            json.dumps(review.as_deterministic_dict(), indent=2), encoding="utf-8"
        )
        artifacts["review_md"].write_text(render_review_markdown(review), encoding="utf-8")
        return review

    def _find_review_path(self, review_id: str) -> Path:
        for path in sorted(self.paths.reviews_dir.glob("*_review.json")):
            payload = load_json(path, default={}) or {}
            if payload.get("review_id") == review_id:
                return path
        raise FileNotFoundError(f"Unable to locate review file for review_id={review_id}")

    def approve_review(self, review_file: str, decision: str, accept_patch: str) -> ReviewApproval:
        review_path = Path(review_file)
        payload = load_json(review_path, default={}) or {}
        review_type = str(payload.get("review_type", "iteration"))
        change_ids = [item.get("change_id", "") for item in payload.get("roadmap_changes", [])]
        if accept_patch == "all":
            accepted = list(change_ids)
        elif accept_patch == "none":
            accepted = []
        else:
            accepted = [item.strip() for item in accept_patch.split(",") if item.strip()]
        deferred = [change_id for change_id in change_ids if change_id not in accepted]
        for change in payload.get("roadmap_changes", []):
            change["status"] = "accepted" if change.get("change_id") in accepted else "deferred"
        payload["status"] = "approved" if decision == "approve" else "deferred"
        review_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        approval = ReviewApproval(
            approval_id=self._review_id(
                str(payload.get("iteration_id", "")), str(payload.get("phase_id", ""))
            ),
            review_id=str(payload.get("review_id", "")),
            iteration_id=str(payload.get("iteration_id", "")),
            decision="approved" if decision == "approve" else "deferred",
            accepted_change_ids=accepted,
            deferred_change_ids=deferred,
            branch_closeout_approved=decision == "approve" and review_type == "iteration",
            next_iteration_authorized=decision == "approve" and review_type == "iteration",
            created_at=now_utc_iso(),
            notes="manual review approval recorded",
        )
        if review_type == "phase":
            phase_id = str(payload.get("phase_id", ""))
            out_path = review_artifact_paths(
                self.paths.reviews_dir, approval.iteration_id, phase_id=phase_id
            )["approval_json"]
        else:
            out_path = review_artifact_paths(self.paths.reviews_dir, approval.iteration_id)[
                "approval_json"
            ]
        out_path.write_text(
            json.dumps(approval.as_deterministic_dict(), indent=2), encoding="utf-8"
        )
        return approval

    def apply_review_patch(self, approval_file: str) -> dict[str, Any]:
        approval = ReviewApproval.model_validate_json(
            Path(approval_file).read_text(encoding="utf-8")
        )
        review_path = self._find_review_path(approval.review_id)
        review_payload = load_json(review_path, default={}) or {}
        patch_path = Path(str((review_payload.get("artifacts") or {}).get("patch_yaml", "")))
        patch_payload = yaml.safe_load(patch_path.read_text(encoding="utf-8")) or {}
        accepted_ids = set(approval.accepted_change_ids)
        accepted_operations = []
        for change in review_payload.get("roadmap_changes", []):
            if change.get("change_id") not in accepted_ids:
                continue
            accepted_operations.append(change.get("operation") or {})

        model_payload = yaml.safe_load(self.roadmap_model_path.read_text(encoding="utf-8")) or {}
        updated_payload = deepcopy(model_payload)
        applied = []
        skipped = []
        for operation in accepted_operations:
            op = str(operation.get("op", ""))
            if op == "append_iteration_entry_criteria":
                iteration = next(
                    (
                        item
                        for item in updated_payload.get("iterations", [])
                        if str(item.get("iteration_id")) == str(operation.get("iteration_id"))
                    ),
                    None,
                )
                if iteration is None:
                    continue
                criteria = iteration.setdefault("entry_criteria", [])
                value = str(operation.get("value", "")).strip()
                if value and value not in criteria:
                    criteria.append(value)
                    applied.append(operation)
            elif op == "append_iteration_exit_criteria":
                iteration = next(
                    (
                        item
                        for item in updated_payload.get("iterations", [])
                        if str(item.get("iteration_id")) == str(operation.get("iteration_id"))
                    ),
                    None,
                )
                if iteration is None:
                    continue
                criteria = iteration.setdefault("exit_criteria", [])
                value = str(operation.get("value", "")).strip()
                if value and value not in criteria:
                    criteria.append(value)
                    applied.append(operation)
            elif op == "append_phase_dependency":
                for iteration in updated_payload.get("iterations", []):
                    for phase in iteration.get("phases", []):
                        if str(phase.get("phase_id")) != str(operation.get("phase_id")):
                            continue
                        deps = phase.setdefault("depends_on", [])
                        value = str(operation.get("dependency", "")).strip()
                        if value and value not in deps:
                            deps.append(value)
                            applied.append(operation)
            elif op == "set_phase_lifecycle":
                for iteration in updated_payload.get("iterations", []):
                    for phase in iteration.get("phases", []):
                        if str(phase.get("phase_id")) != str(operation.get("phase_id")):
                            continue
                        phase["lifecycle_state"] = str(
                            operation.get(
                                "lifecycle_state", phase.get("lifecycle_state", "planned")
                            )
                        )
                        applied.append(operation)
            else:
                skipped.append(
                    {
                        "operation": operation,
                        "reason": "unsupported_patch_operation",
                    }
                )
        self.roadmap_model_path.write_text(
            yaml.safe_dump(updated_payload, sort_keys=False), encoding="utf-8"
        )
        result_path = review_artifact_paths(self.paths.reviews_dir, approval.iteration_id)[
            "patch_apply_json"
        ]
        result = {
            "review_id": approval.review_id,
            "approval_file": str(approval_file),
            "patch_file": str(patch_path),
            "applied_operations": applied,
            "skipped_operations": skipped,
            "source_patch_operations": patch_payload.get("operations", []),
            "roadmap_model_path": str(self.roadmap_model_path),
            "applied_at": now_utc_iso(),
        }
        result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result

    def kickoff(self, iteration_id: str) -> KickoffReport:
        model = self._model()
        policy = normalize_branching_policy(model)
        expected_branch = policy.integration_branch_template.format(
            iteration_id=iteration_id, slug="work"
        )
        previous_iteration_id = str(int(iteration_id) - 1)
        approval_file = ""
        checks = kickoff_checks(str(self.repo_root), policy, iteration_id)
        rationale: list[str] = []
        starter_prompt_path = ""
        branch_plan_path = ""
        if int(iteration_id) > 1:
            approval_path = review_artifact_paths(self.paths.reviews_dir, previous_iteration_id)[
                "approval_json"
            ]
            approval_file = str(approval_path)
            if approval_path.exists():
                approval_payload = load_json(approval_path, default={}) or {}
                authorized = bool(approval_payload.get("next_iteration_authorized", False))
                checks.append(
                    {
                        "name": "prior_review_approval",
                        "ok": authorized,
                        "detail": f"approval={authorized}",
                    }
                )
                starter_prompt_path = str(
                    review_artifact_paths(self.paths.reviews_dir, previous_iteration_id)[
                        "starter_prompt"
                    ]
                )
                branch_plan_path = str(
                    review_artifact_paths(self.paths.reviews_dir, previous_iteration_id)[
                        "branch_plan"
                    ]
                )
            else:
                checks.append(
                    {
                        "name": "prior_review_approval",
                        "ok": False,
                        "detail": f"missing {approval_path}",
                    }
                )
        ok = all(check["ok"] for check in checks)
        if not ok:
            rationale.append(
                "Kickoff is blocked until branch context and prior review approval are valid."
            )
        else:
            rationale.append("Kickoff checks passed for the iteration integration branch.")
        report = KickoffReport(
            kickoff_id=self._review_id(iteration_id, phase_id="kickoff"),
            iteration_id=iteration_id,
            generated_at=now_utc_iso(),
            git=git_info(str(self.repo_root)),
            expected_branch=expected_branch,
            base_branch=policy.merge_target,
            review_approval_file=approval_file,
            checks=checks,
            status="ready" if ok else "blocked",
            starter_prompt_path=starter_prompt_path,
            branch_plan_path=branch_plan_path,
            rationale=rationale,
        )
        out_path = review_artifact_paths(self.paths.reviews_dir, iteration_id)["kickoff_json"]
        out_path.write_text(json.dumps(report.as_deterministic_dict(), indent=2), encoding="utf-8")
        return report


def load_approved_review_summaries(reviews_dir: str | Path) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    base = Path(reviews_dir)
    for approval_path in sorted(base.glob("*_approval.json")):
        approval = load_json(approval_path, default={}) or {}
        if approval.get("decision") != "approved":
            continue
        review_id = approval.get("review_id", "")
        review_path = None
        for candidate in sorted(base.glob("*_review.json")):
            payload = load_json(candidate, default={}) or {}
            if payload.get("review_id") == review_id:
                review_path = candidate
                review = payload
                break
        if review_path is None:
            continue
        summaries.append(
            {
                "review_id": review.get("review_id", ""),
                "review_type": review.get("review_type", ""),
                "iteration_id": review.get("iteration_id", ""),
                "phase_id": review.get("phase_id", ""),
                "status": review.get("status", ""),
                "findings_count": len(review.get("findings", [])),
                "accepted_change_ids": approval.get("accepted_change_ids", []),
                "deferred_change_ids": approval.get("deferred_change_ids", []),
                "next_iteration": review.get("next_iteration", {}),
                "stakeholder_alignment_summary": review.get("stakeholder_alignment_summary", {}),
                "unmet_stakeholder_requirements": review.get("unmet_stakeholder_requirements", []),
                "publication_readiness_blockers": review.get("publication_readiness_blockers", []),
            }
        )
    return summaries
