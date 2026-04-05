"""Project-agnostic secret scanning and redaction helpers."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Iterable

KEY_PATTERNS: dict[str, re.Pattern[str]] = {
    "openai_api_key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    "anthropic_api_key": re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b"),
}


def redact_secrets(text: str) -> str:
    """Replace detected secret-like tokens with a stable redaction marker."""

    redacted = text
    for pattern in KEY_PATTERNS.values():
        redacted = pattern.sub("[REDACTED_SECRET]", redacted)
    return redacted


def scan_text_for_secrets(text: str) -> list[dict[str, str]]:
    """Return matched secret patterns from a text fragment."""

    matches: list[dict[str, str]] = []
    for name, pattern in KEY_PATTERNS.items():
        for found in pattern.findall(text):
            matches.append({"pattern": name, "match": redact_secrets(found)})
    return matches


def tracked_files(repo_root: str | Path) -> Iterable[str]:
    """Return tracked git file paths relative to the repository root."""

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


def scan_repo_for_secrets(
    repo_root: str | Path,
    max_file_bytes: int = 2_000_000,
) -> list[dict[str, str]]:
    """Scan tracked text files in a repo for secret-like patterns."""

    findings: list[dict[str, str]] = []
    for rel_path in tracked_files(repo_root):
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


def ensure_api_key_if_enabled(
    enabled: bool,
    *,
    env_var: str,
    pattern_key: str,
    disabled_message: str,
    missing_message: str,
    invalid_message: str,
    present_message: str,
) -> tuple[bool, str]:
    """Validate a provider-specific API key only when the capability is enabled."""

    if not enabled:
        return True, disabled_message

    key = os.getenv(env_var, "").strip()
    if not key:
        return False, missing_message

    pattern = KEY_PATTERNS[pattern_key]
    if not pattern.search(key):
        return False, invalid_message
    return True, present_message
