"""Compatibility re-exports for shared Responses API helpers.

The canonical implementation now lives in ``semantic_labcore.openai_responses``.
This module remains as a transition shim so existing
``semantic_ai_washing.labcore.openai_responses`` imports keep working while the
workspace package becomes authoritative.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PACKAGE_SRC = Path(__file__).resolve().parents[3] / "packages" / "labcore" / "src"
if _PACKAGE_SRC.exists():
    package_src = str(_PACKAGE_SRC)
    if package_src not in sys.path:
        sys.path.insert(0, package_src)

import semantic_labcore.openai_responses as _impl  # noqa: E402

OPENAI_RESPONSES_URL = _impl.OPENAI_RESPONSES_URL
OpenAIResponsesError = _impl.OpenAIResponsesError
OpenAIResponsesHTTPError = _impl.OpenAIResponsesHTTPError
call_responses_api = _impl.call_responses_api
extract_response_text = _impl.extract_response_text
urllib = _impl.urllib
http = _impl.http
time = _impl.time

__all__ = [
    "OPENAI_RESPONSES_URL",
    "OpenAIResponsesError",
    "OpenAIResponsesHTTPError",
    "call_responses_api",
    "extract_response_text",
]
