from __future__ import annotations

import pytest

from semantic_director.security import ensure_openai_key_if_enabled, scan_text_for_secrets


def test_scan_text_for_secrets_redacts_openai_key() -> None:
    findings = scan_text_for_secrets(
        "token sk-proj-abcdefghijklmnopqrstuvwxyz12345 should not leak"
    )

    assert len(findings) == 1
    assert findings[0]["pattern"] == "openai_api_key"
    assert findings[0]["match"] == "[REDACTED_SECRET]"


def test_director_security_contract_preserves_openai_key_messages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
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
