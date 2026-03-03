"""Shared utilities for director core modules."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: str | Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def run_command(
    command: str,
    cwd: str = ".",
    timeout_seconds: int = 1800,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Run a shell command and return normalized execution details."""
    started_at = now_utc_iso()
    resolved_cwd = str(Path(cwd).resolve())
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    try:
        completed = subprocess.run(
            command,
            shell=True,
            cwd=resolved_cwd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
            env=merged_env,
        )
        timed_out = False
        exit_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        exit_code = 124
        stdout = exc.stdout or ""
        stderr = (exc.stderr or "") + "\n[director] command timed out"

    return {
        "command": command,
        "cwd": resolved_cwd,
        "started_at": started_at,
        "finished_at": now_utc_iso(),
        "exit_code": exit_code,
        "timed_out": timed_out,
        "stdout": stdout,
        "stderr": stderr,
    }


def load_json(path: str | Path, default: Any = None) -> Any:
    p = Path(path)
    if not p.exists():
        return default
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(path: str | Path, payload: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=False)


def git_info(repo_root: str = ".") -> dict[str, Any]:
    def _run(args: list[str]) -> str:
        try:
            return subprocess.check_output(
                args, cwd=repo_root, text=True, stderr=subprocess.DEVNULL
            ).strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return ""

    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"]) or "unknown"
    commit = _run(["git", "rev-parse", "HEAD"]) or "unknown"
    dirty_output = _run(["git", "status", "--porcelain"])
    return {
        "branch": branch,
        "commit": commit,
        "dirty": bool(dirty_output),
    }


def repository_root(start: str = ".") -> str:
    """Best effort repository root detection."""
    current = Path(start).resolve()
    for candidate in [current] + list(current.parents):
        if (candidate / ".git").exists():
            return str(candidate)
    return os.getcwd()
