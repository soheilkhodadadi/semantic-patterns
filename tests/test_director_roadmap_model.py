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
from semantic_ai_washing.director.core.render import (
    is_rendered_roadmap_fresh,
    render_roadmap_markdown,
)
from semantic_ai_washing.director.core.roadmap_model import (
    load_remediation_library,
    load_roadmap_model,
)
from semantic_ai_washing.director.core.utils import sha256_file


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _minimal_model() -> dict:
    return {
        "schema_version": "1.1.0",
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
            },
        },
        "iterations": [
            {
                "iteration_id": "1",
                "title": "Test iteration",
                "goal": "goal",
                "phases": [
                    {
                        "phase_id": "iteration1/irr-validation",
                        "title": "IRR",
                        "goal": "goal",
                        "depends_on": [],
                        "canonical": True,
                        "required_artifacts": ["reports/irr_status.json"],
                        "tasks": [
                            {
                                "task_id": "iteration1.shared.audit_sentence_integrity",
                                "title": "Audit source",
                                "description": "check quality",
                                "iteration_id": "1",
                                "phase_id": "iteration1/irr-validation",
                                "kind": "diagnostic",
                                "depends_on": [],
                                "inputs": [],
                                "outputs": [
                                    {
                                        "artifact_id": "source",
                                        "path": "data/recovery.csv",
                                        "kind": "dataset",
                                        "required": True,
                                        "fingerprint_required": False,
                                        "produced_by": [],
                                        "consumed_by": ["iteration1.irr.prepare_subset"],
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
                            },
                            {
                                "task_id": "iteration1.irr.manual_rater2_handoff",
                                "title": "Rater 2",
                                "description": "manual",
                                "iteration_id": "1",
                                "phase_id": "iteration1/irr-validation",
                                "kind": "manual",
                                "depends_on": ["iteration1.shared.audit_sentence_integrity"],
                                "inputs": [],
                                "outputs": [
                                    {
                                        "artifact_id": "rater2",
                                        "path": "data/rater2.csv",
                                        "kind": "csv",
                                        "required": True,
                                        "fingerprint_required": False,
                                        "produced_by": ["iteration1.irr.manual_rater2_handoff"],
                                        "consumed_by": [],
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
                            },
                        ],
                    }
                ],
            }
        ],
    }


def _minimal_library() -> dict:
    return {
        "schema_version": "1.1.0",
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
    assert "generated from the canonical roadmap YAML model" in md_path.read_text(encoding="utf-8")


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
    report = optimizer.optimize(focus_iteration="1", focus_phase="irr-validation")

    assert Path(report.graph_file).exists()
    assert Path(report.readiness_file).exists()
    assert Path(report.recommendation_file).exists()
    assert Path(report.recommendation_markdown).exists()
    assert report.patch_file
    assert "iteration1.shared.audit_sentence_integrity" in report.recommendation.blocked_task_ids


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
    result = planner.generate(iteration_id="1", phase_name="irr-validation")
    payload = yaml.safe_load(Path(result["runbook_file"]).read_text(encoding="utf-8"))
    titles = [step["title"] for step in payload["steps"]]

    assert any(title.startswith("Task precondition: Audit source") for title in titles)
    assert any(title.startswith("Manual handoff: Rater 2") for title in titles)


def test_load_remediation_library_validates(tmp_path):
    library_path = tmp_path / "director" / "model" / "remediation_library.yaml"
    _write_yaml(library_path, _minimal_library())
    library = load_remediation_library(library_path)
    assert "common.remediate_fragmented_sentences" in library
