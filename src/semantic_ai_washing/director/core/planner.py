"""Deterministic planning and runbook compilation."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

from semantic_ai_washing.director.core.audit import default_provenance, write_audit_record
from semantic_ai_washing.director.core.cost import CostController
from semantic_ai_washing.director.core.llm import refine_plan_markdown
from semantic_ai_washing.director.core.utils import (
    dump_json,
    ensure_dir,
    load_json,
    now_utc_iso,
    sha256_text,
)
from semantic_ai_washing.director.policies import DEFAULT_RISK_REGISTER
from semantic_ai_washing.director.schemas import (
    DecisionRecord,
    ExecutionStep,
    PhaseGate,
    RiskRegisterEntry,
    Runbook,
)


class PlannerEngine:
    def __init__(
        self,
        repo_root: str,
        config: dict[str, Any],
        snapshots_dir: str,
        plans_dir: str,
        decisions_dir: str,
        runs_dir: str,
        cache_dir: str,
    ):
        self.repo_root = repo_root
        self.config = config
        self.snapshots_dir = Path(snapshots_dir)
        self.plans_dir = ensure_dir(plans_dir)
        self.decisions_dir = ensure_dir(decisions_dir)
        self.runs_dir = ensure_dir(runs_dir)
        self.cache_dir = ensure_dir(cache_dir)

    def _load_snapshots(self) -> dict[str, Any]:
        protocol = load_json(self.snapshots_dir / "protocol_summary.json", default={}) or {}
        roadmap = load_json(self.snapshots_dir / "roadmap_summary.json", default={}) or {}
        iteration = load_json(self.snapshots_dir / "iteration_state.json", default={}) or {}
        return {"protocol": protocol, "roadmap": roadmap, "iteration": iteration}

    def _build_risk_entries(self, phase_name: str) -> list[RiskRegisterEntry]:
        profile = self.config.get("project_profile", {})
        profile_risks = profile.get("risk_register", [])
        source = profile_risks if profile_risks else DEFAULT_RISK_REGISTER
        entries = []
        for raw in source:
            entries.append(
                RiskRegisterEntry(
                    code=raw["code"],
                    title=raw["title"],
                    signal=raw["signal"],
                    mitigation=raw["mitigation"],
                    backout=raw["backout"],
                    severity=int(raw.get("severity", 3)),
                    phase_scope=raw.get("phase_scope", [phase_name]),
                )
            )
        return entries

    def _build_gates(self, iteration_id: str, phase_name: str) -> list[PhaseGate]:
        profile = self.config.get("project_profile", {})
        artifact_map = profile.get("phase_artifact_map", {})
        phase_key = f"iteration{iteration_id}/{phase_name}"
        required_outputs = [str(path) for path in artifact_map.get(phase_key, [])]
        return [
            PhaseGate(
                gate_id=f"{phase_name}-gate-001",
                name="Validation Commands",
                description="Canonical validation commands complete successfully",
                pass_condition="All validation commands exit with code 0",
            ),
            PhaseGate(
                gate_id=f"{phase_name}-gate-002",
                name="Artifacts Present",
                description="Required outputs are generated for the phase",
                pass_condition="All required output files exist",
                required_outputs=required_outputs,
            ),
            PhaseGate(
                gate_id=f"{phase_name}-gate-003",
                name="Iteration Log Updated",
                description="Execution evidence is recorded in docs/iteration_log.md",
                pass_condition="iteration_log contains phase entry and evidence",
                required_outputs=["docs/iteration_log.md"],
            ),
        ]

    def _phase_commands(
        self, iteration_id: str, phase_name: str, snapshots: dict[str, Any]
    ) -> list[str]:
        profile = self.config.get("project_profile", {})
        mapping = profile.get("phase_command_map", {})
        key = f"iteration{iteration_id}/{phase_name}"
        if key in mapping:
            return [str(item) for item in mapping[key]]

        roadmap_iterations = snapshots.get("roadmap", {}).get("iterations", [])
        for item in roadmap_iterations:
            if str(item.get("iteration_id", "")) != str(iteration_id):
                continue
            for phase in item.get("phases", []):
                if str(phase.get("name", "")).strip().lower() != phase_name.lower():
                    continue
                commands = phase.get("commands", [])
                if commands:
                    return [str(command) for command in commands]

        roadmap_model = profile.get("roadmap_model", {})
        for item in roadmap_model.get("iterations", []):
            if str(item.get("iteration_id", "")) != str(iteration_id):
                continue
            for phase in item.get("phases", []):
                if str(phase.get("name", "")).strip().lower() != phase_name.lower():
                    continue
                commands = phase.get("commands", [])
                if commands:
                    return [str(command) for command in commands]

        return []

    def _build_steps(
        self, iteration_id: str, phase_name: str, snapshots: dict[str, Any]
    ) -> list[ExecutionStep]:
        profile = self.config.get("project_profile", {})
        timeout_overrides = profile.get("step_timeout_overrides", {})
        snapshot_timeout = int(timeout_overrides.get("snapshot_seconds", 1800))
        validation_timeout = int(timeout_overrides.get("validation_seconds", 1800))
        phase_timeout = int(timeout_overrides.get("phase_seconds", 1800))
        validation_commands = [
            str(item) for item in profile.get("canonical_validation_commands", [])
        ]
        commands = self._phase_commands(iteration_id, phase_name, snapshots)
        steps: list[ExecutionStep] = []

        # Add a deterministic snapshot sanity step first.
        steps.append(
            ExecutionStep(
                step_id="step-001",
                title="Validate snapshots",
                description="Ensure protocol/roadmap/iteration snapshots are available",
                command=f"{sys.executable} -m semantic_ai_washing.director.cli status",
                timeout_seconds=snapshot_timeout,
                required_outputs=[
                    "director/snapshots/protocol_summary.json",
                    "director/snapshots/roadmap_summary.json",
                    "director/snapshots/iteration_state.json",
                ],
                escalation_required=True,
            )
        )

        step_counter = 2
        for idx, command in enumerate(validation_commands, start=1):
            step_id = f"step-{step_counter:03d}"
            step_counter += 1
            steps.append(
                ExecutionStep(
                    step_id=step_id,
                    title=f"Validation command {idx}",
                    description=f"Execute canonical validation: {command}",
                    command=command,
                    timeout_seconds=validation_timeout,
                    escalation_required=True,
                )
            )

        for idx, command in enumerate(commands, start=1):
            step_id = f"step-{step_counter:03d}"
            step_counter += 1
            steps.append(
                ExecutionStep(
                    step_id=step_id,
                    title=f"Phase command {idx}",
                    description=f"Execute: {command}",
                    command=command,
                    timeout_seconds=phase_timeout,
                    escalation_required=False,
                )
            )

        steps.append(
            ExecutionStep(
                step_id=f"step-{step_counter:03d}",
                title="Produce planning artifacts",
                description="Persist runbook + plan markdown + decision scaffold",
                command=None,
                required_outputs=[],
                gate_ids=[
                    f"{phase_name}-gate-001",
                    f"{phase_name}-gate-002",
                    f"{phase_name}-gate-003",
                ],
            )
        )
        return steps

    def _runbook_id(self, iteration_id: str, phase_name: str) -> str:
        return sha256_text(f"{iteration_id}:{phase_name}:{now_utc_iso()}")[:16]

    def _render_plan_markdown(self, runbook: Runbook, snapshots: dict[str, Any]) -> str:
        lines = [
            f"# Director Plan: Iteration {runbook.iteration_id} / {runbook.phase_name}",
            "",
            "## Summary",
            runbook.summary,
            "",
            "## Gates",
        ]
        for gate in runbook.gates:
            lines.append(f"- `{gate.gate_id}`: {gate.name} -> {gate.pass_condition}")

        lines.extend(["", "## Risks"])
        for risk in runbook.risks:
            lines.append(f"- `{risk.code}` {risk.title}: {risk.mitigation}")

        lines.extend(["", "## Steps"])
        for step in runbook.steps:
            cmd = step.command or "(no-op artifact step)"
            lines.append(f"- `{step.step_id}` {step.title}: `{cmd}`")

        lines.extend(
            [
                "",
                "## Snapshot Provenance",
                f"- protocol hash: `{snapshots['protocol'].get('source_sha256', 'unknown')}`",
                f"- roadmap hash: `{snapshots['roadmap'].get('source_sha256', 'unknown')}`",
                f"- iteration snapshot hash: `{snapshots['iteration'].get('source_sha256', 'unknown')}`",
            ]
        )
        return "\n".join(lines).strip() + "\n"

    def generate(self, iteration_id: str, phase_name: str) -> dict[str, Any]:
        snapshots = self._load_snapshots()
        runbook_id = self._runbook_id(iteration_id, phase_name)
        title = f"Iteration {iteration_id} / {phase_name}"
        summary = (
            "Autonomous runbook compiled from repo-canonical snapshots with explicit gates, "
            "risk controls, and blocker escalation."
        )

        runbook = Runbook(
            runbook_id=runbook_id,
            title=title,
            summary=summary,
            iteration_id=str(iteration_id),
            phase_name=phase_name,
            autonomy_mode=self.config.get("autonomy_policy", {}).get("mode", "autonomous"),
            dependencies=["repo snapshots", "iteration log", "validation command chain"],
            gates=self._build_gates(iteration_id, phase_name),
            risks=self._build_risk_entries(phase_name),
            steps=self._build_steps(iteration_id, phase_name, snapshots),
            context={
                "active_branch": snapshots.get("iteration", {})
                .get("git", {})
                .get("branch", "unknown"),
                "last_successful_gate": snapshots.get("iteration", {}).get(
                    "last_successful_gate", "unknown"
                ),
            },
            provenance=default_provenance(self.repo_root),
            llm_refined=False,
        )

        plan_markdown = self._render_plan_markdown(runbook, snapshots)

        # Optional LLM refinement under budget controls.
        usage_file = self.runs_dir / "cost_usage.jsonl"
        llm_cache_dir = self.cache_dir / "llm"
        cost_controller = CostController(
            policy=self.config.get("cost_policy", {}),
            usage_file=usage_file,
            cache_dir=llm_cache_dir,
        )
        refined_markdown, refine_meta = refine_plan_markdown(
            plan_markdown=plan_markdown,
            context_payload={
                "iteration_id": iteration_id,
                "phase_name": phase_name,
                "snapshots": {
                    "protocol_hash": snapshots["protocol"].get("source_sha256", ""),
                    "roadmap_hash": snapshots["roadmap"].get("source_sha256", ""),
                    "iteration_hash": snapshots["iteration"].get("source_sha256", ""),
                },
            },
            llm_config=self.config.get("cost_policy", {}),
            cost_controller=cost_controller,
        )
        runbook.llm_refined = bool(refine_meta.get("used_llm", False))

        runbook_file = self.plans_dir / f"runbook_{runbook_id}.yaml"
        plan_file = self.plans_dir / f"plan_{runbook_id}.md"
        decision_file = self.decisions_dir / f"decision_{runbook_id}.json"

        with runbook_file.open("w", encoding="utf-8") as f:
            yaml.safe_dump(runbook.as_deterministic_dict(), f, sort_keys=False)
        plan_file.write_text(refined_markdown, encoding="utf-8")

        decision = DecisionRecord(
            decision_id=runbook_id,
            blocker_event_id="",
            status="resolved",
            recommended_option_id=None,
            selected_option_id=None,
            rationale="No blocker yet. Placeholder decision record for runbook provenance.",
            options=[],
            context={"runbook_id": runbook_id, "llm_refine": refine_meta},
        )
        dump_json(decision_file, decision.as_deterministic_dict())

        write_audit_record(
            base_dir=self.runs_dir,
            record_type="planning",
            payload={
                "runbook_id": runbook_id,
                "iteration_id": iteration_id,
                "phase_name": phase_name,
                "runbook_file": str(runbook_file),
                "plan_file": str(plan_file),
                "decision_file": str(decision_file),
                "llm_refine": refine_meta,
            },
        )

        return {
            "runbook_id": runbook_id,
            "runbook_file": str(runbook_file),
            "plan_file": str(plan_file),
            "decision_file": str(decision_file),
            "llm_refine": refine_meta,
            "runbook": runbook.as_deterministic_dict(),
            "plan_markdown": refined_markdown,
        }

    @staticmethod
    def load_runbook(path: str) -> Runbook:
        payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        return Runbook.model_validate(payload)

    @staticmethod
    def summarize_runbook(path: str) -> dict[str, Any]:
        runbook = PlannerEngine.load_runbook(path)
        return {
            "runbook_id": runbook.runbook_id,
            "iteration_id": runbook.iteration_id,
            "phase_name": runbook.phase_name,
            "steps": len(runbook.steps),
            "gates": len(runbook.gates),
            "llm_refined": runbook.llm_refined,
        }


def runbook_to_json(path: str, output_path: str) -> str:
    runbook = PlannerEngine.load_runbook(path)
    dump_json(output_path, runbook.as_deterministic_dict())
    return output_path


def plan_output_manifest(plan_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "runbook_id": plan_result["runbook_id"],
        "generated_at": now_utc_iso(),
        "files": {
            "runbook_yaml": plan_result["runbook_file"],
            "plan_md": plan_result["plan_file"],
            "decision_json": plan_result["decision_file"],
        },
        "llm_refine": plan_result.get("llm_refine", {}),
    }


def write_plan_manifest(plan_result: dict[str, Any], out_path: str) -> str:
    manifest = plan_output_manifest(plan_result)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return out_path
