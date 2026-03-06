"""Deterministic condition sensors for task readiness and execution checks."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

from semantic_ai_washing.director.core.utils import sha256_file
from semantic_ai_washing.director.schemas import ConditionSpec

_JSON_TARGET_RE = re.compile(r"^(?P<path>.+?)::(?P<field>[\w\.\-]+)$")


def _resolve_target(repo_root: str, target: str) -> Path:
    candidate = Path(target)
    if candidate.is_absolute():
        return candidate
    return (Path(repo_root) / candidate).resolve()


def _compare(operator: str, left: Any, right: Any) -> bool:
    if operator == "==":
        return left == right
    if operator == "!=":
        return left != right
    if operator == ">=":
        return left >= right
    if operator == "<=":
        return left <= right
    if operator == ">":
        return left > right
    if operator == "<":
        return left < right
    if operator == "in":
        return left in right
    if operator == "not_in":
        return left not in right
    raise ValueError(f"Unsupported operator: {operator}")


def _sentence_fragment_rate(csv_path: Path) -> tuple[float, dict[str, Any]]:
    df = pd.read_csv(csv_path)
    sentence_column = next((col for col in ("sentence", "text") if col in df.columns), None)
    if sentence_column is None:
        raise ValueError(f"No sentence/text column found in {csv_path}")

    sentences = df[sentence_column].fillna("").astype(str)
    total = len(sentences)
    if total == 0:
        return 1.0, {"rows": 0, "fragment_rows": 0}

    def looks_fragmented(text: str) -> bool:
        stripped = text.strip()
        if not stripped:
            return True
        tokens = stripped.split()
        if len(tokens) < 5:
            return True
        if stripped[-1] not in ".!?":
            return True
        alpha_chars = [char for char in stripped if char.isalpha()]
        if alpha_chars and alpha_chars[0].islower():
            return True
        if re.match(r"^[\(\[]?[a-z0-9][\)\]]?\s", stripped):
            return True
        if stripped.endswith((";", ":", ",")):
            return True
        return False

    fragment_rows = int(sum(1 for sentence in sentences if looks_fragmented(sentence)))
    return fragment_rows / total, {"rows": total, "fragment_rows": fragment_rows}


def evaluate_condition(
    condition: ConditionSpec,
    repo_root: str,
) -> dict[str, Any]:
    target = condition.target
    details: dict[str, Any] = {
        "condition_id": condition.condition_id,
        "kind": condition.kind,
        "target": target,
        "operator": condition.operator,
        "expected": condition.expected,
        "on_fail": condition.on_fail,
        "reroute_to": list(condition.reroute_to),
    }

    if condition.kind in {"artifact_exists", "manual_artifact_present"}:
        resolved = _resolve_target(repo_root, target)
        actual = resolved.exists()
        passed = _compare(condition.operator, actual, bool(condition.expected))
        details.update({"actual": actual, "resolved_target": str(resolved)})
    elif condition.kind == "csv_row_count_gte":
        resolved = _resolve_target(repo_root, target)
        if not resolved.exists():
            actual = 0
        else:
            actual = len(pd.read_csv(resolved))
        passed = _compare(condition.operator, actual, condition.expected)
        details.update({"actual": actual, "resolved_target": str(resolved)})
    elif condition.kind == "json_field_compare":
        match = _JSON_TARGET_RE.match(target)
        if not match:
            raise ValueError(f"Invalid json_field_compare target: {target}")
        resolved = _resolve_target(repo_root, match.group("path"))
        payload = json.loads(resolved.read_text(encoding="utf-8")) if resolved.exists() else {}
        actual = payload
        for part in match.group("field").split("."):
            if isinstance(actual, dict):
                actual = actual.get(part)
            else:
                actual = None
                break
        passed = _compare(condition.operator, actual, condition.expected)
        details.update({"actual": actual, "resolved_target": str(resolved)})
    elif condition.kind == "file_hash_present":
        resolved = _resolve_target(repo_root, target)
        actual = sha256_file(resolved) if resolved.exists() else ""
        passed = _compare(condition.operator, actual != "", bool(condition.expected))
        details.update({"actual": actual, "resolved_target": str(resolved)})
    elif condition.kind == "sentence_fragment_rate_lte":
        resolved = _resolve_target(repo_root, target)
        actual, extra = _sentence_fragment_rate(resolved)
        passed = _compare(condition.operator, actual, float(condition.expected))
        details.update({"actual": actual, "resolved_target": str(resolved), **extra})
    else:
        raise ValueError(f"Unsupported condition kind: {condition.kind}")

    details["passed"] = passed
    details["message"] = condition.message
    return details
