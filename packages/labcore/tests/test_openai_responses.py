from __future__ import annotations

import io
import json
import urllib.error

import pytest

from semantic_labcore.openai_responses import (
    OpenAIResponsesError,
    OpenAIResponsesHTTPError,
    call_responses_api,
    extract_response_text,
)


class _FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


def test_extract_response_text_prefers_output_text() -> None:
    payload = {"output_text": "  hello world  "}
    assert extract_response_text(payload) == "hello world"


def test_extract_response_text_falls_back_to_output_chunks() -> None:
    payload = {
        "output": [
            {"content": [{"text": "alpha"}, {"text": "beta"}]},
            {"content": [{"text": "gamma"}]},
        ]
    }
    assert extract_response_text(payload) == "alpha\nbeta\ngamma"


def test_call_responses_api_success_builds_expected_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def _fake_urlopen(req, timeout):  # type: ignore[no-untyped-def]
        captured["url"] = req.full_url
        captured["timeout"] = timeout
        captured["auth"] = req.headers.get("Authorization")
        captured["content_type"] = req.get_header("Content-type")
        captured["payload"] = json.loads(req.data.decode("utf-8"))
        return _FakeResponse({"id": "resp_123", "output_text": "ok"})

    monkeypatch.setattr("semantic_labcore.openai_responses.urllib.request.urlopen", _fake_urlopen)

    payload = call_responses_api(
        model="gpt-test",
        input_payload=[{"role": "user", "content": [{"type": "input_text", "text": "hi"}]}],
        api_key="sk-proj-abcdefghijklmnopqrstuvwxyz12345",
        max_output_tokens=77,
        timeout_seconds=9,
        store=True,
        extra_payload={"metadata": {"source": "test"}},
    )

    assert payload["output_text"] == "ok"
    assert captured["timeout"] == 9
    assert captured["payload"] == {
        "model": "gpt-test",
        "input": [{"role": "user", "content": [{"type": "input_text", "text": "hi"}]}],
        "max_output_tokens": 77,
        "store": True,
        "metadata": {"source": "test"},
    }
    assert captured["auth"] == "Bearer sk-proj-abcdefghijklmnopqrstuvwxyz12345"
    assert captured["content_type"] == "application/json"


def test_call_responses_api_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(OpenAIResponsesError, match="OPENAI_API_KEY missing"):
        call_responses_api(model="gpt-test", input_payload=[])


def test_call_responses_api_normalizes_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    http_error = urllib.error.HTTPError(
        url="https://api.openai.com/v1/responses",
        code=429,
        msg="Too Many Requests",
        hdrs=None,
        fp=io.BytesIO(b'{"error":"rate limit"}'),
    )

    def _fake_urlopen(req, timeout):  # type: ignore[no-untyped-def]
        raise http_error

    monkeypatch.setattr("semantic_labcore.openai_responses.urllib.request.urlopen", _fake_urlopen)

    with pytest.raises(OpenAIResponsesHTTPError) as exc_info:
        call_responses_api(
            model="gpt-test",
            input_payload=[],
            api_key="sk-proj-abcdefghijklmnopqrstuvwxyz12345",
        )

    assert exc_info.value.status_code == 429
    assert "rate limit" in exc_info.value.response_body


def test_call_responses_api_retries_and_surfaces_network_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts = {"count": 0}

    def _fake_urlopen(req, timeout):  # type: ignore[no-untyped-def]
        attempts["count"] += 1
        raise urllib.error.URLError("network down")

    monkeypatch.setattr("semantic_labcore.openai_responses.urllib.request.urlopen", _fake_urlopen)
    monkeypatch.setattr("semantic_labcore.openai_responses.time.sleep", lambda *_: None)

    with pytest.raises(OpenAIResponsesError, match="Responses API network error: network down"):
        call_responses_api(
            model="gpt-test",
            input_payload=[],
            api_key="sk-proj-abcdefghijklmnopqrstuvwxyz12345",
            max_retries=2,
        )

    assert attempts["count"] == 3
