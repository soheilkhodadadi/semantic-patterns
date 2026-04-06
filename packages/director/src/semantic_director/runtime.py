"""Director-facing runtime wrappers with package-owned contracts."""

from __future__ import annotations

from typing import Any

from semantic_labcore.runtime import run_command as _run_command


def run_command(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Preserve director-facing timeout wording."""

    result = _run_command(*args, **kwargs)
    if result.get("timed_out") and isinstance(result.get("stderr"), str):
        result["stderr"] = result["stderr"].replace(
            "[runtime] command timed out",
            "[director] command timed out",
        )
    return result


__all__ = ["run_command"]
