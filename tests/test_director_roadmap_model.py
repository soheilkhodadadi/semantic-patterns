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
        "schema_version": "1.4.0",
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


def _minimal_methodology_alignment() -> dict:
    return {
        "schema_version": "1.4.0",
        "source_artifact": "docs/director/proposal_methodology.md",
        "core_construct": "AI-washing is speculative AI narrative without later observable capability.",
        "active_development_scope": "2021-2024",
        "publication_target_scope": "all publicly traded firms",
        "desired_horizon": "2000-2024 when source availability permits",
        "core_constructs": [
            "Actionable statements indicate current firm AI capability.",
            "Speculative statements indicate firm-specific AI aspiration without operational proof.",
            "Irrelevant statements mention AI generically without capability claims.",
        ],
        "label_semantics": {
            "Actionable": "present or past deployment, implementation, or operational AI use",
            "Speculative": "firm-specific aspirational or forward-looking AI narrative",
            "Irrelevant": "generic AI market, risk, regulatory, or boilerplate language",
        },
        "borderline_rules": [
            "Generic AI cyber-risk language is Irrelevant.",
            "Risk-section language becomes Actionable only when it discloses current firm AI deployment.",
        ],
        "irr_design_requirements": [
            "Stratified sample across at least 100 firms.",
            "Balanced by industry and year.",
            "Two raters plus third adjudicator.",
        ],
        "named_measures": [
            {
                "measure_id": "AI_Focus",
                "formula": "log(1 + AI sentences)",
                "description": "Firm-year AI disclosure intensity.",
                "mapped_phases": ["iteration3/firm-year-measure-construction"],
            }
        ],
        "baseline_predictive_specs": [
            "Patents and job postings at l in {0,1,2} with firm/year FE."
        ],
        "ai_washing_specification": ["A_S", "A_S x PatentMismatch"],
        "rubric_calibration_policy": [
            "Rubric refinement is allowed during development calibration."
        ],
        "rubric_freeze_policy": ["Rubric must freeze before publication-scale deployment."],
        "predictive_validity_policy": [
            "Directional predictive validity is required before publication scale."
        ],
        "hard_gates": ["IRR stratified 100-firm minimum", "Rubric freeze before final scale"],
        "requirements": [
            {
                "requirement_id": "proposal-rubric-realignment",
                "priority": "non-negotiable",
                "summary": "Rubric must be realigned to the proposal construct before tranche-1 canonical labeling continues.",
                "target_iteration": "2",
                "source_refs": ["proposal methodology"],
                "mapped_phases": ["iteration2/rubric-realignment"],
                "mapped_gates": ["rubric_realignment_complete"],
            }
        ],
    }


def _minimal_model() -> dict:
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
        "methodology_alignment": _minimal_methodology_alignment(),
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
    assert "## Methodology Alignment" in body
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
        "schema_version": "1.4.0",
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
        "methodology_alignment": _minimal_methodology_alignment(),
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


def test_optimizer_does_not_surface_review_task_when_review_phase_waits_on_phase_deps(tmp_path):
    paths = get_director_paths(tmp_path)
    model = _minimal_model()
    model["iterations"][0]["phases"] = [
        {
            "phase_id": "iteration1/substantive-phase",
            "title": "Substantive",
            "goal": "must finish first",
            "depends_on": [],
            "canonical": True,
            "required_artifacts": ["reports/substantive.json"],
            "tasks": [],
        },
        {
            "phase_id": "iteration1/review-and-replan",
            "title": "Review",
            "goal": "closeout",
            "depends_on": ["iteration1/substantive-phase"],
            "canonical": True,
            "required_artifacts": ["director/reviews/iteration_1_review.json"],
            "tasks": [
                {
                    "task_id": "iteration1.review.generate_review",
                    "title": "Generate review",
                    "description": "review task should not be recommended early",
                    "iteration_id": "1",
                    "phase_id": "iteration1/review-and-replan",
                    "kind": "analysis",
                    "depends_on": [],
                    "inputs": [],
                    "outputs": [
                        {
                            "artifact_id": "review_json",
                            "path": "director/reviews/iteration_1_review.json",
                            "kind": "json",
                            "required": True,
                        }
                    ],
                    "preconditions": [],
                    "quality_checks": [],
                    "commands": [
                        ".venv/bin/python -m semantic_ai_washing.director.cli review --iteration 1"
                    ],
                    "manual_handoff": False,
                    "risks": ["R4"],
                    "estimated_effort": 1,
                    "risk_reduction": 8,
                    "automation_level": "partial",
                    "on_fail": "block",
                    "reroute_to": [],
                    "evidence_required": True,
                    "tags": ["review_generation"],
                    "gate_class": "ops",
                }
            ],
        },
    ]
    _write_yaml(paths.model_dir / "roadmap_model.yaml", model)
    _write_yaml(paths.model_dir / "remediation_library.yaml", _minimal_library())
    optimizer = DirectorOptimizer(
        repo_root=str(tmp_path),
        roadmap_model_path=str(paths.model_dir / "roadmap_model.yaml"),
        remediation_library_path=str(paths.model_dir / "remediation_library.yaml"),
        optimization_dir=str(paths.optimization_dir),
        decisions_dir=str(paths.decisions_dir),
        weights=model["settings"]["optimizer_weights"],
    )

    report = optimizer.optimize(focus_iteration="1")

    assert "iteration1.review.generate_review" not in report.recommendation.recommended_task_ids
    assert "iteration1/review-and-replan" not in report.recommendation.recommended_phase_ids


def test_task_with_missing_outputs_and_quality_checks_remains_ready(tmp_path):
    paths = get_director_paths(tmp_path)
    model = _minimal_model()
    model["iterations"][0]["phases"] = [
        {
            "phase_id": "iteration1/build-phase",
            "title": "Build",
            "goal": "produce report before validation can pass",
            "depends_on": [],
            "canonical": True,
            "required_artifacts": [],
            "tasks": [
                {
                    "task_id": "iteration1.build.generate_report",
                    "title": "Generate report",
                    "description": "should still be runnable before outputs exist",
                    "iteration_id": "1",
                    "phase_id": "iteration1/build-phase",
                    "kind": "build",
                    "depends_on": [],
                    "inputs": [],
                    "outputs": [
                        {
                            "artifact_id": "report",
                            "path": "reports/example.json",
                            "kind": "json",
                            "required": True,
                        }
                    ],
                    "preconditions": [],
                    "quality_checks": [
                        {
                            "condition_id": "report_status_passed",
                            "kind": "json_field_compare",
                            "target": "reports/example.json::status",
                            "operator": "==",
                            "expected": "passed",
                            "on_fail": "block",
                            "message": "report must be passed",
                            "reroute_to": [],
                        }
                    ],
                    "commands": ["echo generate"],
                    "manual_handoff": False,
                    "risks": ["R1"],
                    "estimated_effort": 1,
                    "risk_reduction": 1,
                    "automation_level": "full",
                    "on_fail": "block",
                    "reroute_to": [],
                    "evidence_required": True,
                    "tags": ["build"],
                    "gate_class": "data",
                }
            ],
        }
    ]
    _write_yaml(paths.model_dir / "roadmap_model.yaml", model)
    _write_yaml(paths.model_dir / "remediation_library.yaml", _minimal_library())
    optimizer = DirectorOptimizer(
        repo_root=str(tmp_path),
        roadmap_model_path=str(paths.model_dir / "roadmap_model.yaml"),
        remediation_library_path=str(paths.model_dir / "remediation_library.yaml"),
        optimization_dir=str(paths.optimization_dir),
        decisions_dir=str(paths.decisions_dir),
        weights=model["settings"]["optimizer_weights"],
    )

    report = optimizer.optimize(focus_iteration="1")
    task_state = next(
        item for item in report.task_states if item.task_id == "iteration1.build.generate_report"
    )

    assert task_state.status == "ready"
    assert "iteration1.build.generate_report" in report.recommendation.recommended_task_ids


def test_actual_iteration2_tranche_workflow_is_wired():
    model = load_roadmap_model("director/model/roadmap_model.yaml")

    rubric_phase = find_phase(model, iteration_id="2", phase_name="rubric-realignment")
    assert rubric_phase is not None
    rubric_task_ids = [task.task_id for task in rubric_phase.tasks]
    assert rubric_task_ids == [
        "iteration2.rubric.review_tranche1_error_patterns_v2_4",
        "iteration2.rubric.publish_protocol_v2_4",
        "iteration2.rubric.generate_tranche1_clean_slice_prelables_v2_4",
        "iteration2.rubric.initialize_tranche1_clean_slice_review_v2_4",
        "iteration2.rubric.confirm_tranche1_clean_slice_v2_4",
        "iteration2.rubric.rebuild_tranche1_text_v2_4",
        "iteration2.rubric.regenerate_tranche1_assistive_prelabels_v2_4",
        "iteration2.rubric.initialize_tranche1_review_v2_4",
    ]
    generate_slice = next(
        task
        for task in rubric_phase.tasks
        if task.task_id == "iteration2.rubric.generate_tranche1_clean_slice_prelables_v2_4"
    )
    assert generate_slice.manual_handoff is False
    assert generate_slice.kind == "build"
    assert any(
        condition.kind == "json_field_compare"
        and condition.target
        == "reports/labels/assistive_prelabel_tranche1_v2_4_clean_slice40_summary.json::status"
        and condition.expected == "passed"
        for condition in generate_slice.quality_checks
    )
    assert any(
        condition.kind == "json_field_compare"
        and condition.target
        == "reports/labels/assistive_prelabel_tranche1_v2_4_clean_slice40_summary.json::usage.request_count"
        and condition.expected == 1
        and condition.operator == ">="
        for condition in generate_slice.quality_checks
    )

    initialize_slice = next(
        task
        for task in rubric_phase.tasks
        if task.task_id == "iteration2.rubric.initialize_tranche1_clean_slice_review_v2_4"
    )
    assert "semantic_ai_washing.labeling.initialize_review_sheet" in initialize_slice.commands[0]
    assert "labeling_batch_v1_filled_v2_4_clean_slice40.csv" in initialize_slice.commands[0]

    review_slice = next(
        task
        for task in rubric_phase.tasks
        if task.task_id == "iteration2.rubric.confirm_tranche1_clean_slice_v2_4"
    )
    assert review_slice.manual_handoff is False
    assert (
        review_slice.inputs[0].path == "data/labels/v1/labeling_batch_v1_filled_v2_1_slice40.csv"
    )

    rebuild_tranche1_v2_4 = next(
        task
        for task in rubric_phase.tasks
        if task.task_id == "iteration2.rubric.rebuild_tranche1_text_v2_4"
    )
    assert any(
        "semantic_ai_washing.data.reextract_tranche_slice" in command
        and "labeling_batch_v1_reextracted_v2_4.csv" in command
        for command in rebuild_tranche1_v2_4.commands
    )

    regenerate_tranche1_v2_4 = next(
        task
        for task in rubric_phase.tasks
        if task.task_id == "iteration2.rubric.regenerate_tranche1_assistive_prelabels_v2_4"
    )
    assert any(
        "assistive_prelabel_batch" in command
        and "labeling_batch_v1_prelabeled_v2_4.csv" in command
        for command in regenerate_tranche1_v2_4.commands
    )
    assert any(
        condition.kind == "json_field_compare"
        and condition.target
        == "reports/labels/assistive_prelabel_tranche1_v2_4_summary.json::status"
        and condition.expected == "passed"
        for condition in regenerate_tranche1_v2_4.quality_checks
    )

    initialize_full = next(
        task
        for task in rubric_phase.tasks
        if task.task_id == "iteration2.rubric.initialize_tranche1_review_v2_4"
    )
    assert "labeling_batch_v1_filled_v2_4.csv" in initialize_full.commands[0]

    tranche1_phase = find_phase(model, iteration_id="2", phase_name="tranche1-labeling")
    assert tranche1_phase is not None
    tranche1_task_ids = [task.task_id for task in tranche1_phase.tasks]
    assert tranche1_task_ids == ["iteration2.labels.verify_tranche1_labels"]
    verify_tranche1 = next(
        task
        for task in tranche1_phase.tasks
        if task.task_id == "iteration2.labels.verify_tranche1_labels"
    )
    assert any(
        condition.kind == "csv_nonempty_count_gte"
        and condition.target == "data/labels/v1/labeling_batch_v1_filled_v2_4.csv::label"
        and condition.expected == 237
        for condition in verify_tranche1.quality_checks
    )

    pool_phase = find_phase(model, iteration_id="2", phase_name="sentence-pool-expansion-2024")
    assert pool_phase is not None
    pool_task_ids = [task.task_id for task in pool_phase.tasks]
    assert pool_task_ids == [
        "iteration2.pool.expand_candidate_pool_batch_01",
        "iteration2.pool.expand_candidate_pool_batch_02",
        "iteration2.pool.expand_candidate_pool_batch_03",
        "iteration2.pool.expand_candidate_pool_batch_04",
        "iteration2.pool.combine_candidate_pool_batches",
        "iteration2.pool.verify_candidate_pool_targets",
    ]
    expand_task = next(
        task
        for task in pool_phase.tasks
        if task.task_id == "iteration2.pool.expand_candidate_pool_batch_01"
    )
    assert expand_task.commands
    assert "semantic_ai_washing.data.build_expanded_sentence_pool" in expand_task.commands[0]
    expand_task_04 = next(
        task
        for task in pool_phase.tasks
        if task.task_id == "iteration2.pool.expand_candidate_pool_batch_04"
    )
    assert "--exclude-manifests" in expand_task_04.commands[0]
    combine_task = next(
        task
        for task in pool_phase.tasks
        if task.task_id == "iteration2.pool.combine_candidate_pool_batches"
    )
    assert (
        "semantic_ai_washing.data.combine_expanded_sentence_pool_batches"
        in combine_task.commands[0]
    )
    verify_pool = next(
        task
        for task in pool_phase.tasks
        if task.task_id == "iteration2.pool.verify_candidate_pool_targets"
    )
    assert any(
        condition.kind == "json_field_compare"
        and condition.target
        == "reports/labels/sentence_pool_expansion_2024_summary.json::candidate_pool.firm_count"
        and condition.expected == 500
        for condition in verify_pool.quality_checks
    )
    assert any(
        condition.kind == "json_field_compare"
        and condition.target
        == "reports/labels/sentence_pool_expansion_2024_summary.json::candidate_pool.clean_sentence_count"
        and condition.expected == 1000
        for condition in verify_pool.quality_checks
    )

    tranche2_phase = find_phase(model, iteration_id="2", phase_name="tranche2-labeling")
    assert tranche2_phase is not None
    tranche2_prepare = next(
        task
        for task in tranche2_phase.tasks
        if task.task_id == "iteration2.labels.prepare_tranche2_labeling_batch"
    )
    assert "--target-size 160" in tranche2_prepare.commands[0]
    assert "--base-quarter-quota 40" in tranche2_prepare.commands[0]
    assert (
        "--exclude-existing-csv data/labels/v1/labeling_batch_v1.csv"
        in tranche2_prepare.commands[0]
    )
    assert any(
        condition.kind == "json_field_compare"
        and condition.target
        == "reports/labels/labeling_batch_v2_summary.json::selection.batch_row_count"
        and condition.expected == 160
        for condition in tranche2_prepare.quality_checks
    )

    tranche3_phase = find_phase(model, iteration_id="2", phase_name="tranche3-labeling")
    assert tranche3_phase is not None
    tranche3_prepare = next(
        task
        for task in tranche3_phase.tasks
        if task.task_id == "iteration2.labels.prepare_tranche3_labeling_batch"
    )
    assert (
        "--exclude-existing-csv data/labels/v1/labeling_batch_v1.csv data/labels/v1/labeling_batch_v2.csv"
        in tranche3_prepare.commands[0]
    )

    merge_phase = find_phase(model, iteration_id="2", phase_name="merge-canonical-labels")
    assert merge_phase is not None
    merge_task = next(
        task
        for task in merge_phase.tasks
        if task.task_id == "iteration2.labels.merge_canonical_labels"
    )
    assert "semantic_ai_washing.labeling.merge_labeling_batches" in merge_task.commands[0]
    assert "data/labels/v1/labeling_batch_v3_filled.csv" in merge_task.commands[0]
    assert "data/labels/v1/labeling_batch_v1_filled_v2_4.csv" in merge_task.commands[0]
    assert any(
        condition.kind == "json_field_compare"
        and condition.target
        == "reports/labels/label_expansion_summary.json::summary.total_canonical_labeled_rows"
        and condition.expected == 551
        for condition in merge_task.quality_checks
    )

    irr_phase = find_phase(model, iteration_id="2", phase_name="irr-and-adjudication")
    assert irr_phase is not None
    irr_prepare = next(
        task for task in irr_phase.tasks if task.task_id == "iteration2.irr.prepare_subset_handoff"
    )
    assert "semantic_ai_washing.labeling.prepare_irr_subset" in irr_prepare.commands[0]
    assert "--target-size 120" in irr_prepare.commands[0]
    assert "--class-quota 40" in irr_prepare.commands[0]
    assert "--min-unique-firms 100" in irr_prepare.commands[0]
    assert any(
        condition.kind == "json_field_compare"
        and condition.target
        == "reports/labels/irr_subset_sampling_report.json::summary.unique_firms"
        and condition.expected == 100
        for condition in irr_prepare.quality_checks
    )

    irr_collect = next(
        task for task in irr_phase.tasks if task.task_id == "iteration2.irr.collect_rater2_labels"
    )
    assert irr_collect.manual_handoff is True
    assert irr_collect.outputs[0].path == "data/labels/v1/irr_subset_rater2_completed.xlsx"

    irr_compute = next(
        task
        for task in irr_phase.tasks
        if task.task_id == "iteration2.irr.compute_and_seed_adjudication"
    )
    assert "semantic_ai_washing.labeling.adjudicate_irr_labels" in irr_compute.commands[0]
    assert "semantic_ai_washing.labeling.compute_irr_metrics" in irr_compute.commands[1]
    assert any(
        condition.kind == "json_field_compare"
        and condition.target == "reports/labels/irr_report.json::summary.status"
        and condition.operator == "in"
        for condition in irr_compute.quality_checks
    )

    irr_finalize = next(
        task
        for task in irr_phase.tasks
        if task.task_id == "iteration2.irr.finalize_adjudication_and_report"
    )
    assert "data/labels/v1/irr_adjudication_completed.xlsx" in irr_finalize.commands[0]
    assert any(
        condition.kind == "manual_artifact_present"
        and condition.target == "data/labels/v1/irr_adjudication_completed.xlsx"
        for condition in irr_finalize.preconditions
    )
    assert any(
        condition.kind == "json_field_compare"
        and condition.target == "reports/labels/irr_report.json::summary.status"
        and condition.expected == "passed"
        for condition in irr_finalize.quality_checks
    )

    irr_diagnostic_phase = find_phase(
        model, iteration_id="2", phase_name="irr-disagreement-diagnostic"
    )
    assert irr_diagnostic_phase is not None
    assert irr_diagnostic_phase.canonical is False
    irr_diagnostic_task = next(
        task
        for task in irr_diagnostic_phase.tasks
        if task.task_id == "iteration2.irr.publish_disagreement_diagnostic"
    )
    assert (
        "semantic_ai_washing.labeling.diagnose_irr_disagreements"
        in irr_diagnostic_task.commands[0]
    )
    assert any(
        condition.kind == "json_field_compare"
        and condition.target == "reports/labels/irr_adjudication_status.json::summary.status"
        and condition.expected == "finalized"
        for condition in irr_diagnostic_task.preconditions
    )

    freeze_phase = find_phase(
        model, iteration_id="2", phase_name="provisional-rubric-freeze-and-split-registry"
    )
    assert freeze_phase is not None
    assert any(
        task.task_id == "iteration2.rubric.publish_provisional_freeze"
        for task in freeze_phase.tasks
    )

    prelim_auth_phase = find_phase(
        model, iteration_id="2", phase_name="preliminary-results-authorization"
    )
    assert prelim_auth_phase is not None
    assert prelim_auth_phase.canonical is False
    prelim_auth_task = next(
        task
        for task in prelim_auth_phase.tasks
        if task.task_id == "iteration2.prelim.publish_preliminary_results_readiness"
    )
    assert (
        "semantic_ai_washing.labeling.publish_preliminary_results_readiness"
        in prelim_auth_task.commands[0]
    )
    assert any(
        condition.kind == "json_field_compare"
        and condition.target
        == "reports/models/preliminary_results_readiness_v1.json::summary.preliminary_only"
        and condition.expected is True
        for condition in prelim_auth_task.quality_checks
    )
    assert any(
        condition.kind == "json_field_compare"
        and condition.target
        == "reports/models/preliminary_results_readiness_v1.json::summary.publication_grade_authorized"
        and condition.expected is False
        for condition in prelim_auth_task.quality_checks
    )

    measures_phase = find_phase(
        model, iteration_id="3", phase_name="firm-year-measure-construction"
    )
    assert measures_phase is not None
    validity_phase = find_phase(
        model, iteration_id="3", phase_name="development-predictive-validity-gate"
    )
    assert validity_phase is not None

    prelim_kickoff_phase = find_phase(
        model, iteration_id="3", phase_name="preliminary-kickoff-and-preflight"
    )
    assert prelim_kickoff_phase is not None
    assert prelim_kickoff_phase.canonical is False

    prelim_retraining_phase = find_phase(
        model, iteration_id="3", phase_name="preliminary-centroid-retraining"
    )
    assert prelim_retraining_phase is not None
    assert prelim_retraining_phase.canonical is False
    assert (
        "artifacts/models/mpnet_prelim_v1/centroids.json"
        in prelim_retraining_phase.required_artifacts
    )

    prelim_eval_phase = find_phase(
        model, iteration_id="3", phase_name="preliminary-heldout-evaluation"
    )
    assert prelim_eval_phase is not None
    assert prelim_eval_phase.canonical is False
    assert "reports/evaluation/heldout_eval_prelim_v1.json" in prelim_eval_phase.required_artifacts

    prelim_classify_phase = find_phase(
        model, iteration_id="3", phase_name="preliminary-active-window-classification"
    )
    assert prelim_classify_phase is not None
    assert prelim_classify_phase.canonical is False
    assert (
        "data/processed/classifications/year=2024/model=mpnet_prelim_v1/classified_sentences.parquet"
        in prelim_classify_phase.required_artifacts
    )

    prelim_measures_phase = find_phase(
        model, iteration_id="3", phase_name="preliminary-firm-year-measure-construction"
    )
    assert prelim_measures_phase is not None
    assert prelim_measures_phase.canonical is False
    assert (
        "data/processed/aggregates/firm_year_narrative_measures_prelim_v1.parquet"
        in prelim_measures_phase.required_artifacts
    )

    prelim_panel_phase = find_phase(
        model, iteration_id="4", phase_name="preliminary-panel-assembly-2021-2024"
    )
    assert prelim_panel_phase is not None
    assert prelim_panel_phase.canonical is False
    assert "data/panels/panel_prelim_v1.parquet" in prelim_panel_phase.required_artifacts

    prelim_panel_qa_phase = find_phase(model, iteration_id="4", phase_name="preliminary-panel-qa")
    assert prelim_panel_qa_phase is not None
    assert prelim_panel_qa_phase.canonical is False
    assert "reports/panels/panel_prelim_qa_v1.json" in prelim_panel_qa_phase.required_artifacts

    prelim_regression_phase = find_phase(
        model, iteration_id="5", phase_name="preliminary-regression-specification"
    )
    assert prelim_regression_phase is not None
    assert prelim_regression_phase.canonical is False
    assert (
        "reports/analysis/regression_specification_prelim_v1.json"
        in prelim_regression_phase.required_artifacts
    )

    prelim_results_phase = find_phase(
        model, iteration_id="5", phase_name="preliminary-results-generation"
    )
    assert prelim_results_phase is not None
    assert prelim_results_phase.canonical is False
    assert (
        "reports/analysis/results_manifest_prelim_v1.json"
        in prelim_results_phase.required_artifacts
    )

    prelim_package_phase = find_phase(
        model, iteration_id="5", phase_name="preliminary-results-package"
    )
    assert prelim_package_phase is not None
    assert prelim_package_phase.canonical is False
    assert (
        "reports/release/preliminary_release_manifest_v1.json"
        in prelim_package_phase.required_artifacts
    )

    prelim_table_phase = find_phase(
        model, iteration_id="5", phase_name="preliminary-results-table-planning"
    )
    assert prelim_table_phase is not None
    assert prelim_table_phase.canonical is False
    assert prelim_table_phase.lifecycle_state == "deferred"
    prelim_table_task = next(
        task
        for task in prelim_table_phase.tasks
        if task.task_id == "iteration5.prelim.define_first_results_tables"
    )
    assert prelim_table_task.manual_handoff is True
    assert (
        prelim_table_task.outputs[0].path
        == "reports/analysis/preliminary_results_table_plan_v1.md"
    )

    upgrade_phase = find_phase(
        model, iteration_id="6", phase_name="post-preliminary-publication-grade-upgrade"
    )
    assert upgrade_phase is not None
    assert upgrade_phase.lifecycle_state == "deferred"
    assert "reports/models/publication_upgrade_plan_v1.json" in upgrade_phase.required_artifacts

    review_phase = find_phase(model, iteration_id="2", phase_name="review-and-replan")
    assert review_phase is not None
    review_task = next(
        task for task in review_phase.tasks if task.task_id == "iteration2.review.generate_review"
    )
    assert review_task.depends_on == ["iteration2.labels.verify_label_sufficiency"]
