"""Autonomous runbook execution controller."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from semantic_ai_washing.director.core.audit import write_audit_record
from semantic_ai_washing.director.core.decision import DecisionEngine
from semantic_ai_washing.director.core.gates import GateEvaluator
from semantic_ai_washing.director.core.utils import dump_json, git_info, now_utc_iso, run_command
from semantic_ai_washing.director.schemas import BlockerEvent, Runbook


class RunbookExecutor:
    def __init__(
        self,
        repo_root: str,
        runs_dir: str,
        decisions_dir: str,
        autonomy_policy: dict[str, Any],
    ):
        self.repo_root = repo_root
        self.runs_dir = Path(runs_dir)
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.decision_engine = DecisionEngine(decisions_dir=decisions_dir)
        self.autonomy_policy = autonomy_policy

    def _load_runbook(self, runbook_path: str) -> Runbook:
        payload = yaml.safe_load(Path(runbook_path).read_text(encoding="utf-8"))
        return Runbook.model_validate(payload)

    def _state_path(self, runbook_id: str) -> Path:
        return self.runs_dir / f"execution_state_{runbook_id}.json"

    def _result_path(self, runbook_id: str) -> Path:
        return self.runs_dir / f"execution_result_{runbook_id}.json"

    def _load_or_init_state(self, runbook: Runbook, resume: bool) -> dict[str, Any]:
        state_path = self._state_path(runbook.runbook_id)
        if resume and state_path.exists():
            return json.loads(state_path.read_text(encoding="utf-8"))
        return {
            "runbook_id": runbook.runbook_id,
            "started_at": now_utc_iso(),
            "updated_at": now_utc_iso(),
            "mode": "autonomous",
            "git": git_info(self.repo_root),
            "step_results": {},
            "status": "running",
            "blocker": None,
            "decision_file": None,
        }

    def _save_state(self, state: dict[str, Any]) -> None:
        state["updated_at"] = now_utc_iso()
        dump_json(self._state_path(state["runbook_id"]), state)

    def _block_and_decide(self, state: dict[str, Any], blocker: BlockerEvent) -> dict[str, Any]:
        decision = self.decision_engine.decide(
            blocker=blocker,
            selected_option_id=None,
            require_manual_selection=bool(
                self.autonomy_policy.get("require_explicit_recovery_selection", True)
            ),
        )
        decision_file = self.decision_engine.write_decision(decision)
        state["status"] = "blocked"
        state["blocker"] = blocker.as_deterministic_dict()
        state["decision_file"] = str(decision_file)
        self._save_state(state)

        write_audit_record(
            base_dir=self.runs_dir,
            record_type="blocker",
            payload={
                "runbook_id": state["runbook_id"],
                "blocker": blocker.as_deterministic_dict(),
                "decision_file": str(decision_file),
            },
        )
        state["state_file"] = str(self._state_path(state["runbook_id"]))
        return state

    def run(
        self, runbook_path: str, mode: str = "autonomous", resume: bool = False
    ) -> dict[str, Any]:
        runbook = self._load_runbook(runbook_path)
        state = self._load_or_init_state(runbook, resume=resume)
        state["mode"] = mode
        if resume and state.get("status") == "deferred_blocked":
            deferred = state.get("deferred", {})
            due = (
                str(deferred.get("until_iteration", "")) == str(runbook.iteration_id)
                and str(deferred.get("until_phase", "")).strip().lower()
                == str(runbook.phase_name).strip().lower()
            )
            if not due:
                self._save_state(state)
                return {
                    "runbook_id": runbook.runbook_id,
                    "status": "deferred_blocked",
                    "state_file": str(self._state_path(runbook.runbook_id)),
                    "result_file": "",
                    "step_count": len(runbook.steps),
                    "steps_passed": sum(
                        1
                        for item in state.get("step_results", {}).values()
                        if item.get("status") == "passed"
                    ),
                    "deferred_until_iteration": deferred.get("until_iteration", ""),
                    "deferred_until_phase": deferred.get("until_phase", ""),
                }
            state["status"] = "running"
            state["deferred_recheck_started_at"] = now_utc_iso()
            self._save_state(state)

        gate_lookup = {gate.gate_id: gate for gate in runbook.gates}
        gate_evaluator = GateEvaluator(repo_root=self.repo_root)
        repo_root_path = Path(self.repo_root).resolve()

        for step in runbook.steps:
            existing = state["step_results"].get(step.step_id)
            if existing and existing.get("status") == "passed":
                continue

            state["step_results"][step.step_id] = {
                "status": "running",
                "title": step.title,
                "command": step.command,
                "started_at": now_utc_iso(),
            }
            self._save_state(state)

            if step.command:
                step_cwd = Path(step.cwd)
                normalized_cwd = (
                    step_cwd.resolve()
                    if step_cwd.is_absolute()
                    else (repo_root_path / step_cwd).resolve()
                )
                result = run_command(
                    step.command,
                    cwd=str(normalized_cwd),
                    timeout_seconds=step.timeout_seconds,
                )
                state["step_results"][step.step_id]["command_result"] = result
                if result["exit_code"] != 0:
                    blocker = BlockerEvent(
                        blocker_id=f"{runbook.runbook_id}-{step.step_id}-runtime",
                        blocker_type="runtime",
                        severity="high",
                        message=f"Step command failed: {step.command}",
                        step_id=step.step_id,
                        context={
                            "exit_code": result["exit_code"],
                            "stderr": result["stderr"][-500:],
                            "stdout": result["stdout"][-500:],
                        },
                    )
                    state["step_results"][step.step_id]["status"] = "failed"
                    self._save_state(state)
                    return self._block_and_decide(state, blocker)

            missing_outputs = [path for path in step.required_outputs if not Path(path).exists()]
            if missing_outputs:
                blocker = BlockerEvent(
                    blocker_id=f"{runbook.runbook_id}-{step.step_id}-data",
                    blocker_type="data",
                    severity="high",
                    message=f"Required outputs missing for {step.step_id}",
                    step_id=step.step_id,
                    context={"missing_outputs": missing_outputs},
                )
                state["step_results"][step.step_id]["status"] = "failed"
                state["step_results"][step.step_id]["missing_outputs"] = missing_outputs
                self._save_state(state)
                return self._block_and_decide(state, blocker)

            for gate_id in step.gate_ids:
                gate = gate_lookup.get(gate_id)
                if gate is None:
                    continue
                if gate_id.endswith("-gate-001"):
                    validation_steps = [
                        result
                        for result in state["step_results"].values()
                        if isinstance(result, dict)
                        and str(result.get("title", "")).startswith("Validation command")
                    ]
                    validation_passed = bool(validation_steps) and all(
                        item.get("status") == "passed" for item in validation_steps
                    )
                    gate_result = {
                        "gate_id": gate.gate_id,
                        "name": gate.name,
                        "passed": validation_passed,
                        "missing_outputs": [],
                        "command_result": None,
                        "validation_step_count": len(validation_steps),
                    }
                else:
                    gate_result = gate_evaluator.evaluate(gate)
                state["step_results"][step.step_id].setdefault("gate_results", []).append(
                    gate_result
                )
                if not gate_result["passed"]:
                    blocker = BlockerEvent(
                        blocker_id=f"{runbook.runbook_id}-{step.step_id}-{gate_id}",
                        blocker_type="gate",
                        severity="high",
                        message=f"Gate failed: {gate_id}",
                        step_id=step.step_id,
                        gate_id=gate_id,
                        context=gate_result,
                    )
                    state["step_results"][step.step_id]["status"] = "failed"
                    self._save_state(state)
                    return self._block_and_decide(state, blocker)

            state["step_results"][step.step_id]["status"] = "passed"
            state["step_results"][step.step_id]["finished_at"] = now_utc_iso()
            self._save_state(state)

        state["status"] = "passed"
        state["finished_at"] = now_utc_iso()
        self._save_state(state)

        result = {
            "runbook_id": runbook.runbook_id,
            "status": state["status"],
            "state_file": str(self._state_path(runbook.runbook_id)),
            "result_file": str(self._result_path(runbook.runbook_id)),
            "step_count": len(runbook.steps),
            "steps_passed": sum(
                1 for item in state["step_results"].values() if item.get("status") == "passed"
            ),
        }
        dump_json(self._result_path(runbook.runbook_id), result)

        write_audit_record(
            base_dir=self.runs_dir,
            record_type="execution",
            payload={
                "runbook_id": runbook.runbook_id,
                "status": state["status"],
                "state_file": result["state_file"],
                "result_file": result["result_file"],
            },
        )
        return result
