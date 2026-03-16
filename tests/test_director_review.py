from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml

from semantic_ai_washing.director.cli import main


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2))


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)


def _init_git_repo(tmp_path: Path) -> None:
    _run(["git", "init", "-b", "main"], tmp_path)
    _run(["git", "config", "user.email", "codex@example.com"], tmp_path)
    _run(["git", "config", "user.name", "Codex"], tmp_path)
    _write(tmp_path / "README.md", "test repo\n")
    _run(["git", "add", "README.md"], tmp_path)
    _run(["git", "commit", "-m", "init"], tmp_path)


def _review_model() -> dict:
    return {
        "schema_version": "1.4.0",
        "project": {"name": "semantic-patterns", "description": "test"},
        "settings": {
            "active_horizon_iterations": ["1", "2"],
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
            "desired_horizon": "20-year horizon when source availability permits",
            "methodology_hard_gates": ["IRR must be human-human and > 0.7"],
            "data_hard_gates": ["500 firms", ">=500 adjudicated labels", ">=80 per class"],
            "publication_hard_gates": ["results package required"],
            "requirements": [
                {
                    "requirement_id": "stakeholder-scale",
                    "stakeholder": "Kuntara",
                    "priority": "publication-critical",
                    "summary": "Scale beyond pilot before retraining.",
                    "target_iteration": "2",
                    "source_refs": ["email thread 2025-08-27"],
                    "mapped_phases": ["iteration2/sentence-pool-expansion-2024"],
                    "mapped_gates": ["candidate_pool_500_firms"],
                },
                {
                    "requirement_id": "stakeholder-validate-method",
                    "stakeholder": "Kuntara",
                    "priority": "non-negotiable",
                    "summary": "Validate the classification method before scaling.",
                    "target_iteration": "1",
                    "source_refs": ["email thread 2025-07-26"],
                    "mapped_phases": ["iteration1/rubric-and-api-bootstrap"],
                    "mapped_gates": ["assistive_api_smoke_passed"],
                },
            ],
        },
        "methodology_alignment": {
            "schema_version": "1.4.0",
            "source_artifact": "docs/director/proposal_methodology.md",
            "core_construct": "AI-washing is speculative AI narrative without later observable capability.",
            "active_development_scope": "2021-2024",
            "publication_target_scope": "all publicly traded firms",
            "desired_horizon": "2000-2024 when source availability permits",
            "core_constructs": [
                "Actionable vs Speculative vs Irrelevant support a predictive credibility measure."
            ],
            "label_semantics": {
                "Actionable": "current firm AI deployment",
                "Speculative": "firm-specific AI aspiration without operational evidence",
                "Irrelevant": "generic AI context or risk language",
            },
            "borderline_rules": [
                "Generic AI risk language is Irrelevant.",
                "Risk-section disclosure of present AI deployment is Actionable.",
            ],
            "irr_design_requirements": ["100+ firms", "industry-year balance", "by-class kappa"],
            "named_measures": [
                {
                    "measure_id": "A_S",
                    "formula": "log(1 + A / (1 + S))",
                    "description": "Actionable-to-speculative ratio.",
                    "mapped_phases": ["iteration3/firm-year-measure-construction"],
                }
            ],
            "baseline_predictive_specs": ["Patents and job postings for l in {0,1,2}."],
            "ai_washing_specification": ["A_S x PatentMismatch"],
            "rubric_calibration_policy": ["Rubric may change during development calibration."],
            "rubric_freeze_policy": ["Rubric must freeze before publication-scale deployment."],
            "predictive_validity_policy": [
                "Directional predictive validity is the required development gate."
            ],
            "hard_gates": ["human_human_irr_only", "irr_stratified_100_firms_min"],
            "requirements": [
                {
                    "requirement_id": "proposal-rubric-realignment",
                    "priority": "non-negotiable",
                    "summary": "Realign the rubric before tranche-1 canonical labeling continues.",
                    "target_iteration": "2",
                    "source_refs": ["proposal methodology"],
                    "mapped_phases": ["iteration2/tranche1-labeling"],
                    "mapped_gates": ["rubric_realignment_complete"],
                }
            ],
        },
        "policies": [],
        "data_layers": [],
        "source_windows": [],
        "tooling_policies": [],
        "iterations": [
            {
                "iteration_id": "1",
                "title": "Iteration 1",
                "goal": "finish foundation work",
                "entry_criteria": [],
                "exit_criteria": ["review approved"],
                "phases": [
                    {
                        "phase_id": "iteration1/rubric-and-api-bootstrap",
                        "title": "API bootstrap",
                        "goal": "bootstrap",
                        "depends_on": [],
                        "canonical": True,
                        "required_artifacts": ["reports/api/api_bootstrap_smoke_test.json"],
                        "tasks": [],
                    },
                    {
                        "phase_id": "iteration1/label-ops-bootstrap",
                        "title": "Label ops",
                        "goal": "prepare labels",
                        "depends_on": ["iteration1/rubric-and-api-bootstrap"],
                        "canonical": True,
                        "required_artifacts": [
                            "reports/data/pilot_2024_sentence_quality.json",
                            "reports/labels/labeling_batch_v1_summary.json",
                        ],
                        "tasks": [],
                    },
                    {
                        "phase_id": "iteration1/review-and-replan",
                        "title": "Review and replan",
                        "goal": "close out iteration",
                        "depends_on": ["iteration1/label-ops-bootstrap"],
                        "canonical": True,
                        "required_artifacts": [
                            "director/reviews/iteration_1_review.json",
                            "director/reviews/iteration_1_approval.json",
                        ],
                        "tasks": [],
                    },
                ],
            },
            {
                "iteration_id": "2",
                "title": "Iteration 2",
                "goal": "next iteration",
                "entry_criteria": ["iteration 1 review approved"],
                "exit_criteria": [],
                "phases": [
                    {
                        "phase_id": "iteration2/kickoff-and-preflight",
                        "title": "Kickoff",
                        "goal": "validate branch context",
                        "depends_on": ["iteration1/review-and-replan"],
                        "canonical": True,
                        "required_artifacts": ["director/reviews/iteration_2_kickoff.json"],
                        "tasks": [],
                    },
                    {
                        "phase_id": "iteration2/tranche1-labeling",
                        "title": "Tranche 1 labeling",
                        "goal": "verify the initial labeling tranche",
                        "depends_on": ["iteration2/kickoff-and-preflight"],
                        "canonical": True,
                        "required_artifacts": ["data/labels/v1/labeling_batch_v1_filled.csv"],
                        "tasks": [],
                    },
                    {
                        "phase_id": "iteration2/review-and-replan",
                        "title": "Review and replan",
                        "goal": "close out iteration",
                        "depends_on": ["iteration2/tranche1-labeling"],
                        "canonical": True,
                        "required_artifacts": ["director/reviews/iteration_2_review.json"],
                        "tasks": [],
                    },
                ],
            },
        ],
    }


def _write_run_artifacts(tmp_path: Path) -> None:
    _write_yaml(
        tmp_path / "director" / "plans" / "runbook_rb_api_blocked.yaml",
        {
            "runbook_id": "rb_api_blocked",
            "iteration_id": "1",
            "phase_name": "rubric-and-api-bootstrap",
        },
    )
    _write_json(
        tmp_path / "director" / "runs" / "execution_state_rb_api_blocked.json",
        {
            "runbook_id": "rb_api_blocked",
            "status": "blocked",
            "updated_at": "2026-03-06T01:00:00+00:00",
            "git": {"commit": "abc123"},
            "step_results": {
                "step-001": {
                    "title": "Task command: API smoke",
                    "command_result": {
                        "command": ".venv/bin/python -m semantic_ai_washing.director.tasks.api_bootstrap --mode live",
                        "started_at": "2026-03-06T01:00:00+00:00",
                        "finished_at": "2026-03-06T01:00:05+00:00",
                    },
                }
            },
            "blocker": {
                "blocker_id": "block-api-missing-key",
                "blocker_type": "runtime",
                "severity": "high",
                "message": "Step command failed: .venv/bin/python -m semantic_ai_washing.director.tasks.api_bootstrap --mode live",
            },
        },
    )
    _write_json(
        tmp_path / "director" / "runs" / "execution_result_rb_api_blocked.json",
        {"runbook_id": "rb_api_blocked", "status": "blocked"},
    )

    _write_yaml(
        tmp_path / "director" / "plans" / "runbook_rb_api_passed.yaml",
        {
            "runbook_id": "rb_api_passed",
            "iteration_id": "1",
            "phase_name": "rubric-and-api-bootstrap",
        },
    )
    _write_json(
        tmp_path / "director" / "runs" / "execution_state_rb_api_passed.json",
        {
            "runbook_id": "rb_api_passed",
            "status": "passed",
            "updated_at": "2026-03-06T02:00:00+00:00",
            "git": {"commit": "def456"},
            "step_results": {
                "step-001": {
                    "title": "Task command: API smoke",
                    "command_result": {
                        "command": ".venv/bin/python -m semantic_ai_washing.director.tasks.api_bootstrap --mode live",
                        "started_at": "2026-03-06T02:00:00+00:00",
                        "finished_at": "2026-03-06T02:00:03+00:00",
                    },
                }
            },
        },
    )
    _write_json(
        tmp_path / "director" / "runs" / "execution_result_rb_api_passed.json",
        {"runbook_id": "rb_api_passed", "status": "passed"},
    )

    _write_yaml(
        tmp_path / "director" / "plans" / "runbook_rb_labels.yaml",
        {
            "runbook_id": "rb_labels",
            "iteration_id": "1",
            "phase_name": "label-ops-bootstrap",
        },
    )
    _write_json(
        tmp_path / "director" / "runs" / "execution_state_rb_labels.json",
        {
            "runbook_id": "rb_labels",
            "status": "passed",
            "updated_at": "2026-03-06T03:00:00+00:00",
            "git": {"commit": "ghi789"},
            "step_results": {
                "step-001": {
                    "title": "Validation command 1",
                    "command_result": {
                        "command": "make doctor",
                        "started_at": "2026-03-06T03:00:00+00:00",
                        "finished_at": "2026-03-06T03:00:08+00:00",
                    },
                },
                "step-002": {
                    "title": "Task command: Build labeling batch",
                    "command_result": {
                        "command": ".venv/bin/python -m semantic_ai_washing.labeling.build_labeling_batch",
                        "started_at": "2026-03-06T03:00:10+00:00",
                        "finished_at": "2026-03-06T03:00:16+00:00",
                    },
                },
            },
        },
    )
    _write_json(
        tmp_path / "director" / "runs" / "execution_result_rb_labels.json",
        {"runbook_id": "rb_labels", "status": "passed"},
    )


def main_with_args(args: list[str]) -> int:
    import sys

    old_argv = sys.argv
    try:
        sys.argv = ["director", *args]
        return int(main())
    finally:
        sys.argv = old_argv


def test_review_approval_patch_and_kickoff_flow(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _init_git_repo(tmp_path)
    main_with_args(["init"])

    _write(tmp_path / "docs" / "iteration_log.md", "## Iteration 1\nreview pending\n")
    _write(tmp_path / "docs" / "director" / "implementation_protocol_master.md", "Protocol text\n")
    _write_yaml(tmp_path / "director" / "model" / "roadmap_model.yaml", _review_model())
    _write_json(
        tmp_path / "reports" / "data" / "pilot_2024_sentence_quality.json",
        {"fragment_rate": 0.01},
    )
    _write_json(
        tmp_path / "reports" / "labels" / "labeling_batch_v1_summary.json",
        {
            "selection": {"quarter_quotas_used": {"Q1": 37, "Q2": 68, "Q3": 68, "Q4": 67}},
            "quality": {"heldout_overlap_count": 0, "exact_duplicate_count": 0},
        },
    )
    _write_json(
        tmp_path / "reports" / "api" / "api_bootstrap_smoke_test.json",
        {"status": "passed"},
    )
    _write_run_artifacts(tmp_path)

    review_code = main_with_args(["review", "--iteration", "1"])
    assert review_code == 0
    review_path = tmp_path / "director" / "reviews" / "iteration_1_review.json"
    review_payload = json.loads(review_path.read_text(encoding="utf-8"))
    assert review_payload["review_type"] == "iteration"
    assert review_payload["blocker_summary"]["blocker_count"] == 1
    assert review_payload["roadmap_changes"]
    requirement_rows = review_payload["stakeholder_alignment_summary"]["requirement_statuses"]
    validate_method = next(
        row for row in requirement_rows if row["requirement_id"] == "stakeholder-validate-method"
    )
    scale_requirement = next(
        row for row in requirement_rows if row["requirement_id"] == "stakeholder-scale"
    )
    assert validate_method["status"] == "satisfied"
    assert scale_requirement["status"] == "open"

    phase_review_code = main_with_args(
        ["review", "--iteration", "1", "--phase", "rubric-and-api-bootstrap"]
    )
    assert phase_review_code == 0
    phase_review = json.loads(
        (
            tmp_path
            / "director"
            / "reviews"
            / "phase_iteration1_rubric-and-api-bootstrap_review.json"
        ).read_text(encoding="utf-8")
    )
    assert phase_review["review_type"] == "phase"
    assert phase_review["blocker_summary"]["blocker_count"] == 1
    assert "requirement_statuses" in phase_review["stakeholder_alignment_summary"]
    assert "requirement_statuses" in phase_review["methodology_alignment_summary"]

    _run(["git", "switch", "-c", "codex/iteration2/integration"], tmp_path)
    kickoff_blocked = main_with_args(["kickoff", "--iteration", "2"])
    assert kickoff_blocked == 2

    approve_code = main_with_args(
        [
            "approve-review",
            "--review-file",
            str(review_path),
            "--decision",
            "approve",
            "--accept-patch",
            "all",
        ]
    )
    assert approve_code == 0
    approval_path = tmp_path / "director" / "reviews" / "iteration_1_approval.json"
    approval_payload = json.loads(approval_path.read_text(encoding="utf-8"))
    assert approval_payload["next_iteration_authorized"] is True

    apply_code = main_with_args(["apply-review-patch", "--approval-file", str(approval_path)])
    assert apply_code == 0
    updated_model = yaml.safe_load(
        (tmp_path / "director" / "model" / "roadmap_model.yaml").read_text(encoding="utf-8")
    )
    iteration2 = next(
        item for item in updated_model["iterations"] if str(item["iteration_id"]) == "2"
    )
    assert any("sentence-quality gate" in item.lower() for item in iteration2["entry_criteria"])

    kickoff_ready = main_with_args(["kickoff", "--iteration", "2"])
    assert kickoff_ready == 0
    kickoff_payload = json.loads(
        (tmp_path / "director" / "reviews" / "iteration_2_kickoff.json").read_text(
            encoding="utf-8"
        )
    )
    assert kickoff_payload["status"] == "ready"

    render_code = main_with_args(["render-roadmap"])
    assert render_code == 0
    roadmap_body = (tmp_path / "docs" / "director" / "roadmap_master.md").read_text(
        encoding="utf-8"
    )
    assert "## Branching Policy" in roadmap_body
    assert "## Review Workflow" in roadmap_body
    assert "## Stakeholder Alignment" in roadmap_body
    assert "## Methodology Alignment" in roadmap_body
    assert "Approved Review Appendix" in roadmap_body

    capsys.readouterr()
    status_code = main_with_args(["status"])
    assert status_code == 0
    status_payload = json.loads(capsys.readouterr().out)
    assert status_payload["latest_review"].endswith("iteration_1_review.json")
    assert status_payload["latest_review_approval"].endswith("iteration_1_approval.json")
    assert status_payload["latest_kickoff"].endswith("iteration_2_kickoff.json")
    assert status_payload["latest_authorized_track"] == "canonical"

    refreshed_review = json.loads(review_path.read_text(encoding="utf-8"))
    assert (
        refreshed_review["methodology_alignment_summary"]["source_artifact"]
        == "docs/director/proposal_methodology.md"
    )


def test_dual_track_review_approval_blocks_canonical_kickoff(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _init_git_repo(tmp_path)
    main_with_args(["init"])

    model = _review_model()
    model["settings"]["active_horizon_iterations"] = ["1", "2", "3"]
    model["iterations"].append(
        {
            "iteration_id": "3",
            "title": "Iteration 3",
            "goal": "preliminary lane",
            "entry_criteria": ["iteration 2 review approved"],
            "exit_criteria": [],
            "phases": [
                {
                    "phase_id": "iteration3/preliminary-kickoff-and-preflight",
                    "title": "Prelim kickoff",
                    "goal": "validate preliminary lane",
                    "depends_on": ["iteration2/review-and-replan"],
                    "canonical": False,
                    "required_artifacts": [
                        "director/reviews/iteration_3_preliminary_kickoff.json"
                    ],
                    "tasks": [],
                },
                {
                    "phase_id": "iteration3/kickoff-and-preflight",
                    "title": "Canonical kickoff",
                    "goal": "validate canonical lane",
                    "depends_on": ["iteration2/review-and-replan"],
                    "canonical": True,
                    "required_artifacts": ["director/reviews/iteration_3_kickoff.json"],
                    "tasks": [],
                },
            ],
        }
    )

    _write(tmp_path / "docs" / "iteration_log.md", "## Iteration 2\nreview pending\n")
    _write(tmp_path / "docs" / "director" / "implementation_protocol_master.md", "Protocol text\n")
    _write_yaml(tmp_path / "director" / "model" / "roadmap_model.yaml", model)
    _write_json(
        tmp_path / "reports" / "models" / "preliminary_results_readiness_v1.json",
        {
            "summary": {
                "preliminary_results_authorized": True,
                "publication_grade_authorized": False,
            }
        },
    )

    review_code = main_with_args(["review", "--iteration", "2"])
    assert review_code == 0
    review_path = tmp_path / "director" / "reviews" / "iteration_2_review.json"

    approve_code = main_with_args(
        [
            "approve-review",
            "--review-file",
            str(review_path),
            "--decision",
            "approve",
            "--accept-patch",
            "none",
            "--authorized-track",
            "preliminary_only",
        ]
    )
    assert approve_code == 0

    approval_payload = json.loads(
        (tmp_path / "director" / "reviews" / "iteration_2_approval.json").read_text(
            encoding="utf-8"
        )
    )
    assert approval_payload["authorized_track"] == "preliminary_only"

    _run(["git", "switch", "-c", "codex/iteration3/integration"], tmp_path)
    canonical_kickoff = main_with_args(["kickoff", "--iteration", "3"])
    assert canonical_kickoff == 2

    preliminary_kickoff = main_with_args(["kickoff", "--iteration", "3", "--track", "preliminary"])
    assert preliminary_kickoff == 0
    preliminary_payload = json.loads(
        (tmp_path / "director" / "reviews" / "iteration_3_preliminary_kickoff.json").read_text(
            encoding="utf-8"
        )
    )
    assert preliminary_payload["track"] == "preliminary"
    assert preliminary_payload["status"] == "ready"

    capsys.readouterr()
    status_code = main_with_args(["status"])
    assert status_code == 0
    status_payload = json.loads(capsys.readouterr().out)
    assert status_payload["latest_authorized_track"] == "preliminary_only"
