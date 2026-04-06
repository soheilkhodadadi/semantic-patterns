from __future__ import annotations

from semantic_director.api_assistive import (
    parse_assistive_response_text,
    validate_assistive_response_payload,
)
from semantic_director.schemas import ApiAssistivePolicy


def _policy() -> ApiAssistivePolicy:
    return ApiAssistivePolicy.model_validate(
        {
            "schema_version": "1.4.0",
            "mode": "assistive_only",
            "provider": "openai",
            "transport": "responses_api",
            "env_var": "OPENAI_API_KEY",
            "model": "gpt-5-mini",
            "request": {
                "store": False,
                "timeout_seconds": 60,
                "max_output_tokens": 200,
            },
            "budget": {
                "max_live_requests_per_run": 1,
                "max_prompt_tokens_per_call": 1200,
                "max_output_tokens_per_call": 200,
                "max_estimated_cost_usd_per_run": 0.1,
            },
            "selection": {
                "sample_input": "data/sample.csv",
                "report_path": "reports/api/report.json",
                "timeout_seconds": 60,
                "store": False,
                "max_output_tokens": 200,
                "min_tokens": 12,
                "max_tokens": 120,
                "require_fragment_score_max": 0.0,
            },
            "telemetry": {
                "usage_file": "director/runs/cost_usage.jsonl",
                "component": "api_assistive_smoke_test",
                "cache_allowed": False,
            },
            "usage_policy": {
                "canonical": False,
                "allowed_use_cases": ["rubric_check"],
                "prohibited_use_cases": ["canonical_training_labels"],
            },
            "prompt_spec": {
                "schema_version": "1.4.0",
                "reference_rubric_path": "docs/labeling_protocol.md",
                "label_set": ["Actionable", "Speculative", "Irrelevant"],
                "confidence_bands": ["high", "medium", "low"],
                "system_prompt": "Return JSON only.",
                "user_prompt_template": "Label this sentence.",
            },
            "smoke_output": {"report_path": "reports/api/api_bootstrap_smoke_test.json"},
        }
    )


def test_parse_assistive_response_text_accepts_fenced_json() -> None:
    payload = parse_assistive_response_text(
        '```json\n{"label":"Actionable","confidence":"high","rationale":"Now in use.","assistive_only":true}\n```'
    )

    assert payload["label"] == "Actionable"
    assert payload["assistive_only"] is True


def test_validate_assistive_response_payload_normalizes_valid_payload() -> None:
    payload = validate_assistive_response_payload(
        {
            "label": "Actionable",
            "confidence": "high",
            "rationale": "Current operational use.",
            "assistive_only": True,
        },
        _policy(),
    )

    assert payload == {
        "label": "Actionable",
        "confidence": "high",
        "rationale": "Current operational use.",
        "assistive_only": True,
    }
