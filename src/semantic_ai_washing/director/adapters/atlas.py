"""Read-only Atlas metadata adapter.

This adapter intentionally captures only metadata (tab title/url/history timestamps)
and does not attempt chat transcript extraction.
"""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any

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


def _atlas_cli_path() -> str:
    code_home = os.getenv("CODEX_HOME", os.path.expanduser("~/.codex"))
    return os.getenv(
        "ATLAS_CLI", os.path.join(code_home, "skills", "atlas", "scripts", "atlas_cli.py")
    )


def _run_atlas_command(args: list[str]) -> tuple[bool, str]:
    cmd = ["uv", "run", "--python", "3.12", "python", _atlas_cli_path()] + args
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
        return True, out
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        return False, str(exc)


def fetch_atlas_metadata(search_term: str = "", limit: int = 20) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "captured_at": now_utc_iso(),
        "search_term": search_term,
        "limit": limit,
        "app_name": "",
        "tabs": [],
        "history": [],
        "notes": [],
    }

    ok, app_name_raw = _run_atlas_command(["app-name"])
    if ok:
        metadata["app_name"] = app_name_raw.strip().splitlines()[-1]
    else:
        metadata["notes"].append("atlas app-name unavailable")

    ok, tabs_raw = _run_atlas_command(["tabs", "--json"])
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
    ok, history_raw = _run_atlas_command(history_args)
    if ok:
        parsed = _parse_json_blob(history_raw)
        if parsed is not None:
            metadata["history"] = parsed
        else:
            metadata["notes"].append("atlas history JSON parse failed")
    else:
        metadata["notes"].append("atlas history unavailable")

    return metadata
