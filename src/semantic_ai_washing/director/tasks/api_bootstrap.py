"""Run a bounded assistive-only OpenAI API smoke test."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

import yaml

from semantic_ai_washing.director.core.api_assistive import (
    build_prompt_messages,
    load_api_assistive_policy,
    parse_assistive_response_text,
    prompt_hash,
    resolve_repo_path,
    select_smoke_sentence,
    smoke_report_base,
    validate_assistive_response_payload,
    write_smoke_report,
)
from semantic_ai_washing.director.core.cost import CostController
from semantic_ai_washing.director.core.openai_responses import (
    OpenAIResponsesError,
    OpenAIResponsesHTTPError,
    call_responses_api,
    extract_response_text,
)
from semantic_ai_washing.director.core.utils import git_info, now_utc_iso, sha256_text
from semantic_ai_washing.director.schemas import CostUsageRecord

DEFAULT_POLICY = "director/config/api_assistive_policy.yaml"
DEFAULT_COST_POLICY = "director/config/cost_policy.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Expected YAML object in {path}")
    return payload


def _cost_controller(
    repo_root: str, cost_policy_path: str
) -> tuple[CostController, dict[str, Any]]:
    resolved = resolve_repo_path(repo_root, cost_policy_path)
    policy = _load_yaml(resolved)
    controller = CostController(
        policy=policy,
        usage_file=resolve_repo_path(repo_root, "director/runs/cost_usage.jsonl"),
        cache_dir=resolve_repo_path(repo_root, "director/cache/llm"),
    )
    return controller, policy


def _usage_payload(
    response_payload: dict[str, Any],
    cost_controller: CostController,
    cost_policy: dict[str, Any],
    *,
    prompt_hash_value: str,
    model_name: str,
) -> tuple[dict[str, Any], str]:
    usage = response_payload.get("usage", {}) if isinstance(response_payload, dict) else {}
    prompt_tokens = int(usage.get("input_tokens", usage.get("prompt_tokens", 0)) or 0)
    completion_tokens = int(usage.get("output_tokens", usage.get("completion_tokens", 0)) or 0)
    total_tokens = int(usage.get("total_tokens", prompt_tokens + completion_tokens) or 0)
    estimated_cost = cost_controller.estimate_cost_usd(prompt_tokens, completion_tokens)
    pricing_unconfigured = (
        float(cost_policy.get("price_per_1k_prompt_tokens_usd", 0.0) or 0.0) == 0.0
        and float(cost_policy.get("price_per_1k_completion_tokens_usd", 0.0) or 0.0) == 0.0
    )
    status = "pricing_unconfigured" if pricing_unconfigured else "estimated"
    record = CostUsageRecord(
        usage_id=sha256_text(f"{prompt_hash_value}:{now_utc_iso()}"),
        component="api_assistive_smoke_test",
        model_name=model_name,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        estimated_cost_usd=estimated_cost,
        cache_hit=False,
        metadata={"prompt_hash": prompt_hash_value},
    )
    cost_controller.record_usage(record)
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "estimated_cost_usd": estimated_cost,
    }, status


def run_api_bootstrap(
    *,
    policy_path: str = DEFAULT_POLICY,
    sample_input: str = "",
    output: str = "",
    mode: str = "live",
    repo_root: str = ".",
    cost_policy_path: str = DEFAULT_COST_POLICY,
) -> tuple[dict[str, Any], int]:
    resolved_root = Path(repo_root).resolve()
    policy, resolved_policy_path = load_api_assistive_policy(policy_path, repo_root=resolved_root)
    resolved_sample_input = (
        resolve_repo_path(resolved_root, sample_input)
        if sample_input
        else resolve_repo_path(resolved_root, policy.selection.sample_input)
    )
    resolved_output = (
        resolve_repo_path(resolved_root, output)
        if output
        else resolve_repo_path(resolved_root, policy.smoke_output["report_path"])
    )
    selected_sentence, selection_fallback = select_smoke_sentence(
        resolved_sample_input,
        repo_root=resolved_root,
        min_tokens=policy.selection.min_tokens,
        max_tokens=policy.selection.max_tokens,
        require_fragment_score_max=policy.selection.require_fragment_score_max,
    )
    messages = build_prompt_messages(policy, selected_sentence["sentence"])
    prompt_hash_value = prompt_hash(messages)
    payload = smoke_report_base(
        policy_path=resolved_policy_path,
        model=policy.model,
        mode=mode,
        selected_sentence=selected_sentence,
        selection_fallback=selection_fallback,
        prompt_hash_value=prompt_hash_value,
    )
    payload["generated_at"] = now_utc_iso()
    payload["git"] = git_info(str(resolved_root))
    payload["request_summary"]["max_output_tokens"] = int(
        policy.request.get("max_output_tokens", policy.selection.max_output_tokens) or 0
    )
    payload["request_summary"]["store"] = bool(policy.request.get("store", policy.selection.store))

    if mode == "dry-run":
        payload["status"] = "dry_run"
        payload["request_summary"]["sample_input"] = str(resolved_sample_input)
        write_smoke_report(resolved_output, payload)
        return payload, 0

    api_key = os.getenv(policy.env_var, "").strip()
    if not api_key:
        payload["status"] = "missing_key"
        payload["error"] = {
            "type": "missing_key",
            "message": f"{policy.env_var} is required for live mode",
            "http_status": None,
        }
        write_smoke_report(resolved_output, payload)
        return payload, 1

    start = time.perf_counter()
    try:
        response_payload = call_responses_api(
            model=policy.model,
            input_payload=messages,
            api_key=api_key,
            max_output_tokens=int(
                policy.request.get("max_output_tokens", policy.selection.max_output_tokens) or 0
            ),
            timeout_seconds=int(
                policy.request.get("timeout_seconds", policy.selection.timeout_seconds) or 60
            ),
            store=bool(policy.request.get("store", policy.selection.store)),
        )
    except OpenAIResponsesHTTPError as exc:
        payload["status"] = "auth_failed" if exc.status_code in {401, 403} else "request_failed"
        payload["latency_ms"] = round((time.perf_counter() - start) * 1000, 3)
        payload["error"] = {
            "type": type(exc).__name__,
            "message": str(exc),
            "http_status": exc.status_code,
        }
        write_smoke_report(resolved_output, payload)
        return payload, 1
    except OpenAIResponsesError as exc:
        payload["status"] = "request_failed"
        payload["latency_ms"] = round((time.perf_counter() - start) * 1000, 3)
        payload["error"] = {
            "type": type(exc).__name__,
            "message": str(exc),
            "http_status": None,
        }
        write_smoke_report(resolved_output, payload)
        return payload, 1

    payload["latency_ms"] = round((time.perf_counter() - start) * 1000, 3)
    controller, cost_policy = _cost_controller(str(resolved_root), cost_policy_path)
    usage_payload, cost_status = _usage_payload(
        response_payload,
        controller,
        cost_policy,
        prompt_hash_value=prompt_hash_value,
        model_name=policy.model,
    )
    payload["usage"] = usage_payload
    payload["cost_estimation_status"] = cost_status

    try:
        response_text = extract_response_text(response_payload)
        parsed = parse_assistive_response_text(response_text)
    except (json.JSONDecodeError, ValueError) as exc:
        payload["status"] = "invalid_response"
        payload["error"] = {
            "type": type(exc).__name__,
            "message": str(exc),
            "http_status": None,
        }
        write_smoke_report(resolved_output, payload)
        return payload, 1

    try:
        response_summary = validate_assistive_response_payload(parsed, policy)
    except ValueError as exc:
        payload["status"] = "invalid_label"
        payload["error"] = {
            "type": type(exc).__name__,
            "message": str(exc),
            "http_status": None,
        }
        write_smoke_report(resolved_output, payload)
        return payload, 1

    payload["status"] = "passed"
    payload["response_summary"] = response_summary
    payload["request_summary"]["response_id"] = response_payload.get("id", "")
    write_smoke_report(resolved_output, payload)
    return payload, 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", default=DEFAULT_POLICY)
    parser.add_argument("--sample-input", default="")
    parser.add_argument("--output", default="")
    parser.add_argument("--mode", choices=["live", "dry-run"], default="live")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--cost-policy", default=DEFAULT_COST_POLICY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    _, exit_code = run_api_bootstrap(
        policy_path=args.policy,
        sample_input=args.sample_input,
        output=args.output,
        mode=args.mode,
        repo_root=args.repo_root,
        cost_policy_path=args.cost_policy,
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
