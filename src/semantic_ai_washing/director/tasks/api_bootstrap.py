"""Compatibility shim for the package-owned API bootstrap task."""

from semantic_director.api_bootstrap import DEFAULT_COST_POLICY, DEFAULT_POLICY, main, parse_args
from semantic_director.api_bootstrap import (
    OpenAIResponsesError,
    OpenAIResponsesHTTPError,
    call_responses_api,
    extract_response_text,
    run_api_bootstrap,
)

__all__ = [
    "DEFAULT_COST_POLICY",
    "DEFAULT_POLICY",
    "OpenAIResponsesError",
    "OpenAIResponsesHTTPError",
    "call_responses_api",
    "extract_response_text",
    "parse_args",
    "run_api_bootstrap",
    "main",
]
