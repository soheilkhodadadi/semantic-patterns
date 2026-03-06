from __future__ import annotations

import json
from pathlib import Path

import yaml

from semantic_ai_washing.director.cli import main


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_cli_init_and_status(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    exit_code = main_with_args(["init"])
    assert exit_code == 0

    status_code = main_with_args(["status"])
    assert status_code == 0


def test_cli_ingest_and_plan(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    main_with_args(["init"])

    protocol = tmp_path / "protocol.md"
    roadmap = tmp_path / "roadmap.md"
    iteration_log = tmp_path / "docs" / "iteration_log.md"
    _write(protocol, "Protocol text")
    _write(roadmap, "Roadmap text")
    _write(iteration_log, "## Iteration 1\n### Phase: p1 (start)")

    ingest_code = main_with_args(
        [
            "ingest",
            "--protocol",
            str(protocol),
            "--roadmap",
            str(roadmap),
            "--iteration-log",
            str(iteration_log),
        ]
    )
    assert ingest_code == 0

    profile_path = tmp_path / "director" / "config" / "project_profile.yaml"
    profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    profile["phase_command_map"]["iteration1/p1"] = ["echo p1"]
    profile_path.write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")

    plan_code = main_with_args(["plan", "--iteration", "1", "--phase", "p1"])
    assert plan_code == 0

    plans = list((tmp_path / "director" / "plans").glob("runbook_*.yaml"))
    assert plans


def test_cli_ingest_with_roadmap_model_and_optimize(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    main_with_args(["init"])

    protocol = tmp_path / "protocol.md"
    model = tmp_path / "director" / "model" / "roadmap_model.yaml"
    iteration_log = tmp_path / "docs" / "iteration_log.md"
    dataset = tmp_path / "data" / "recovery.csv"

    _write(protocol, "Protocol text")
    _write(
        model,
        """
schema_version: "1.1.0"
project:
  name: semantic-patterns
  description: test
settings:
  active_horizon_iterations: ["1"]
  optimizer_weights:
    unblock_value: 5
    critical_path_depth: 4
    risk_reduction: 3
    automation_bonus: 2
    manual_effort_penalty: 2
    precondition_gap_penalty: 4
    quality_failure_penalty: 5
  defaults:
    phase_execution_mode: phase_first
    proposal_only: true
    allow_cross_iteration_rewrite: true
    fragment_rate_threshold: 0.15
branching_policy:
  schema_version: "1.0.0"
  integration_branch_template: "iteration{iteration_id}/integration"
  work_branch_template: "iteration{iteration_id}/{slug}"
  merge_target: "main"
  preferred_merge_strategy: "ff_only_if_possible_else_pr_merge_commit"
  require_review_approval_before_next_iteration: true
  require_review_approval_before_main_merge: true
  suggest_new_chat_at_iteration_boundary: true
  starter_prompt_required: true
  tag_template: "iteration{iteration_id}-closeout"
  closeout_validation_commands:
    - .venv/bin/pytest -q
policies: []
data_layers: []
source_windows: []
tooling_policies: []
iterations:
  - iteration_id: "1"
    title: test
    goal: test
    entry_criteria: []
    exit_criteria: []
    phases:
      - phase_id: iteration1/irr-validation
        title: IRR
        goal: goal
        depends_on: []
        canonical: true
        required_artifacts: []
        tasks:
          - task_id: iteration1.shared.audit_sentence_integrity
            title: Audit
            description: quality
            iteration_id: "1"
            phase_id: iteration1/irr-validation
            kind: diagnostic
            depends_on: []
            inputs: []
            outputs: []
            preconditions:
              - condition_id: audit.exists
                kind: artifact_exists
                target: data/recovery.csv
                operator: "=="
                expected: true
                on_fail: block
                message: missing
                reroute_to: []
            quality_checks:
              - condition_id: audit.fragment_rate
                kind: sentence_fragment_rate_lte
                target: data/recovery.csv
                operator: "<="
                expected: 0.15
                on_fail: reroute
                message: fragmented
                reroute_to:
                  - common.remediate_fragmented_sentences
            commands: []
            manual_handoff: false
            risks: [R1]
            estimated_effort: 2
            risk_reduction: 9
            automation_level: partial
            on_fail: reroute
            reroute_to:
              - common.remediate_fragmented_sentences
            evidence_required: true
""".strip(),
    )
    _write(
        tmp_path / "director" / "model" / "remediation_library.yaml",
        """
schema_version: "1.1.0"
tasks:
  - task_id: common.remediate_fragmented_sentences
    title: Fix fragments
    description: manual
    iteration_id: common
    phase_id: common/remediation
    kind: remediation
    depends_on: []
    inputs: []
    outputs: []
    preconditions: []
    quality_checks: []
    commands: []
    manual_handoff: true
    risks: [R5]
    estimated_effort: 5
    risk_reduction: 8
    automation_level: manual
    on_fail: block
    reroute_to: []
    evidence_required: true
""".strip(),
    )
    _write(iteration_log, "## Iteration 1\n### Phase: p1 (start)")
    _write(dataset, "sentence\nbroken fragment\nanother fragment\n")

    ingest_code = main_with_args(
        [
            "ingest",
            "--protocol",
            str(protocol),
            "--roadmap-model",
            str(model),
            "--iteration-log",
            str(iteration_log),
        ]
    )
    assert ingest_code == 0

    render_code = main_with_args(["render-roadmap"])
    assert render_code == 0

    optimize_code = main_with_args(["optimize", "--iteration", "1", "--phase", "irr-validation"])
    assert optimize_code == 0

    recommendations = list((tmp_path / "director" / "optimization").glob("recommendation_*.json"))
    assert recommendations


def test_cli_decide_from_blocker(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    main_with_args(["init"])

    blocker = {
        "schema_version": "1.0.0",
        "blocker_id": "btest",
        "blocker_type": "env",
        "severity": "high",
        "message": "doctor failed",
        "context": {},
    }
    blocker_file = tmp_path / "blocker.json"
    blocker_file.write_text(json.dumps(blocker), encoding="utf-8")

    code = main_with_args(["decide", "--blocker-file", str(blocker_file)])
    assert code == 0

    decisions = list((tmp_path / "director" / "decisions").glob("decision_*.json"))
    assert decisions


def test_cli_decide_from_execution_state(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    main_with_args(["init"])

    state = {
        "runbook_id": "rb1",
        "status": "blocked",
        "blocker": {
            "schema_version": "1.0.0",
            "blocker_id": "b-state",
            "blocker_type": "runtime",
            "severity": "high",
            "message": "failed command",
            "context": {},
        },
    }
    state_file = tmp_path / "execution_state.json"
    state_file.write_text(json.dumps(state), encoding="utf-8")

    code = main_with_args(["decide", "--execution-state", str(state_file)])
    assert code == 0


def test_cli_decide_rejects_decision_payload(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    main_with_args(["init"])

    decision_payload = {
        "schema_version": "1.0.0",
        "decision_id": "d1",
        "blocker_event_id": "b1",
        "status": "needs_selection",
        "rationale": "placeholder",
        "options": [],
        "context": {},
    }
    payload_file = tmp_path / "decision_like.json"
    payload_file.write_text(json.dumps(decision_payload), encoding="utf-8")

    code = main_with_args(["decide", "--blocker-file", str(payload_file)])
    assert code == 2


def test_cli_defer_writes_deferred_record_and_updates_state(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    main_with_args(["init"])

    runs_dir = tmp_path / "director" / "runs"
    decisions_dir = tmp_path / "director" / "decisions"
    decision_file = decisions_dir / "decision_fake.json"
    decision_file.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "decision_id": "dec123",
                "blocker_event_id": "block123",
                "status": "needs_selection",
                "rationale": "test",
                "options": [],
                "context": {},
            }
        ),
        encoding="utf-8",
    )

    state_file = runs_dir / "execution_state_rb1.json"
    state_file.write_text(
        json.dumps(
            {
                "runbook_id": "rb1",
                "status": "blocked",
                "decision_file": str(decision_file.resolve()),
                "step_results": {},
            }
        ),
        encoding="utf-8",
    )

    code = main_with_args(
        [
            "defer",
            "--decision-file",
            str(decision_file),
            "--until-iteration",
            "2",
            "--until-phase",
            "full-sample-classification",
            "--criteria",
            "increase training pool",
        ]
    )
    assert code == 0

    deferred = list(decisions_dir.glob("deferred_*.json"))
    assert deferred
    updated_state = json.loads(state_file.read_text(encoding="utf-8"))
    assert updated_state["status"] == "deferred_blocked"


def main_with_args(args: list[str]) -> int:
    import sys

    previous = sys.argv
    try:
        sys.argv = ["director"] + args
        return int(main())
    finally:
        sys.argv = previous
