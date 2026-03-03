from __future__ import annotations

import json
from pathlib import Path

import yaml

from semantic_ai_washing.director.adapters.iteration_log import parse_iteration_log
from semantic_ai_washing.director.core.config import (
    ensure_default_configs,
    get_director_paths,
    load_configs,
)
from semantic_ai_washing.director.core.cost import CostController
from semantic_ai_washing.director.core.decision import DecisionEngine
from semantic_ai_washing.director.core.executor import RunbookExecutor
from semantic_ai_washing.director.core.planner import PlannerEngine
from semantic_ai_washing.director.core.security import redact_secrets
from semantic_ai_washing.director.core.snapshot import SnapshotIngestor
from semantic_ai_washing.director.core.state import StateCompiler
from semantic_ai_washing.director.schemas import BlockerEvent, CostUsageRecord


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_snapshot_parser_handles_missing_and_conflicting_phase_entries(tmp_path):
    log_path = tmp_path / "iteration_log.md"
    _write(
        log_path,
        """
## Iteration 1 (In Progress)
### Phase: alpha (start)
- Date: 2026-03-01
- Status: pending
### Phase: alpha (completed)
- Date: 2026-03-02
- Status: done
""".strip(),
    )

    parsed = parse_iteration_log(str(log_path))
    assert parsed["iteration_count"] == 1
    assert len(parsed["phases"]) == 2
    assert parsed["phases"][0]["name"] == "alpha"
    assert parsed["phases"][1]["status_label"] == "completed"


def test_state_compiler_infers_active_iteration_and_last_gate(tmp_path):
    iteration_state = tmp_path / "iteration_state.json"
    iteration_state.write_text(
        json.dumps(
            {
                "iterations": [{"iteration_id": "1"}, {"iteration_id": "2"}],
                "last_successful_gate": "unknown",
            }
        ),
        encoding="utf-8",
    )

    report_dir = tmp_path / "reports" / "iteration1" / "phase1"
    report_dir.mkdir(parents=True)
    (report_dir / "qa_report.json").write_text(
        json.dumps({"summary": {"status": "pass"}}), encoding="utf-8"
    )

    compiler = StateCompiler(repo_root=str(tmp_path))
    compiled = compiler.compile(str(iteration_state), output_path=str(tmp_path / "compiled.json"))

    assert compiled["active_iteration"] == "2"
    assert str(compiled["last_gate_status"]).startswith("pass:")
    assert (tmp_path / "compiled.json").exists()


def test_runbook_generator_outputs_valid_yaml(tmp_path):
    paths = get_director_paths(str(tmp_path))
    ensure_default_configs(paths)

    # Seed minimal snapshots.
    _write(paths.snapshots_dir / "protocol_summary.json", json.dumps({"source_sha256": "a"}))
    _write(paths.snapshots_dir / "roadmap_summary.json", json.dumps({"source_sha256": "b"}))
    _write(
        paths.snapshots_dir / "iteration_state.json",
        json.dumps({"source_sha256": "c", "last_successful_gate": "unknown"}),
    )

    config = load_configs(paths)
    planner = PlannerEngine(
        repo_root=str(tmp_path),
        config=config,
        snapshots_dir=str(paths.snapshots_dir),
        plans_dir=str(paths.plans_dir),
        decisions_dir=str(paths.decisions_dir),
        runs_dir=str(paths.runs_dir),
        cache_dir=str(paths.cache_dir),
    )
    result = planner.generate(iteration_id="1", phase_name="phase-x")

    runbook_payload = yaml.safe_load(Path(result["runbook_file"]).read_text(encoding="utf-8"))
    assert runbook_payload["runbook_id"] == result["runbook_id"]
    assert runbook_payload["phase_name"] == "phase-x"
    assert isinstance(runbook_payload["steps"], list)


def test_blocker_engine_ranks_options_deterministically(tmp_path):
    engine = DecisionEngine(decisions_dir=tmp_path)
    blocker = BlockerEvent(
        blocker_id="b1",
        blocker_type="runtime",
        message="command failed",
    )

    first = engine.options_for(blocker)
    second = engine.options_for(blocker)
    assert [opt.option_id for opt in first] == [opt.option_id for opt in second]
    assert first[0].score >= first[-1].score


def test_executor_resumes_from_checkpoint(tmp_path):
    runbook_path = tmp_path / "runbook.yaml"
    runbook_payload = {
        "schema_version": "1.0.0",
        "runbook_id": "rb123",
        "title": "resume test",
        "summary": "test",
        "iteration_id": "1",
        "phase_name": "resume",
        "autonomy_mode": "autonomous",
        "dependencies": [],
        "gates": [],
        "risks": [],
        "steps": [
            {
                "schema_version": "1.0.0",
                "step_id": "step-001",
                "title": "first",
                "description": "first",
                "command": "python -c 'print(\"ok\")'",
                "cwd": ".",
                "timeout_seconds": 60,
                "retry_limit": 0,
                "required_outputs": [],
                "gate_ids": [],
                "escalation_required": False,
                "status": "pending",
            },
            {
                "schema_version": "1.0.0",
                "step_id": "step-002",
                "title": "second",
                "description": "second",
                "command": "python -c 'print(\"ok2\")'",
                "cwd": ".",
                "timeout_seconds": 60,
                "retry_limit": 0,
                "required_outputs": [],
                "gate_ids": [],
                "escalation_required": False,
                "status": "pending",
            },
        ],
        "context": {},
        "provenance": {},
        "llm_refined": False,
    }
    runbook_path.write_text(yaml.safe_dump(runbook_payload, sort_keys=False), encoding="utf-8")

    executor = RunbookExecutor(
        repo_root=str(tmp_path),
        runs_dir=str(tmp_path / "runs"),
        decisions_dir=str(tmp_path / "decisions"),
        autonomy_policy={"require_explicit_recovery_selection": True},
    )

    # Simulate partially completed run state.
    state_path = tmp_path / "runs" / "execution_state_rb123.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "runbook_id": "rb123",
                "step_results": {"step-001": {"status": "passed"}},
                "status": "running",
            }
        ),
        encoding="utf-8",
    )

    result = executor.run(str(runbook_path), resume=True)
    assert result["status"] == "passed"


def test_cost_limiter_blocks_additional_usage(tmp_path):
    usage = tmp_path / "cost_usage.jsonl"
    controller = CostController(
        policy={"max_tokens_per_run": 10, "max_cost_usd_per_run": 1.0},
        usage_file=usage,
        cache_dir=tmp_path / "cache",
    )

    controller.record_usage(
        CostUsageRecord(
            usage_id="u1",
            component="test",
            prompt_tokens=6,
            completion_tokens=3,
            total_tokens=9,
            estimated_cost_usd=0.2,
        )
    )
    ok, _ = controller.can_spend(add_tokens=3, add_cost_usd=0.1)
    assert not ok


def test_redaction_removes_secret_patterns():
    key = "sk-proj-" + "ABC123_DEF456_GHI789_JKL012MNOP345QRST"
    text = f"OPENAI key {key} is here"
    redacted = redact_secrets(text)
    assert "sk-proj" not in redacted
    assert "[REDACTED_SECRET]" in redacted


def test_end_to_end_ingest_plan_run_with_blocker_escalation(tmp_path):
    protocol = tmp_path / "protocol.md"
    roadmap = tmp_path / "roadmap.md"
    iteration_log = tmp_path / "iteration_log.md"

    _write(protocol, "Diagnostics -> Planning -> Execution")
    _write(roadmap, "Iteration 1: label expansion")
    _write(
        iteration_log,
        """
## Iteration 1 (In Progress)
### Phase: label-expansion (start)
- Validation run: pending
""".strip(),
    )

    paths = get_director_paths(str(tmp_path))
    ensure_default_configs(paths)

    ingestor = SnapshotIngestor(paths.snapshots_dir)
    ingestor.ingest(
        protocol_path=str(protocol),
        roadmap_path=str(roadmap),
        iteration_log_path=str(iteration_log),
        enable_atlas=False,
    )

    config = load_configs(paths)
    planner = PlannerEngine(
        repo_root=str(tmp_path),
        config=config,
        snapshots_dir=str(paths.snapshots_dir),
        plans_dir=str(paths.plans_dir),
        decisions_dir=str(paths.decisions_dir),
        runs_dir=str(paths.runs_dir),
        cache_dir=str(paths.cache_dir),
    )
    result = planner.generate(iteration_id="1", phase_name="label-expansion")

    # Force step failure to trigger blocker escalation.
    runbook_payload = yaml.safe_load(Path(result["runbook_file"]).read_text(encoding="utf-8"))
    runbook_payload["steps"][0]["command"] = "python -c 'import sys; sys.exit(1)'"
    Path(result["runbook_file"]).write_text(
        yaml.safe_dump(runbook_payload, sort_keys=False),
        encoding="utf-8",
    )

    executor = RunbookExecutor(
        repo_root=str(tmp_path),
        runs_dir=str(paths.runs_dir),
        decisions_dir=str(paths.decisions_dir),
        autonomy_policy={"require_explicit_recovery_selection": True},
    )
    run_result = executor.run(result["runbook_file"], mode="autonomous", resume=False)
    assert run_result["status"] == "blocked"

    state_file = Path(run_result["state_file"])
    payload = json.loads(state_file.read_text(encoding="utf-8"))
    assert payload["decision_file"]
    assert Path(payload["decision_file"]).exists()
