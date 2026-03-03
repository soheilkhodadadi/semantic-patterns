"""State compiler for current repository + iteration snapshots."""

from __future__ import annotations

import glob
from pathlib import Path
from typing import Any

from semantic_ai_washing.director.core.utils import dump_json, git_info, load_json, now_utc_iso


def _collect_validation_reports(repo_root: str) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    patterns = [
        "reports/iteration*/phase*/**/*report*.json",
        "reports/iteration*/phase*/**/*metrics*.json",
        "reports/iteration*/phase*/**/*qa*.json",
    ]
    seen: set[str] = set()
    for pattern in patterns:
        for path in glob.glob(str(Path(repo_root) / pattern), recursive=True):
            if path in seen:
                continue
            seen.add(path)
            payload = load_json(path, default=None)
            if payload is None:
                continue
            reports.append({"path": path, "payload": payload})
    return reports


class StateCompiler:
    def __init__(self, repo_root: str = "."):
        self.repo_root = repo_root

    def compile(self, iteration_state_path: str, output_path: str | None = None) -> dict[str, Any]:
        iteration_state = load_json(iteration_state_path, default={}) or {}
        git_meta = git_info(self.repo_root)
        reports = _collect_validation_reports(self.repo_root)

        last_gate = iteration_state.get("last_successful_gate", "unknown")
        for item in reversed(reports):
            payload = item["payload"]
            status = None
            if isinstance(payload, dict):
                if isinstance(payload.get("summary"), dict):
                    status = payload["summary"].get("status")
                status = status or payload.get("status")
            if status == "pass":
                last_gate = f"pass:{item['path']}"
                break
            if status == "fail":
                last_gate = f"fail:{item['path']}"
                break

        compiled = {
            "compiled_at": now_utc_iso(),
            "git": git_meta,
            "iteration_snapshot": iteration_state,
            "validation_reports": reports,
            "last_gate_status": last_gate,
            "active_iteration": _active_iteration(iteration_state),
        }

        if output_path:
            dump_json(output_path, compiled)
        return compiled


def _active_iteration(iteration_state: dict[str, Any]) -> str:
    items = iteration_state.get("iterations", []) if isinstance(iteration_state, dict) else []
    if not items:
        return "unknown"
    try:
        latest = max(items, key=lambda item: int(item.get("iteration_id", 0) or 0))
    except ValueError:
        return "unknown"
    return str(latest.get("iteration_id", "unknown"))
