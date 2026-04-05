"""Compatibility re-exports for director runtime helpers.

The shared implementations now live in ``semantic_ai_washing.labcore.runtime``.
This module remains as a compatibility shim so existing director imports do not
break during the staged migration.
"""

from typing import Any

from semantic_ai_washing.labcore.runtime import (
    dump_json,
    ensure_dir,
    git_info,
    load_json,
    now_utc_iso,
    repository_root,
    sha256_file,
    sha256_text,
)
from semantic_ai_washing.labcore.runtime import run_command as _run_command


def run_command(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Preserve director-facing timeout wording during the migration."""

    result = _run_command(*args, **kwargs)
    if result.get("timed_out") and isinstance(result.get("stderr"), str):
        result["stderr"] = result["stderr"].replace(
            "[runtime] command timed out",
            "[director] command timed out",
        )
    return result


__all__ = [
    "dump_json",
    "ensure_dir",
    "git_info",
    "load_json",
    "now_utc_iso",
    "repository_root",
    "run_command",
    "sha256_file",
    "sha256_text",
]
