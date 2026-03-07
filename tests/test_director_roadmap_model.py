from __future__ import annotations

import json
from pathlib import Path

import yaml

from semantic_ai_washing.director.core.config import (
    ensure_default_configs,
    get_director_paths,
    load_configs,
)
from semantic_ai_washing.director.core.optimizer import DirectorOptimizer
from semantic_ai_washing.director.core.planner import PlannerEngine
from semantic_ai_washing.director.core.readiness import ReadinessEvaluator
from semantic_ai_washing.director.core.render import (
    is_rendered_roadmap_fresh,
    render_roadmap_markdown,
)
from semantic_ai_washing.director.core.roadmap_model import (
    find_phase,
    load_remediation_library,
    load_roadmap_model,
)
from semantic_ai_washing.director.core.task_graph import build_task_graph
from semantic_ai_washing.director.core.utils import sha256_file


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _minimal_stakeholder_alignment() -> dict:
    return {
        "schema_version": "1.3.0",
        "source_artifact": "docs/director/stakeholder_expectations.md",
        "active_development_scope": "2021-2024",
        "publication_target_scope": "all publicly traded firms",
        "desired_horizon": "20-year horizon",
        "methodology_hard_gates": ["human-human IRR only"],
        "data_hard_gates": ["500 firms", "1-2k clean AI sentences"],
        "publication_hard_gates": ["paper package required"],
        "requirements": [
            {
                "requirement_id": "stakeholder-scale",
                "stakeholder": "Kuntara",
                "priority": "publication-critical",
                "summary": "Scale the dataset before retraining.",
                "target_iteration": "2",
                "source_refs": ["email thread 2025-08-27"],
                "mapped_phases": ["iteration2/source-index-contract"],
                "mapped_gates": ["candidate_pool_500_firms"],
            }
        ],
    }


def _minimal_model() -> dict:
    return {
        "schema_version": "1.3.0",
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
            "integration_branch_template": "iteration{iteration_id}/integration",
            "work_branch_template": "iteration{iteration_id}/{slug}",
            "merge_target": "main",
            "preferred_merge_strategy": "ff_only_if_possible_else_pr_merge_commit",
            "require_review_approval_before_next_iteration": True,
            "require_review_approval_before_main_merge": True,
            "suggest_new_chat_at_iteration_boundary": True,
            "starter_prompt_required": True,
            "tag_template": "iteration{iteration_id}-closeout",
            "closeout_validation_commands": [
                "make bootstrap",
                "make doctor",
                "make format",
                "make lint",
                ".venv/bin/pytest -q",
            ],
        },
        "stakeholder_alignment": _minimal_stakeholder_alignment(),
        "policies": [
            {
                "policy_id": "heldout_frozen",
                "kind": "dataset_freeze",
                "description": "held-out locked",
                "enforcement": "hard",
                "targets": ["data/validation/held_out_sentences.csv"],
                "value": True,
            },
            {
                "policy_id": "openai_assistive_only",
                "kind": "model_governance",
                "description": "assistive only",
                "enforcement": "hard",
                "targets": ["iteration2/api-bootstrap"],
                "value": "assistive_only",
            },
        ],
        "data_layers": [
            {
                "layer_id": "source_index",
                "canonical_path": "data/metadata/available_filings_index.csv",
                "format": "csv",
                "required_fields": ["cik", "year", "path"],
            }
        ],
        "source_windows": [
            {
                "source_window_id": "active_2021_2024",
                "years": ["2021", "2022", "2023", "2024"],
                "source_root_ref": "env:SEC_SOURCE_DIR",
                "status": "active",
            },
            {
                "source_window_id": "historical_2000_2020",
                "years": ["2000-2020"],
                "source_root_ref": "env:SEC_SOURCE_DIR",
                "status": "deferred",
            },
        ],
        "tooling_policies": [
            {
                "policy_id": "atlas_isolated_env",
                "tool": "atlas",
                "mode": "isolated_skill_env",
                "repo_root_uv_run_forbidden": True,
                "required_runner": "~/.codex/skills/atlas/scripts/atlas_cli.py",
                "wrapper_path": "scripts/atlas_isolated.sh",
                "expected_repo_venv_python": "3.9",
                "expected_repo_venv_home": "anaconda3/bin",
            }
        ],
        "iterations": [
            {
                "iteration_id": "1",
                "title": "Foundation",
                "goal": "goal",
                "entry_criteria": [],
                "exit_criteria": [],
                "phases": [
                    {
                        "phase_id": "iteration1/label-ops-bootstrap",
                        "title": "Label ops",
                        "goal": "goal",
                        "depends_on": [],
                        "canonical": True,
                        "required_artifacts": ["reports/quality.json"],
                        "source_window_id": "active_2021_2024",
                        "tasks": [
                            {
                                "task_id": "iteration1.shared.audit_sentence_integrity",
                                "title": "Audit source",
                                "description": "check quality",
                                "iteration_id": "1",
                                "phase_id": "iteration1/label-ops-bootstrap",
                                "kind": "diagnostic",
                                "depends_on": [],
                                "inputs": [],
                                "outputs": [
                                    {
                                        "artifact_id": "source",
                                        "path": "data/recovery.csv",
                                        "kind": "dataset",
                                        "required": True,
                                    }
                                ],
                                "preconditions": [
                                    {
                                        "condition_id": "audit.exists",
                                        "kind": "artifact_exists",
                                        "target": "data/recovery.csv",
                                        "operator": "==",
                                        "expected": True,
                                        "on_fail": "block",
                                        "message": "missing source",
                                        "reroute_to": [],
                                    }
                                ],
                                "quality_checks": [
                                    {
                                        "condition_id": "audit.fragment_rate",
                                        "kind": "sentence_fragment_rate_lte",
                                        "target": "data/recovery.csv",
                                        "operator": "<=",
                                        "expected": 0.15,
                                        "on_fail": "reroute",
                                        "message": "fragmentation high",
                                        "reroute_to": ["common.remediate_fragmented_sentences"],
                                    }
                                ],
                                "commands": [],
                                "manual_handoff": False,
                                "risks": ["R1"],
                                "estimated_effort": 2,
                                "risk_reduction": 9,
                                "automation_level": "partial",
                                "on_fail": "reroute",
                                "reroute_to": ["common.remediate_fragmented_sentences"],
                                "evidence_required": True,
                                "tags": ["sentence_quality_gate"],
                                "gate_class": "data",
                            },
                            {
                                "task_id": "iteration1.labels.manual_labeling",
                                "title": "Labeling",
                                "description": "manual",
                                "iteration_id": "1",
                                "phase_id": "iteration1/label-ops-bootstrap",
                                "kind": "manual",
                                "depends_on": ["iteration1.shared.audit_sentence_integrity"],
                                "inputs": [],
                                "outputs": [
                                    {
                                        "artifact_id": "labels",
                                        "path": "data/labels.csv",
                                        "kind": "csv",
                                        "required": True,
                                    }
                                ],
                                "preconditions": [],
                                "quality_checks": [],
                                "commands": [],
                                "manual_handoff": True,
                                "risks": ["R1"],
                                "estimated_effort": 8,
                                "risk_reduction": 8,
                                "automation_level": "manual",
                                "on_fail": "block",
                                "reroute_to": [],
                                "evidence_required": True,
                                "tags": ["human_labeling"],
                                "gate_class": "manual",
                            },
                        ],
                    },
                    {
                        "phase_id": "iteration1/legacy-diagnostics",
                        "title": "Legacy",
                        "goal": "goal",
                        "depends_on": [],
                        "canonical": False,
                        "required_artifacts": ["reports/legacy.json"],
                        "lifecycle_state": "historical",
                        "tasks": [],
                    },
                ],
            },
            {
                "iteration_id": "2",
                "title": "Future",
                "goal": "goal",
                "entry_criteria": [],
                "exit_criteria": [],
                "phases": [
                    {
                        "phase_id": "iteration2/source-index-contract",
                        "title": "Source index",
                        "goal": "goal",
                        "depends_on": [],
                        "canonical": True,
                        "required_artifacts": ["data/metadata/available_filings_index.csv"],
                        "source_window_id": "active_2021_2024",
                        "tasks": [],
                    },
                    {
                        "phase_id": "iteration2/historical-backfill",
                        "title": "Historical backfill",
                        "goal": "goal",
                        "depends_on": [],
                        "canonical": True,
                        "required_artifacts": ["reports/history.json"],
                        "lifecycle_state": "deferred",
                        "source_window_id": "historical_2000_2020",
                        "tasks": [],
                    },
                ],
            },
        ],
    }


def _policy_block_model() -> dict:
    model = _minimal_model()
    model["iterations"][0]["phases"].append(
        {
            "phase_id": "iteration1/illegal-training",
            "title": "Illegal training",
            "goal": "goal",
            "depends_on": [],
            "canonical": True,
            "required_artifacts": [],
            "tasks": [
                {
                    "task_id": "iteration1.training.illegal_heldout",
                    "title": "Illegal heldout use",
                    "description": "should be blocked",
                    "iteration_id": "1",
                    "phase_id": "iteration1/illegal-training",
                    "kind": "build",
                    "depends_on": [],
                    "inputs": [
                        {
                            "artifact_id": "heldout",
                            "path": "data/validation/held_out_sentences.csv",
                            "kind": "csv",
                            "required": True,
                        }
                    ],
                    "outputs": [],
                    "preconditions": [],
                    "quality_checks": [],
                    "commands": [],
                    "manual_handoff": False,
                    "risks": ["R3"],
                    "estimated_effort": 2,
                    "risk_reduction": 6,
                    "automation_level": "full",
                    "on_fail": "block",
                    "reroute_to": [],
                    "evidence_required": True,
                    "tags": ["training"],
                    "gate_class": "science",
                }
            ],
        }
    )
    return model


def _minimal_library() -> dict:
    return {
        "schema_version": "1.3.0",
        "tasks": [
            {
                "task_id": "common.remediate_fragmented_sentences",
                "title": "Remediate fragments",
                "description": "manual remediation",
                "iteration_id": "common",
                "phase_id": "common/remediation",
                "kind": "remediation",
                "depends_on": [],
                "inputs": [],
                "outputs": [],
                "preconditions": [],
                "quality_checks": [],
                "commands": [],
                "manual_handoff": True,
                "risks": ["R5"],
                "estimated_effort": 5,
                "risk_reduction": 8,
                "automation_level": "manual",
                "on_fail": "block",
                "reroute_to": [],
                "evidence_required": True,
                "tags": ["sentence_quality_remediation"],
                "gate_class": "manual",
            }
        ],
    }


def test_load_and_render_roadmap_model(tmp_path):
    model_path = tmp_path / "director" / "model" / "roadmap_model.yaml"
    _write_yaml(model_path, _minimal_model())

    model = load_roadmap_model(model_path)
    md_path = tmp_path / "docs" / "director" / "roadmap_master.md"
    rendered = render_roadmap_markdown(
        model=model,
        source_model=str(model_path),
        source_sha256=sha256_file(model_path),
    )
    _write(md_path, rendered)
    assert is_rendered_roadmap_fresh(model_path, md_path)
    body = md_path.read_text(encoding="utf-8")
    assert "generated from the canonical roadmap YAML model" in body
    assert "## Policies" in body
    assert "## Data Layers" in body
    assert "## Stakeholder Alignment" in body
    assert "stakeholder-scale" in body


def test_optimizer_emits_artifacts_and_patch(tmp_path):
    paths = get_director_paths(str(tmp_path))
    ensure_default_configs(paths)
    _write_yaml(paths.model_dir / "roadmap_model.yaml", _minimal_model())
    _write_yaml(paths.model_dir / "remediation_library.yaml", _minimal_library())
    _write(paths.snapshots_dir / "protocol_summary.json", json.dumps({"source_sha256": "a"}))
    _write(paths.snapshots_dir / "roadmap_summary.json", json.dumps({"source_sha256": "b"}))
    _write(paths.snapshots_dir / "iteration_state.json", json.dumps({"iterations": []}))
    _write(
        tmp_path / "data" / "recovery.csv",
        "sentence\nfragment without punctuation\nanother bad fragment\n",
    )

    optimizer = DirectorOptimizer(
        repo_root=str(tmp_path),
        roadmap_model_path=str(paths.model_dir / "roadmap_model.yaml"),
        remediation_library_path=str(paths.model_dir / "remediation_library.yaml"),
        optimization_dir=str(paths.optimization_dir),
        decisions_dir=str(paths.decisions_dir),
        weights=load_configs(paths)["project_profile"]["optimization_weights"],
        emit_patch=True,
    )
    report = optimizer.optimize(focus_iteration="1", focus_phase="label-ops-bootstrap")

    assert Path(report.graph_file).exists()
    assert Path(report.readiness_file).exists()
    assert Path(report.recommendation_file).exists()
    assert Path(report.recommendation_markdown).exists()
    assert report.patch_file
    assert "iteration1.shared.audit_sentence_integrity" in report.recommendation.blocked_task_ids


def test_optimizer_ranks_phase_level_work_and_ignores_historical(tmp_path):
    paths = get_director_paths(str(tmp_path))
    ensure_default_configs(paths)
    _write_yaml(paths.model_dir / "roadmap_model.yaml", _minimal_model())
    _write_yaml(paths.model_dir / "remediation_library.yaml", _minimal_library())
    _write(paths.snapshots_dir / "protocol_summary.json", json.dumps({"source_sha256": "a"}))
    _write(paths.snapshots_dir / "roadmap_summary.json", json.dumps({"source_sha256": "b"}))
    _write(paths.snapshots_dir / "iteration_state.json", json.dumps({"iterations": []}))

    optimizer = DirectorOptimizer(
        repo_root=str(tmp_path),
        roadmap_model_path=str(paths.model_dir / "roadmap_model.yaml"),
        remediation_library_path=str(paths.model_dir / "remediation_library.yaml"),
        optimization_dir=str(paths.optimization_dir),
        decisions_dir=str(paths.decisions_dir),
        weights=load_configs(paths)["project_profile"]["optimization_weights"],
        emit_patch=False,
    )
    report = optimizer.optimize()

    assert "iteration2/source-index-contract" in report.recommendation.recommended_phase_ids
    assert "iteration1/legacy-diagnostics" not in report.recommendation.recommended_phase_ids
    assert "iteration2/historical-backfill" in report.recommendation.blocked_phase_ids


def test_planner_uses_task_graph_for_modeled_phase(tmp_path):
    paths = get_director_paths(str(tmp_path))
    ensure_default_configs(paths)
    _write_yaml(paths.model_dir / "roadmap_model.yaml", _minimal_model())
    _write_yaml(paths.model_dir / "remediation_library.yaml", _minimal_library())
    _write(paths.snapshots_dir / "protocol_summary.json", json.dumps({"source_sha256": "a"}))
    _write(paths.snapshots_dir / "roadmap_summary.json", json.dumps({"source_sha256": "b"}))
    _write(paths.snapshots_dir / "iteration_state.json", json.dumps({"source_sha256": "c"}))

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
    result = planner.generate(iteration_id="1", phase_name="label-ops-bootstrap")
    payload = yaml.safe_load(Path(result["runbook_file"]).read_text(encoding="utf-8"))
    titles = [step["title"] for step in payload["steps"]]

    assert any(title.startswith("Task precondition: Audit source") for title in titles)
    assert any(title.startswith("Manual handoff: Labeling") for title in titles)


def test_policy_block_is_reported(tmp_path):
    paths = get_director_paths(str(tmp_path))
    ensure_default_configs(paths)
    _write_yaml(paths.model_dir / "roadmap_model.yaml", _policy_block_model())
    _write_yaml(paths.model_dir / "remediation_library.yaml", _minimal_library())
    _write(paths.snapshots_dir / "protocol_summary.json", json.dumps({"source_sha256": "a"}))
    _write(paths.snapshots_dir / "roadmap_summary.json", json.dumps({"source_sha256": "b"}))
    _write(paths.snapshots_dir / "iteration_state.json", json.dumps({"iterations": []}))

    optimizer = DirectorOptimizer(
        repo_root=str(tmp_path),
        roadmap_model_path=str(paths.model_dir / "roadmap_model.yaml"),
        remediation_library_path=str(paths.model_dir / "remediation_library.yaml"),
        optimization_dir=str(paths.optimization_dir),
        decisions_dir=str(paths.decisions_dir),
        weights=load_configs(paths)["project_profile"]["optimization_weights"],
        emit_patch=False,
    )
    report = optimizer.optimize(focus_iteration="1", focus_phase="illegal-training")

    assert "heldout_frozen" in report.recommendation.policy_block_ids
    assert "iteration1.training.illegal_heldout" in report.recommendation.blocked_task_ids


def test_load_remediation_library_validates(tmp_path):
    library_path = tmp_path / "director" / "model" / "remediation_library.yaml"
    _write_yaml(library_path, _minimal_library())
    library = load_remediation_library(library_path)
    assert "common.remediate_fragmented_sentences" in library


def test_phase_dependencies_flow_into_task_readiness(tmp_path):
    model_payload = {
        "schema_version": "1.3.0",
        "project": {"name": "semantic-patterns", "description": "test"},
        "settings": {"defaults": {"phase_execution_mode": "phase_first"}},
        "branching_policy": {
            "schema_version": "1.0.0",
            "integration_branch_template": "iteration{iteration_id}/integration",
            "work_branch_template": "iteration{iteration_id}/{slug}",
            "merge_target": "main",
            "preferred_merge_strategy": "ff_only_if_possible_else_pr_merge_commit",
            "require_review_approval_before_next_iteration": True,
            "require_review_approval_before_main_merge": True,
            "suggest_new_chat_at_iteration_boundary": True,
            "starter_prompt_required": True,
            "tag_template": "iteration{iteration_id}-closeout",
            "closeout_validation_commands": [".venv/bin/pytest -q"],
        },
        "stakeholder_alignment": _minimal_stakeholder_alignment(),
        "policies": [],
        "data_layers": [],
        "source_windows": [],
        "tooling_policies": [],
        "iterations": [
            {
                "iteration_id": "1",
                "title": "Foundation",
                "goal": "goal",
                "entry_criteria": [],
                "exit_criteria": [],
                "phases": [
                    {
                        "phase_id": "iteration1/phase-a",
                        "title": "Phase A",
                        "goal": "goal",
                        "depends_on": [],
                        "tasks": [
                            {
                                "task_id": "iteration1.phase_a.blocked",
                                "title": "Blocked",
                                "description": "blocked output",
                                "iteration_id": "1",
                                "phase_id": "iteration1/phase-a",
                                "kind": "validation",
                                "depends_on": [],
                                "inputs": [],
                                "outputs": [
                                    {
                                        "artifact_id": "missing",
                                        "path": "reports/missing.json",
                                        "kind": "json",
                                        "required": True,
                                    }
                                ],
                                "preconditions": [],
                                "quality_checks": [
                                    {
                                        "condition_id": "missing_status",
                                        "kind": "json_field_compare",
                                        "target": "reports/missing.json::status",
                                        "operator": "==",
                                        "expected": "passed",
                                        "on_fail": "block",
                                        "message": "blocked",
                                        "reroute_to": [],
                                    }
                                ],
                                "commands": [],
                                "manual_handoff": False,
                                "risks": [],
                                "estimated_effort": 1,
                                "risk_reduction": 1,
                                "automation_level": "partial",
                                "on_fail": "block",
                                "reroute_to": [],
                                "evidence_required": True,
                                "tags": [],
                                "gate_class": "ops",
                            }
                        ],
                    },
                    {
                        "phase_id": "iteration1/phase-b",
                        "title": "Phase B",
                        "goal": "goal",
                        "depends_on": ["iteration1/phase-a"],
                        "tasks": [
                            {
                                "task_id": "iteration1.phase_b.ready_without_phase_dep_fix",
                                "title": "Downstream",
                                "description": "should inherit phase deps",
                                "iteration_id": "1",
                                "phase_id": "iteration1/phase-b",
                                "kind": "build",
                                "depends_on": ["iteration1.shared.other_task"],
                                "inputs": [],
                                "outputs": [
                                    {
                                        "artifact_id": "later",
                                        "path": "reports/later.json",
                                        "kind": "json",
                                        "required": True,
                                    }
                                ],
                                "preconditions": [],
                                "quality_checks": [],
                                "commands": [],
                                "manual_handoff": False,
                                "risks": [],
                                "estimated_effort": 1,
                                "risk_reduction": 1,
                                "automation_level": "partial",
                                "on_fail": "block",
                                "reroute_to": [],
                                "evidence_required": True,
                                "tags": [],
                                "gate_class": "ops",
                            },
                            {
                                "task_id": "iteration1.shared.other_task",
                                "title": "Other",
                                "description": "supporting dep",
                                "iteration_id": "1",
                                "phase_id": "iteration1/phase-b",
                                "kind": "build",
                                "depends_on": [],
                                "inputs": [],
                                "outputs": [],
                                "preconditions": [],
                                "quality_checks": [],
                                "commands": [],
                                "manual_handoff": False,
                                "risks": [],
                                "estimated_effort": 1,
                                "risk_reduction": 1,
                                "automation_level": "partial",
                                "on_fail": "block",
                                "reroute_to": [],
                                "evidence_required": True,
                                "tags": [],
                                "gate_class": "ops",
                            },
                        ],
                    },
                ],
            }
        ],
    }

    model_path = tmp_path / "director" / "model" / "roadmap_model.yaml"
    _write_yaml(model_path, model_payload)
    model = load_roadmap_model(model_path)
    graph = build_task_graph(model)
    evaluator = ReadinessEvaluator(repo_root=str(tmp_path), graph=graph, model=model)
    task_states, _ = evaluator.evaluate_all()
    state_map = {item.task_id: item for item in task_states}

    assert state_map["iteration1.phase_b.ready_without_phase_dep_fix"].status == "waiting_on_deps"
    assert (
        "iteration1.phase_a.blocked"
        in state_map["iteration1.phase_b.ready_without_phase_dep_fix"].missing_dependencies
    )


def test_actual_label_ops_phase_has_executable_batch_builder():
    model = load_roadmap_model("director/model/roadmap_model.yaml")
    phase = find_phase(model, iteration_id="1", phase_name="label-ops-bootstrap")

    assert phase is not None
    assert "reports/labels/labeling_batch_v1_summary.json" in phase.required_artifacts

    task = next(
        task for task in phase.tasks if task.task_id == "iteration1.labels.prepare_labeling_batch"
    )
    assert task.commands
    assert "semantic_ai_washing.labeling.build_labeling_batch" in task.commands[0]
    quality_targets = {condition.target for condition in task.quality_checks}
    assert (
        "reports/labels/labeling_batch_v1_summary.json::selection.batch_row_count"
        in quality_targets
    )
    assert (
        "reports/labels/labeling_batch_v1_summary.json::quality.heldout_overlap_count"
        in quality_targets
    )
