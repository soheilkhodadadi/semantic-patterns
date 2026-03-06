"""Configuration and path loading for the director package."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from semantic_ai_washing.director.core.utils import ensure_dir


@dataclass(frozen=True)
class DirectorPaths:
    repo_root: Path
    director_root: Path
    config_dir: Path
    model_dir: Path
    snapshots_dir: Path
    plans_dir: Path
    optimization_dir: Path
    reviews_dir: Path
    runs_dir: Path
    decisions_dir: Path
    cache_dir: Path


DEFAULT_CONFIG = {
    "project_profile": {
        "project_name": "semantic-patterns",
        "iteration_log": "docs/iteration_log.md",
        "roadmap_model_path": "director/model/roadmap_model.yaml",
        "remediation_library_path": "director/model/remediation_library.yaml",
        "tooling_policy_path": "director/config/tooling_policy.yaml",
        "canonical_validation_commands": [
            "make bootstrap",
            "make doctor",
            "make format",
            "make lint",
            ".venv/bin/pytest -q",
        ],
        "optimization_weights": {
            "unblock_value": 5,
            "critical_path_depth": 4,
            "risk_reduction": 3,
            "automation_bonus": 2,
            "manual_effort_penalty": 2,
            "precondition_gap_penalty": 4,
            "quality_failure_penalty": 5,
        },
        "feature_flags": {
            "use_task_graph_planner": True,
            "emit_roadmap_patch": True,
        },
        "phase_command_map": {},
    },
    "autonomy_policy": {
        "mode": "autonomous",
        "require_explicit_recovery_selection": True,
        "halt_on_escalation_required": True,
        "allow_policy_sensitive_autorun": False,
    },
    "cost_policy": {
        "llm_enabled": False,
        "model": "gpt-5-mini",
        "max_tokens_per_run": 15000,
        "max_cost_usd_per_run": 2.0,
        "max_prompt_tokens_per_call": 4000,
        "max_completion_tokens_per_call": 1200,
        "price_per_1k_prompt_tokens_usd": 0.0,
        "price_per_1k_completion_tokens_usd": 0.0,
    },
    "tooling_policy": {
        "policies": [
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
        ]
    },
}


def get_director_paths(repo_root: str = ".") -> DirectorPaths:
    root = Path(repo_root).resolve()
    director_root = root / "director"
    return DirectorPaths(
        repo_root=root,
        director_root=director_root,
        config_dir=director_root / "config",
        model_dir=director_root / "model",
        snapshots_dir=director_root / "snapshots",
        plans_dir=director_root / "plans",
        optimization_dir=director_root / "optimization",
        reviews_dir=director_root / "reviews",
        runs_dir=director_root / "runs",
        decisions_dir=director_root / "decisions",
        cache_dir=director_root / "cache",
    )


def ensure_director_dirs(paths: DirectorPaths) -> None:
    ensure_dir(paths.director_root)
    ensure_dir(paths.config_dir)
    ensure_dir(paths.model_dir)
    ensure_dir(paths.snapshots_dir)
    ensure_dir(paths.plans_dir)
    ensure_dir(paths.optimization_dir)
    ensure_dir(paths.reviews_dir)
    ensure_dir(paths.runs_dir)
    ensure_dir(paths.decisions_dir)
    ensure_dir(paths.cache_dir)


def _yaml_load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML object in {path}")
    return data


def _yaml_dump(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False)


def ensure_default_configs(paths: DirectorPaths) -> None:
    files = {
        "project_profile": paths.config_dir / "project_profile.yaml",
        "autonomy_policy": paths.config_dir / "autonomy_policy.yaml",
        "cost_policy": paths.config_dir / "cost_policy.yaml",
        "tooling_policy": paths.config_dir / "tooling_policy.yaml",
    }
    for key, file_path in files.items():
        if not file_path.exists():
            _yaml_dump(file_path, DEFAULT_CONFIG[key])

    roadmap_model = paths.model_dir / "roadmap_model.yaml"
    if not roadmap_model.exists():
        _yaml_dump(
            roadmap_model,
            {
                "schema_version": "1.2.0",
                "project": {
                    "name": "semantic-patterns",
                    "description": "Canonical machine-readable roadmap model.",
                },
                "settings": {
                    "active_horizon_iterations": ["1", "2"],
                    "optimizer_weights": DEFAULT_CONFIG["project_profile"]["optimization_weights"],
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
                "policies": [],
                "data_layers": [],
                "source_windows": [],
                "tooling_policies": [],
                "iterations": [],
            },
        )

    remediation_library = paths.model_dir / "remediation_library.yaml"
    if not remediation_library.exists():
        _yaml_dump(
            remediation_library,
            {
                "schema_version": "1.2.0",
                "tasks": [],
            },
        )


def load_configs(paths: DirectorPaths) -> dict[str, Any]:
    ensure_director_dirs(paths)
    ensure_default_configs(paths)

    project_profile = _yaml_load(paths.config_dir / "project_profile.yaml")
    autonomy_policy = _yaml_load(paths.config_dir / "autonomy_policy.yaml")
    cost_policy = _yaml_load(paths.config_dir / "cost_policy.yaml")
    tooling_policy = _yaml_load(paths.config_dir / "tooling_policy.yaml")
    return {
        "project_profile": {**DEFAULT_CONFIG["project_profile"], **project_profile},
        "autonomy_policy": {**DEFAULT_CONFIG["autonomy_policy"], **autonomy_policy},
        "cost_policy": {**DEFAULT_CONFIG["cost_policy"], **cost_policy},
        "tooling_policy": {**DEFAULT_CONFIG["tooling_policy"], **tooling_policy},
    }


def required_file_paths(paths: DirectorPaths) -> list[Path]:
    return [
        paths.config_dir / "project_profile.yaml",
        paths.config_dir / "autonomy_policy.yaml",
        paths.config_dir / "cost_policy.yaml",
        paths.config_dir / "tooling_policy.yaml",
        paths.snapshots_dir / "protocol_summary.json",
        paths.snapshots_dir / "roadmap_summary.json",
        paths.snapshots_dir / "iteration_state.json",
        paths.model_dir / "roadmap_model.yaml",
        paths.model_dir / "remediation_library.yaml",
    ]
