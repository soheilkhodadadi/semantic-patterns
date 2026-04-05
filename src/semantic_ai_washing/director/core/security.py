"""Compatibility re-exports for director security helpers.

The shared implementations now live in ``semantic_ai_washing.labcore.security``.
This module remains as a compatibility shim so existing director imports do not
break during the staged migration.
"""

from semantic_ai_washing.labcore.security import (
    KEY_PATTERNS,
    redact_secrets,
    scan_repo_for_secrets,
    scan_text_for_secrets,
)
from semantic_ai_washing.labcore.security import (
    ensure_api_key_if_enabled as _ensure_api_key_if_enabled,
)


def ensure_openai_key_if_enabled(llm_enabled: bool) -> tuple[bool, str]:
    """Preserve the director-facing OpenAI key validation contract."""

    return _ensure_api_key_if_enabled(
        llm_enabled,
        env_var="OPENAI_API_KEY",
        pattern_key="openai_api_key",
        disabled_message="LLM refinement disabled in cost_policy.yaml",
        missing_message="OPENAI_API_KEY is required when llm_enabled=true",
        invalid_message="OPENAI_API_KEY is present but does not match expected pattern",
        present_message="OPENAI_API_KEY present",
    )


__all__ = [
    "KEY_PATTERNS",
    "ensure_openai_key_if_enabled",
    "redact_secrets",
    "scan_repo_for_secrets",
    "scan_text_for_secrets",
]
