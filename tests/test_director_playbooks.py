from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from semantic_director.cli import main
from semantic_director.playbooks import (
    list_playbooks,
    recommend_playbooks,
    show_playbook,
)
from semantic_ai_washing.director.schemas import ReviewFinding


REPO_ROOT = Path(__file__).resolve().parents[1]


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2))


def _run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)


def _init_git_repo(tmp_path: Path) -> None:
    _run(["git", "init", "-b", "main"], tmp_path)
    _run(["git", "config", "user.email", "codex@example.com"], tmp_path)
    _run(["git", "config", "user.name", "Codex"], tmp_path)
    _write(tmp_path / "README.md", "temp repo\n")
    _run(["git", "add", "README.md"], tmp_path)
    _run(["git", "commit", "-m", "init"], tmp_path)


def _minimal_model() -> dict:
    return {
        "schema_version": "1.4.0",
        "project": {"name": "semantic-patterns", "description": "test"},
        "settings": {
            "active_horizon_iterations": ["1"],
            "optimizer_weights": {
                "unblock_value": 5,
                "critical_path_depth": 4,
                "risk_reduction": 3,
                "automation_bonus": 2,
                "manual_effort_penalty": 2,
                "precondition_gap_penalty": 4,
                "quality_failure_penalty": 5,
            },
            "defaults": {
                "phase_execution_mode": "phase_first",
                "proposal_only": True,
                "allow_cross_iteration_rewrite": True,
                "fragment_rate_threshold": 0.15,
                "active_source_window_id": "active_2021_2024",
                "canonical_table_format": "parquet",
            },
        },
        "branching_policy": {
            "schema_version": "1.0.0",
            "integration_branch_template": "codex/iteration{iteration_id}/integration",
            "work_branch_template": "codex/iteration{iteration_id}/{slug}",
            "merge_target": "main",
            "preferred_merge_strategy": "ff_only_if_possible_else_pr_merge_commit",
            "require_review_approval_before_next_iteration": True,
            "require_review_approval_before_main_merge": True,
            "suggest_new_chat_at_iteration_boundary": True,
            "starter_prompt_required": True,
            "tag_template": "iteration{iteration_id}-closeout",
            "closeout_validation_commands": [".venv/bin/pytest -q"],
        },
        "stakeholder_alignment": {
            "schema_version": "1.4.0",
            "source_artifact": "docs/director/stakeholder_expectations.md",
            "active_development_scope": "2021-2024",
            "publication_target_scope": "all publicly traded firms",
            "desired_horizon": "20-year horizon",
            "methodology_hard_gates": [],
            "data_hard_gates": [],
            "publication_hard_gates": [],
            "requirements": [],
        },
        "methodology_alignment": {
            "schema_version": "1.4.0",
            "source_artifact": "docs/director/proposal_methodology.md",
            "core_construct": "test",
            "active_development_scope": "2021-2024",
            "publication_target_scope": "all publicly traded firms",
            "desired_horizon": "2000-2024",
            "core_constructs": [],
            "label_semantics": {},
            "borderline_rules": [],
            "irr_design_requirements": [],
            "named_measures": [],
            "baseline_predictive_specs": [],
            "ai_washing_specification": [],
            "rubric_calibration_policy": [],
            "rubric_freeze_policy": [],
            "predictive_validity_policy": [],
            "hard_gates": [],
            "requirements": [],
        },
        "policies": [],
        "data_layers": [],
        "source_windows": [],
        "tooling_policies": [],
        "iterations": [
            {
                "iteration_id": "1",
                "title": "Iteration 1",
                "goal": "test",
                "entry_criteria": [],
                "exit_criteria": [],
                "phases": [
                    {
                        "phase_id": "iteration1/label-ops-bootstrap",
                        "title": "Label ops",
                        "goal": "prepare labels",
                        "depends_on": [],
                        "canonical": True,
                        "required_artifacts": [],
                        "tasks": [],
                    },
                    {
                        "phase_id": "iteration1/review-and-replan",
                        "title": "Review and replan",
                        "goal": "close out iteration",
                        "depends_on": ["iteration1/label-ops-bootstrap"],
                        "canonical": True,
                        "required_artifacts": [],
                        "tasks": [],
                    },
                ],
            }
        ],
    }


def _copy_playbooks(tmp_path: Path) -> None:
    shutil.copytree(
        REPO_ROOT / "director" / "playbooks",
        tmp_path / "director" / "playbooks",
        dirs_exist_ok=True,
    )


def main_with_args(args: list[str]) -> int:
    previous = sys.argv[:]
    try:
        sys.argv = ["director", *args]
        return main()
    finally:
        sys.argv = previous


def test_playbook_loader_and_show():
    playbooks = list_playbooks(REPO_ROOT)
    ids = [item["playbook_id"] for item in playbooks]
    assert ids == ["extraction_micro_cleanup", "prompt_boundary_benchmark"]

    details = show_playbook(REPO_ROOT, "prompt_boundary_benchmark")
    assert details["spec"]["playbook_id"] == "prompt_boundary_benchmark"
    assert "reviewed slice" in details["procedure_markdown"]


def test_recommend_playbooks_deterministic():
    findings = [
        ReviewFinding(
            scope="iteration",
            finding_id="boundary",
            category="gate_weakness",
            summary="Overall accuracy is acceptable but actionable speculative boundary accuracy is weak on a fixed slice.",
            recommended_action="Run a prompt benchmark on the subgroup boundary before scaling.",
            evidence_refs=["reports/labels/tranche1_prompt_benchmark_v2_4.md"],
        ),
        ReviewFinding(
            scope="phase",
            finding_id="noise",
            category="data_quality",
            summary="Table of Contents header fragment and unmatched noisy extraction rows remain in the slice.",
            recommended_action="Run a micro cleanup on 5-10 noisy extraction rows.",
            evidence_refs=["reports/labels/tranche1_reextraction_v2_2_summary.json"],
        ),
    ]
    recommendations = recommend_playbooks(findings, REPO_ROOT)
    assert [item.playbook_id for item in recommendations] == [
        "prompt_boundary_benchmark",
        "extraction_micro_cleanup",
    ]
    assert recommendations[0].match_score >= recommendations[1].match_score


def test_review_and_status_surface_recommended_playbooks(tmp_path, monkeypatch, capsys):
    _init_git_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert main_with_args(["init"]) == 0
    capsys.readouterr()

    _copy_playbooks(tmp_path)
    _write_yaml(tmp_path / "director" / "model" / "roadmap_model.yaml", _minimal_model())
    _write(tmp_path / "docs" / "iteration_log.md", "# Iteration Log\n")
    _write(tmp_path / "docs" / "director" / "stakeholder_expectations.md", "stub\n")
    _write(tmp_path / "docs" / "director" / "proposal_methodology.md", "stub\n")

    _write_yaml(
        tmp_path / "director" / "plans" / "runbook_rb1.yaml",
        {
            "runbook_id": "rb1",
            "iteration_id": "1",
            "phase_name": "label-ops-bootstrap",
        },
    )
    _write_json(
        tmp_path / "director" / "runs" / "execution_state_rb1.json",
        {
            "runbook_id": "rb1",
            "status": "blocked",
            "updated_at": "2026-03-11T12:00:00+00:00",
            "git": {"commit": "abc123"},
            "step_results": {},
        },
    )
    _write_json(
        tmp_path / "director" / "runs" / "execution_result_rb1.json",
        {"runbook_id": "rb1", "status": "blocked"},
    )

    from semantic_ai_washing.director.core import review as review_module

    def fake_quality_summary(self, iteration_id, phase_summary):
        finding = ReviewFinding(
            scope="iteration",
            finding_id="boundary",
            category="gate_weakness",
            summary="Overall accuracy is acceptable but actionable speculative boundary accuracy is weak on a fixed slice.",
            recommended_action="Run a prompt benchmark on the subgroup boundary before scaling.",
            evidence_refs=["reports/labels/tranche1_prompt_benchmark_v2_4.md"],
        )
        return {"reports": {}}, [finding]

    monkeypatch.setattr(review_module.ReviewEngine, "_quality_summary", fake_quality_summary)

    monkeypatch.setattr("sys.argv", ["director", "review", "--iteration", "1"])
    assert main() == 0
    review_path = tmp_path / "director" / "reviews" / "iteration_1_review.json"
    review_payload = json.loads(review_path.read_text(encoding="utf-8"))
    assert review_payload["recommended_playbooks"][0]["playbook_id"] == "prompt_boundary_benchmark"
    capsys.readouterr()

    monkeypatch.setattr("sys.argv", ["director", "status"])
    assert main() == 0
    status_payload = json.loads(capsys.readouterr().out)
    assert (
        status_payload["latest_recommended_playbooks"][0]["playbook_id"]
        == "prompt_boundary_benchmark"
    )


def test_cli_playbooks_list_and_show(tmp_path, monkeypatch, capsys):
    _init_git_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert main_with_args(["init"]) == 0
    capsys.readouterr()
    _copy_playbooks(tmp_path)

    monkeypatch.setattr("sys.argv", ["director", "playbooks", "--list"])
    assert main() == 0
    list_payload = json.loads(capsys.readouterr().out)
    assert {item["playbook_id"] for item in list_payload["playbooks"]} == {
        "prompt_boundary_benchmark",
        "extraction_micro_cleanup",
    }

    monkeypatch.setattr(
        "sys.argv", ["director", "playbooks", "--show", "prompt_boundary_benchmark"]
    )
    assert main() == 0
    show_payload = json.loads(capsys.readouterr().out)
    assert show_payload["spec"]["playbook_id"] == "prompt_boundary_benchmark"
    assert "reviewed slice" in show_payload["procedure_markdown"]
