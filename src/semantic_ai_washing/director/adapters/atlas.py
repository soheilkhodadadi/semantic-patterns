"""Read-only Atlas metadata adapter.

This adapter intentionally captures only metadata (tab title/url/history timestamps)
and does not attempt chat transcript extraction.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import yaml

from semantic_ai_washing.director.core.utils import now_utc_iso


def _parse_json_blob(raw: str) -> Any | None:
    raw = raw.strip()
    if not raw:
        return None
    for marker in ("[", "{"):
        idx = raw.find(marker)
        if idx >= 0:
            candidate = raw[idx:]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
    return None


def _load_tooling_policy(repo_root: str | None) -> dict[str, Any]:
    if not repo_root:
        return {}
    policy_path = Path(repo_root) / "director" / "config" / "tooling_policy.yaml"
    if not policy_path.exists():
        return {}
    payload = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        return {}
    return payload


def _atlas_policy(repo_root: str | None) -> dict[str, Any]:
    policies = _load_tooling_policy(repo_root).get("policies", [])
    for policy in policies:
        if isinstance(policy, dict) and policy.get("tool") == "atlas":
            return policy
    return {}


def _atlas_cli_path(policy: dict[str, Any]) -> str:
    code_home = os.getenv("CODEX_HOME", os.path.expanduser("~/.codex"))
    configured = policy.get("required_runner") if isinstance(policy, dict) else ""
    runner = configured or os.getenv(
        "ATLAS_CLI", os.path.join(code_home, "skills", "atlas", "scripts", "atlas_cli.py")
    )
    return os.path.expanduser(runner)


def _atlas_wrapper_path(policy: dict[str, Any], repo_root: str | None) -> str:
    wrapper = policy.get("wrapper_path", "") if isinstance(policy, dict) else ""
    if not wrapper or not repo_root:
        return ""
    candidate = Path(wrapper)
    if candidate.is_absolute():
        return str(candidate)
    return str((Path(repo_root) / candidate).resolve())


def _run_atlas_command(args: list[str], repo_root: str | None = None) -> tuple[bool, str]:
    policy = _atlas_policy(repo_root)
    wrapper = _atlas_wrapper_path(policy, repo_root)
    atlas_cli = _atlas_cli_path(policy)

    if wrapper and Path(wrapper).exists():
        cmd = [wrapper, atlas_cli] + args
    else:
        cmd = ["uv", "run", "--python", "3.12", "python", atlas_cli] + args

    env = os.environ.copy()
    env["ATLAS_CLI"] = atlas_cli

    try:
        with tempfile.TemporaryDirectory(prefix="atlas-isolated-") as temp_dir:
            out = subprocess.check_output(
                cmd,
                text=True,
                stderr=subprocess.STDOUT,
                cwd=temp_dir,
                env=env,
            )
        return True, out
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        return False, str(exc)


def fetch_atlas_metadata(
    search_term: str = "",
    limit: int = 20,
    repo_root: str | None = None,
) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "captured_at": now_utc_iso(),
        "search_term": search_term,
        "limit": limit,
        "app_name": "",
        "tabs": [],
        "history": [],
        "notes": [],
    }

    ok, app_name_raw = _run_atlas_command(["app-name"], repo_root=repo_root)
    if ok:
        metadata["app_name"] = app_name_raw.strip().splitlines()[-1]
    else:
        metadata["notes"].append("atlas app-name unavailable")

    ok, tabs_raw = _run_atlas_command(["tabs", "--json"], repo_root=repo_root)
    if ok:
        parsed = _parse_json_blob(tabs_raw)
        if parsed is not None:
            metadata["tabs"] = parsed
        else:
            metadata["notes"].append("atlas tabs JSON parse failed")
    else:
        metadata["notes"].append("atlas tabs unavailable")

    history_args = ["history", "--limit", str(limit), "--json"]
    if search_term:
        history_args = ["history", "--search", search_term, "--limit", str(limit), "--json"]
    ok, history_raw = _run_atlas_command(history_args, repo_root=repo_root)
    if ok:
        parsed = _parse_json_blob(history_raw)
        if parsed is not None:
            metadata["history"] = parsed
        else:
            metadata["notes"].append("atlas history JSON parse failed")
    else:
        metadata["notes"].append("atlas history unavailable")

    return metadata
