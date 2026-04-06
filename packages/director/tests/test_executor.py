from __future__ import annotations

import json

import yaml

from semantic_director.executor import RunbookExecutor


def test_executor_resumes_from_checkpoint(tmp_path) -> None:
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


def test_executor_manual_handoff_blocks_when_output_missing(tmp_path) -> None:
    runbook_path = tmp_path / "runbook.yaml"
    runbook_payload = {
        "schema_version": "1.0.0",
        "runbook_id": "rbmanual",
        "title": "manual test",
        "summary": "test",
        "iteration_id": "1",
        "phase_name": "manual-phase",
        "autonomy_mode": "autonomous",
        "dependencies": [],
        "gates": [],
        "risks": [],
        "steps": [
            {
                "schema_version": "1.0.0",
                "step_id": "step-001",
                "title": "Manual handoff: labeling",
                "description": "await artifact",
                "command": None,
                "cwd": ".",
                "timeout_seconds": 60,
                "retry_limit": 0,
                "required_outputs": ["data/manual.csv"],
                "conditions": [],
                "gate_ids": [],
                "escalation_required": False,
                "manual_handoff": True,
                "task_id": "t.manual",
                "status": "pending",
            }
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
    result = executor.run(str(runbook_path))
    state = json.loads((tmp_path / "runs" / "execution_state_rbmanual.json").read_text())

    assert result["status"] == "blocked"
    assert state["blocker"]["blocker_type"] == "manual"
    assert state["step_results"]["step-001"]["status"] == "waiting_manual"
