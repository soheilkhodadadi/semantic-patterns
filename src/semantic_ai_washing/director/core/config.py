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
    snapshots_dir: Path
    plans_dir: Path
    runs_dir: Path
    decisions_dir: Path
    cache_dir: Path


DEFAULT_CONFIG = {
    "project_profile": {
        "project_name": "semantic-patterns",
        "iteration_log": "docs/iteration_log.md",
        "canonical_validation_commands": [
            "make bootstrap",
            "make doctor",
            "make format",
            "make lint",
            ".venv/bin/pytest -q",
        ],
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
}


def get_director_paths(repo_root: str = ".") -> DirectorPaths:
    root = Path(repo_root).resolve()
    director_root = root / "director"
    return DirectorPaths(
        repo_root=root,
        director_root=director_root,
        config_dir=director_root / "config",
        snapshots_dir=director_root / "snapshots",
        plans_dir=director_root / "plans",
        runs_dir=director_root / "runs",
        decisions_dir=director_root / "decisions",
        cache_dir=director_root / "cache",
    )


def ensure_director_dirs(paths: DirectorPaths) -> None:
    ensure_dir(paths.director_root)
    ensure_dir(paths.config_dir)
    ensure_dir(paths.snapshots_dir)
    ensure_dir(paths.plans_dir)
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
    }
    for key, file_path in files.items():
        if not file_path.exists():
            _yaml_dump(file_path, DEFAULT_CONFIG[key])


def load_configs(paths: DirectorPaths) -> dict[str, Any]:
    ensure_director_dirs(paths)
    ensure_default_configs(paths)

    project_profile = _yaml_load(paths.config_dir / "project_profile.yaml")
    autonomy_policy = _yaml_load(paths.config_dir / "autonomy_policy.yaml")
    cost_policy = _yaml_load(paths.config_dir / "cost_policy.yaml")
    return {
        "project_profile": {**DEFAULT_CONFIG["project_profile"], **project_profile},
        "autonomy_policy": {**DEFAULT_CONFIG["autonomy_policy"], **autonomy_policy},
        "cost_policy": {**DEFAULT_CONFIG["cost_policy"], **cost_policy},
    }


def required_file_paths(paths: DirectorPaths) -> list[Path]:
    return [
        paths.config_dir / "project_profile.yaml",
        paths.config_dir / "autonomy_policy.yaml",
        paths.config_dir / "cost_policy.yaml",
        paths.snapshots_dir / "protocol_summary.json",
        paths.snapshots_dir / "roadmap_summary.json",
        paths.snapshots_dir / "iteration_state.json",
    ]
