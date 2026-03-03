"""Secret guardrails and redaction helpers."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Iterable

KEY_PATTERNS: dict[str, re.Pattern[str]] = {
    "openai_api_key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    "anthropic_api_key": re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b"),
}


def redact_secrets(text: str) -> str:
    redacted = text
    for pattern in KEY_PATTERNS.values():
        redacted = pattern.sub("[REDACTED_SECRET]", redacted)
    return redacted


def scan_text_for_secrets(text: str) -> list[dict[str, str]]:
    matches: list[dict[str, str]] = []
    for name, pattern in KEY_PATTERNS.items():
        for found in pattern.findall(text):
            matches.append({"pattern": name, "match": redact_secrets(found)})
    return matches


def _tracked_files(repo_root: str) -> Iterable[str]:
    try:
        out = subprocess.check_output(
            ["git", "ls-files"],
            cwd=repo_root,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]


def scan_repo_for_secrets(repo_root: str, max_file_bytes: int = 2_000_000) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for rel_path in _tracked_files(repo_root):
        path = Path(repo_root) / rel_path
        if not path.exists() or path.is_dir():
            continue
        if path.stat().st_size > max_file_bytes:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        except OSError:
            continue

        for idx, line in enumerate(text.splitlines(), start=1):
            for item in scan_text_for_secrets(line):
                findings.append(
                    {
                        "path": rel_path,
                        "line": str(idx),
                        "pattern": item["pattern"],
                        "snippet": redact_secrets(line.strip())[:220],
                    }
                )
    return findings


def ensure_openai_key_if_enabled(llm_enabled: bool) -> tuple[bool, str]:
    if not llm_enabled:
        return True, "LLM refinement disabled in cost_policy.yaml"

    import os

    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return False, "OPENAI_API_KEY is required when llm_enabled=true"
    if not KEY_PATTERNS["openai_api_key"].search(key):
        return False, "OPENAI_API_KEY is present but does not match expected pattern"
    return True, "OPENAI_API_KEY present"
