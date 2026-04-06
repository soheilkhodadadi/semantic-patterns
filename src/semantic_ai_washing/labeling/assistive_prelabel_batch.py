"""Compatibility shim for the member-owned assistive prelabel helpers."""

from ai_washing_member.labeling import assistive_prelabel_batch as _member
from semantic_labcore.openai_responses import call_responses_api, extract_response_text

DEFAULT_INPUT = _member.DEFAULT_INPUT
DEFAULT_OUTPUT = _member.DEFAULT_OUTPUT
DEFAULT_REPORT = _member.DEFAULT_REPORT
DEFAULT_POLICY = _member.DEFAULT_POLICY
DEFAULT_COST_POLICY = _member.DEFAULT_COST_POLICY
ASSISTIVE_COLUMNS = _member.ASSISTIVE_COLUMNS
REQUIRED_COLUMNS = _member.REQUIRED_COLUMNS
OpenAIResponsesError = _member.OpenAIResponsesError
OpenAIResponsesHTTPError = _member.OpenAIResponsesHTTPError
_build_cost_controller = _member._build_cost_controller


def generate_assistive_prelabels(*args, **kwargs):
    _member.call_responses_api = call_responses_api
    _member.extract_response_text = extract_response_text
    _member._build_cost_controller = _build_cost_controller
    return _member.generate_assistive_prelabels(*args, **kwargs)


def parse_args():
    return _member.parse_args()


def main() -> int:
    _member.call_responses_api = call_responses_api
    _member.extract_response_text = extract_response_text
    _member._build_cost_controller = _build_cost_controller
    return _member.main()


__all__ = [
    "DEFAULT_INPUT",
    "DEFAULT_OUTPUT",
    "DEFAULT_REPORT",
    "DEFAULT_POLICY",
    "DEFAULT_COST_POLICY",
    "ASSISTIVE_COLUMNS",
    "REQUIRED_COLUMNS",
    "OpenAIResponsesError",
    "OpenAIResponsesHTTPError",
    "_build_cost_controller",
    "call_responses_api",
    "extract_response_text",
    "generate_assistive_prelabels",
    "main",
    "parse_args",
]
