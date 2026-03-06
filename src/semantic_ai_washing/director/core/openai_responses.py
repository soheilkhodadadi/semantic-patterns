"""Shared lightweight OpenAI Responses API transport helpers."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"


class OpenAIResponsesError(RuntimeError):
    """Base error for lightweight Responses API interactions."""


class OpenAIResponsesHTTPError(OpenAIResponsesError):
    """HTTP failure with normalized metadata."""

    def __init__(self, status_code: int, message: str, response_body: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


def extract_response_text(payload: dict[str, Any]) -> str:
    """Extract plain text from a Responses API payload."""
    if isinstance(payload.get("output_text"), str) and payload["output_text"].strip():
        return payload["output_text"].strip()

    output = payload.get("output", [])
    chunks: list[str] = []
    for item in output:
        for content in item.get("content", []):
            text = content.get("text")
            if text:
                chunks.append(text)
    return "\n".join(chunks).strip()


def call_responses_api(
    *,
    model: str,
    input_payload: list[dict[str, Any]],
    api_key: str | None = None,
    max_output_tokens: int = 200,
    timeout_seconds: int = 60,
    store: bool = False,
    extra_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Call the OpenAI Responses API and return decoded JSON."""
    resolved_api_key = (api_key or os.getenv("OPENAI_API_KEY", "")).strip()
    if not resolved_api_key:
        raise OpenAIResponsesError("OPENAI_API_KEY missing")

    request_payload: dict[str, Any] = {
        "model": model,
        "input": input_payload,
        "max_output_tokens": max_output_tokens,
        "store": store,
    }
    if extra_payload:
        request_payload.update(extra_payload)

    req = urllib.request.Request(
        OPENAI_RESPONSES_URL,
        data=json.dumps(request_payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {resolved_api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        response_body = exc.read().decode("utf-8", errors="replace")
        raise OpenAIResponsesHTTPError(
            status_code=int(exc.code),
            message=f"Responses API HTTP error: {exc.code}",
            response_body=response_body,
        ) from exc
    except urllib.error.URLError as exc:
        raise OpenAIResponsesError(f"Responses API network error: {exc.reason}") from exc
    except TimeoutError as exc:
        raise OpenAIResponsesError("Responses API request timed out") from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise OpenAIResponsesError("Responses API returned invalid JSON payload") from exc

    if not isinstance(payload, dict):
        raise OpenAIResponsesError("Responses API payload is not a JSON object")
    return payload
