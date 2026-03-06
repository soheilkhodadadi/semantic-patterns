"""Helpers for assistive-only API bootstrap workflows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from semantic_ai_washing.director.schemas import ApiAssistivePolicy
from semantic_ai_washing.director.core.utils import dump_json, sha256_text


def resolve_repo_path(repo_root: str | Path, target: str | Path) -> Path:
    candidate = Path(target)
    if candidate.is_absolute():
        return candidate.resolve()
    return (Path(repo_root).resolve() / candidate).resolve()


def load_api_assistive_policy(
    path: str | Path,
    repo_root: str | Path = ".",
) -> tuple[ApiAssistivePolicy, Path]:
    resolved = resolve_repo_path(repo_root, path)
    payload = yaml.safe_load(resolved.read_text(encoding="utf-8")) or {}
    policy = ApiAssistivePolicy.model_validate(payload)

    rubric_path = resolve_repo_path(repo_root, policy.prompt_spec.reference_rubric_path)
    if not rubric_path.exists():
        raise ValueError(f"Referenced rubric path does not exist: {rubric_path}")
    return policy, resolved


def select_smoke_sentence(
    sample_input: str | Path,
    *,
    repo_root: str | Path = ".",
    min_tokens: int = 12,
    max_tokens: int = 120,
    require_fragment_score_max: float = 0.0,
) -> tuple[dict[str, Any], bool]:
    resolved = resolve_repo_path(repo_root, sample_input)
    df = pd.read_csv(resolved)
    required_columns = {
        "sentence_id",
        "sentence",
        "source_file",
        "source_year",
        "source_quarter",
        "source_cik",
        "sentence_index",
        "token_count",
        "fragment_score",
    }
    missing = sorted(required_columns - set(df.columns))
    if missing:
        raise ValueError(f"Sample input missing required columns: {missing}")

    ordered = df.sort_values(["source_file", "sentence_index", "sentence_id"]).reset_index(
        drop=True
    )
    eligible = ordered[
        (ordered["token_count"] >= min_tokens)
        & (ordered["token_count"] <= max_tokens)
        & (ordered["fragment_score"] <= require_fragment_score_max)
    ]
    selection_fallback = eligible.empty
    chosen = eligible.iloc[0] if not eligible.empty else ordered.iloc[0]
    return {
        "sentence_id": str(chosen["sentence_id"]),
        "sentence": str(chosen["sentence"]),
        "source_file": str(chosen["source_file"]),
        "source_year": int(chosen["source_year"]),
        "source_quarter": int(chosen["source_quarter"]),
        "source_cik": str(chosen["source_cik"]),
        "sentence_index": int(chosen["sentence_index"]),
        "token_count": int(chosen["token_count"]),
        "fragment_score": float(chosen["fragment_score"]),
        "sentence_excerpt": str(chosen["sentence"])[:240],
    }, selection_fallback


def build_prompt_messages(policy: ApiAssistivePolicy, sentence: str) -> list[dict[str, Any]]:
    user_text = (
        f"{policy.prompt_spec.user_prompt_template}\n\n"
        f"Sentence:\n{sentence}\n\n"
        "Return a single JSON object and no surrounding commentary."
    )
    return [
        {
            "role": "system",
            "content": [{"type": "text", "text": policy.prompt_spec.system_prompt}],
        },
        {
            "role": "user",
            "content": [{"type": "text", "text": user_text}],
        },
    ]


def prompt_hash(messages: list[dict[str, Any]]) -> str:
    return sha256_text(json.dumps(messages, sort_keys=True))


def parse_assistive_response_text(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
    payload = json.loads(cleaned)
    if not isinstance(payload, dict):
        raise ValueError("Assistive response must decode to a JSON object")
    return payload


def validate_assistive_response_payload(
    payload: dict[str, Any],
    policy: ApiAssistivePolicy,
) -> dict[str, Any]:
    label = str(payload.get("label", "")).strip()
    confidence = str(payload.get("confidence", "")).strip().lower()
    rationale = str(payload.get("rationale", "")).strip()
    assistive_only = payload.get("assistive_only")

    if label not in policy.prompt_spec.label_set:
        raise ValueError(f"Invalid label returned: {label or '<missing>'}")
    if confidence not in policy.prompt_spec.confidence_bands:
        raise ValueError(f"Invalid confidence returned: {confidence or '<missing>'}")
    if assistive_only is not True:
        raise ValueError("assistive_only must be true")
    if not rationale:
        raise ValueError("rationale must be non-empty")

    return {
        "label": label,
        "confidence": confidence,
        "rationale": rationale,
        "assistive_only": True,
    }


def smoke_report_base(
    *,
    policy_path: str | Path,
    model: str,
    mode: str,
    selected_sentence: dict[str, Any],
    selection_fallback: bool,
    prompt_hash_value: str,
) -> dict[str, Any]:
    return {
        "status": "pending",
        "mode": mode,
        "policy_path": str(policy_path),
        "model": model,
        "selected_sentence": selected_sentence,
        "selection_fallback": selection_fallback,
        "request_summary": {
            "store": False,
            "max_output_tokens": 0,
            "prompt_hash": prompt_hash_value,
        },
        "response_summary": {},
        "usage": {},
        "cost_estimation_status": "not_applicable",
        "latency_ms": 0,
        "error": None,
    }


def write_smoke_report(path: str | Path, payload: dict[str, Any]) -> None:
    dump_json(path, payload)
