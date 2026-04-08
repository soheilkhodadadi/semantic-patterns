"""Compatibility shim for the member-owned preliminary benchmark matrix helpers."""

import ai_washing_member.classification.benchmark_preliminary_models as _member
from ai_washing_member.classification.benchmark_preliminary_models import (
    main,
    parse_args,
    predict_sentences,
    run_benchmark,
)

__all__ = ["predict_sentences", "run_benchmark", "parse_args", "main"]

member = _member


if __name__ == "__main__":
    main()
