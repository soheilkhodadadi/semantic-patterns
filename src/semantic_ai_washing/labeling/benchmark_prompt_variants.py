"""Compatibility shim for the member-owned prompt benchmark helpers."""

from ai_washing_member.labeling import benchmark_prompt_variants as _member

DEFAULT_INPUT = _member.DEFAULT_INPUT
DEFAULT_BENCHMARK = _member.DEFAULT_BENCHMARK
DEFAULT_POLICY = _member.DEFAULT_POLICY
DEFAULT_VARIANTS = _member.DEFAULT_VARIANTS
DEFAULT_COST_POLICY = _member.DEFAULT_COST_POLICY
DEFAULT_REPORT_JSON = _member.DEFAULT_REPORT_JSON
DEFAULT_REPORT_MD = _member.DEFAULT_REPORT_MD
DEFAULT_FULL_INPUT = _member.DEFAULT_FULL_INPUT
DEFAULT_FULL_OUTPUT = _member.DEFAULT_FULL_OUTPUT
DEFAULT_FULL_FILLED = _member.DEFAULT_FULL_FILLED
DEFAULT_FULL_REPORT = _member.DEFAULT_FULL_REPORT
DEFAULT_VERSION = _member.DEFAULT_VERSION
REQUIRED_GATE_OVERALL = _member.REQUIRED_GATE_OVERALL
REQUIRED_GATE_ACTION_SPEC = _member.REQUIRED_GATE_ACTION_SPEC
generate_assistive_prelabels = _member.generate_assistive_prelabels


def benchmark_prompt_variants(*args, **kwargs):
    _member.generate_assistive_prelabels = generate_assistive_prelabels
    return _member.benchmark_prompt_variants(*args, **kwargs)


def parse_args():
    return _member.parse_args()


def main() -> int:
    _member.generate_assistive_prelabels = generate_assistive_prelabels
    return _member.main()


__all__ = [
    "DEFAULT_INPUT",
    "DEFAULT_BENCHMARK",
    "DEFAULT_POLICY",
    "DEFAULT_VARIANTS",
    "DEFAULT_COST_POLICY",
    "DEFAULT_REPORT_JSON",
    "DEFAULT_REPORT_MD",
    "DEFAULT_FULL_INPUT",
    "DEFAULT_FULL_OUTPUT",
    "DEFAULT_FULL_FILLED",
    "DEFAULT_FULL_REPORT",
    "DEFAULT_VERSION",
    "REQUIRED_GATE_OVERALL",
    "REQUIRED_GATE_ACTION_SPEC",
    "generate_assistive_prelabels",
    "benchmark_prompt_variants",
    "main",
    "parse_args",
]
