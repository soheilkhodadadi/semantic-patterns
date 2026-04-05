from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from semantic_ai_washing.director.core.security import ensure_openai_key_if_enabled
from semantic_ai_washing.labcore.security import (
    KEY_PATTERNS,
    ensure_api_key_if_enabled,
    redact_secrets,
    scan_repo_for_secrets,
    scan_text_for_secrets,
    tracked_files,
)


def test_redact_and_scan_text_for_secrets() -> None:
    text = "token sk-proj-abcdefghijklmnopqrstuvwxyz12345 is present"

    redacted = redact_secrets(text)
    matches = scan_text_for_secrets(text)

    assert "sk-proj-" not in redacted
    assert "[REDACTED_SECRET]" in redacted
    assert len(matches) == 1
    assert matches[0]["pattern"] == "openai_api_key"
    assert matches[0]["match"] == "[REDACTED_SECRET]"


def test_tracked_files_and_repo_scan_detect_secret(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    tracked = repo / "tracked.txt"
    tracked.write_text(
        "keep sk-proj-abcdefghijklmnopqrstuvwxyz12345 hidden\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "tracked.txt"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "add tracked file"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    files = list(tracked_files(repo))
    findings = scan_repo_for_secrets(repo)

    assert files == ["tracked.txt"]
    assert len(findings) == 1
    assert findings[0]["path"] == "tracked.txt"
    assert findings[0]["pattern"] == "openai_api_key"
    assert "[REDACTED_SECRET]" in findings[0]["snippet"]


def test_generic_api_key_validator_and_director_shim(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    ok, message = ensure_api_key_if_enabled(
        False,
        env_var="OPENAI_API_KEY",
        pattern_key="openai_api_key",
        disabled_message="disabled",
        missing_message="missing",
        invalid_message="invalid",
        present_message="present",
    )
    assert (ok, message) == (True, "disabled")

    ok, message = ensure_openai_key_if_enabled(True)
    assert (ok, message) == (False, "OPENAI_API_KEY is required when llm_enabled=true")

    monkeypatch.setenv("OPENAI_API_KEY", "not-a-real-key")
    ok, message = ensure_openai_key_if_enabled(True)
    assert (ok, message) == (
        False,
        "OPENAI_API_KEY is present but does not match expected pattern",
    )

    monkeypatch.setenv("OPENAI_API_KEY", "sk-proj-abcdefghijklmnopqrstuvwxyz12345")
    ok, message = ensure_openai_key_if_enabled(True)
    assert (ok, message) == (True, "OPENAI_API_KEY present")


def test_key_patterns_include_expected_public_keys() -> None:
    assert "openai_api_key" in KEY_PATTERNS
    assert "anthropic_api_key" in KEY_PATTERNS
