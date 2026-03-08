"""Generate bounded assistive-only prelabels for a labeling review CSV."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from semantic_ai_washing.director.core.api_assistive import (
    build_prompt_messages,
    load_api_assistive_policy,
    parse_assistive_response_text,
    prompt_hash,
    validate_assistive_response_payload,
)
from semantic_ai_washing.director.core.cost import CostController
from semantic_ai_washing.director.core.openai_responses import (
    OpenAIResponsesError,
    OpenAIResponsesHTTPError,
    call_responses_api,
    extract_response_text,
)
from semantic_ai_washing.director.core.utils import dump_json, now_utc_iso, sha256_text
from semantic_ai_washing.director.schemas import CostUsageRecord

DEFAULT_INPUT = "data/labels/v1/labeling_batch_v1.csv"
DEFAULT_OUTPUT = "data/labels/v1/labeling_batch_v1_prelabeled.csv"
DEFAULT_REPORT = "reports/labels/assistive_prelabel_summary.json"
DEFAULT_POLICY = "director/config/api_assistive_policy.yaml"
DEFAULT_COST_POLICY = "director/config/cost_policy.yaml"
ASSISTIVE_COLUMNS = [
    "assistive_label",
    "assistive_confidence",
    "assistive_rationale",
    "assistive_model",
    "assistive_generated_at",
    "assistive_prompt_hash",
]
REQUIRED_COLUMNS = ["sentence_id", "sentence", "source_file", "sentence_index", "label"]


def _resolve(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def _load_yaml(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return payload


def _load_frame(input_csv: str, output_csv: str) -> tuple[pd.DataFrame, bool]:
    input_path = _resolve(input_csv)
    output_path = _resolve(output_csv)
    source_path = output_path if output_path.exists() else input_path
    frame = pd.read_csv(source_path)
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Input labeling batch missing required columns: {missing}")
    for column in ASSISTIVE_COLUMNS:
        if column not in frame.columns:
            frame[column] = ""
    return frame, output_path.exists()


def _build_cost_controller(cost_policy_path: str) -> tuple[CostController, dict[str, Any]]:
    policy = _load_yaml(cost_policy_path)
    controller = CostController(
        policy=policy,
        usage_file=_resolve("director/runs/cost_usage.jsonl"),
        cache_dir=_resolve("director/cache/llm"),
    )
    return controller, policy


def _record_usage(
    controller: CostController,
    cost_policy: dict[str, Any],
    *,
    prompt_hash_value: str,
    model_name: str,
    response_payload: dict[str, Any],
) -> dict[str, Any]:
    usage = response_payload.get("usage", {}) if isinstance(response_payload, dict) else {}
    prompt_tokens = int(usage.get("input_tokens", usage.get("prompt_tokens", 0)) or 0)
    completion_tokens = int(usage.get("output_tokens", usage.get("completion_tokens", 0)) or 0)
    total_tokens = int(usage.get("total_tokens", prompt_tokens + completion_tokens) or 0)
    estimated_cost = controller.estimate_cost_usd(prompt_tokens, completion_tokens)
    pricing_unconfigured = (
        float(cost_policy.get("price_per_1k_prompt_tokens_usd", 0.0) or 0.0) == 0.0
        and float(cost_policy.get("price_per_1k_completion_tokens_usd", 0.0) or 0.0) == 0.0
    )
    record = CostUsageRecord(
        usage_id=sha256_text(f"assistive-prelabel:{prompt_hash_value}:{now_utc_iso()}"),
        component="assistive_prelabel_batch",
        model_name=model_name,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        estimated_cost_usd=estimated_cost,
        cache_hit=False,
        metadata={"prompt_hash": prompt_hash_value},
    )
    controller.record_usage(record)
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "estimated_cost_usd": estimated_cost,
        "cost_estimation_status": "pricing_unconfigured" if pricing_unconfigured else "estimated",
    }


def generate_assistive_prelabels(
    *,
    input_csv: str = DEFAULT_INPUT,
    output_csv: str = DEFAULT_OUTPUT,
    report_path: str = DEFAULT_REPORT,
    policy_path: str = DEFAULT_POLICY,
    cost_policy_path: str = DEFAULT_COST_POLICY,
    mode: str = "live",
    max_rows: int = 0,
    sleep_seconds: float = 0.0,
) -> tuple[dict[str, Any], int]:
    policy, resolved_policy = load_api_assistive_policy(policy_path)
    frame, resumed = _load_frame(input_csv, output_csv)

    frame = frame.sort_values(["source_file", "sentence_index", "sentence_id"]).reset_index(
        drop=True
    )
    canonical_labeled_mask = frame["label"].fillna("").astype(str).map(str.strip).ne("")
    existing_assistive_mask = frame["assistive_label"].fillna("").astype(str).map(str.strip).ne("")
    pending = frame[~canonical_labeled_mask & ~existing_assistive_mask].copy()
    if max_rows > 0:
        pending = pending.head(max_rows).copy()

    report: dict[str, Any] = {
        "generated_at": now_utc_iso(),
        "status": "pending",
        "mode": mode,
        "policy_path": str(resolved_policy),
        "input_csv": str(_resolve(input_csv)),
        "output_csv": str(_resolve(output_csv)),
        "report_path": str(_resolve(report_path)),
        "model": policy.model,
        "resumed_existing_output": resumed,
        "parameters": {
            "max_rows": int(max_rows),
            "sleep_seconds": float(sleep_seconds),
        },
        "counts": {
            "input_rows": int(len(frame)),
            "skipped_canonical_labeled_rows": int(canonical_labeled_mask.sum()),
            "skipped_existing_assistive_rows": int(existing_assistive_mask.sum()),
            "pending_rows_before_run": int(len(pending)),
            "processed_rows": 0,
            "failed_rows": 0,
            "pending_rows_after_run": 0,
        },
        "usage": {
            "request_count": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "estimated_cost_usd": 0.0,
            "cost_estimation_status": "not_applicable",
        },
        "errors": [],
    }

    output_path = _resolve(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_file = _resolve(report_path)
    report_file.parent.mkdir(parents=True, exist_ok=True)

    if mode == "dry-run":
        frame.to_csv(output_path, index=False)
        report["status"] = "dry_run"
        report["counts"]["pending_rows_after_run"] = int(len(pending))
        dump_json(report_file, report)
        return report, 0

    api_key = os.getenv(policy.env_var, "").strip()
    if not api_key:
        frame.to_csv(output_path, index=False)
        report["status"] = "missing_key"
        report["counts"]["pending_rows_after_run"] = int(len(pending))
        report["errors"].append(
            {"type": "missing_key", "message": f"{policy.env_var} is required"}
        )
        dump_json(report_file, report)
        return report, 1

    controller, cost_policy = _build_cost_controller(cost_policy_path)

    for row in pending.itertuples(index=True):
        messages = build_prompt_messages(policy, str(row.sentence))
        prompt_hash_value = prompt_hash(messages)
        extra_payload: dict[str, Any] = {}
        reasoning_effort = str(policy.request.get("reasoning_effort", "")).strip()
        if reasoning_effort:
            extra_payload["reasoning"] = {"effort": reasoning_effort}
        text_format = policy.request.get("text_format", "")
        if isinstance(text_format, dict) and text_format:
            extra_payload["text"] = {"format": text_format}

        try:
            response_payload = call_responses_api(
                model=policy.model,
                input_payload=messages,
                api_key=api_key,
                max_output_tokens=int(policy.request.get("max_output_tokens", 200) or 200),
                timeout_seconds=int(policy.request.get("timeout_seconds", 60) or 60),
                store=bool(policy.request.get("store", False)),
                extra_payload=extra_payload or None,
            )
            response_text = extract_response_text(response_payload)
            parsed = parse_assistive_response_text(response_text)
            summary = validate_assistive_response_payload(parsed, policy)
            usage = _record_usage(
                controller,
                cost_policy,
                prompt_hash_value=prompt_hash_value,
                model_name=policy.model,
                response_payload=response_payload,
            )
        except OpenAIResponsesHTTPError as exc:
            report["errors"].append(
                {
                    "sentence_id": str(row.sentence_id),
                    "type": type(exc).__name__,
                    "message": str(exc),
                    "http_status": exc.status_code,
                }
            )
            report["counts"]["failed_rows"] += 1
            frame.to_csv(output_path, index=False)
            report["status"] = "request_failed"
            break
        except (OpenAIResponsesError, ValueError, json.JSONDecodeError) as exc:
            report["errors"].append(
                {
                    "sentence_id": str(row.sentence_id),
                    "type": type(exc).__name__,
                    "message": str(exc),
                }
            )
            report["counts"]["failed_rows"] += 1
            frame.to_csv(output_path, index=False)
            report["status"] = "request_failed"
            break

        frame.at[row.Index, "assistive_label"] = summary["label"]
        frame.at[row.Index, "assistive_confidence"] = summary["confidence"]
        frame.at[row.Index, "assistive_rationale"] = summary["rationale"]
        frame.at[row.Index, "assistive_model"] = policy.model
        frame.at[row.Index, "assistive_generated_at"] = now_utc_iso()
        frame.at[row.Index, "assistive_prompt_hash"] = prompt_hash_value
        report["counts"]["processed_rows"] += 1
        report["usage"]["request_count"] += 1
        report["usage"]["prompt_tokens"] += usage["prompt_tokens"]
        report["usage"]["completion_tokens"] += usage["completion_tokens"]
        report["usage"]["total_tokens"] += usage["total_tokens"]
        report["usage"]["estimated_cost_usd"] = round(
            report["usage"]["estimated_cost_usd"] + usage["estimated_cost_usd"], 6
        )
        report["usage"]["cost_estimation_status"] = usage["cost_estimation_status"]

        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

    frame.to_csv(output_path, index=False)
    if report["status"] == "pending":
        report["status"] = "passed"
    current_pending_mask = frame["label"].fillna("").astype(str).map(str.strip).eq("") & frame[
        "assistive_label"
    ].fillna("").astype(str).map(str.strip).eq("")
    report["counts"]["pending_rows_after_run"] = int(current_pending_mask.sum())
    dump_json(report_file, report)
    return report, 0 if report["status"] == "passed" else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", default=DEFAULT_INPUT)
    parser.add_argument("--output-csv", default=DEFAULT_OUTPUT)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    parser.add_argument("--policy", default=DEFAULT_POLICY)
    parser.add_argument("--cost-policy", default=DEFAULT_COST_POLICY)
    parser.add_argument("--mode", choices=["live", "dry-run"], default="live")
    parser.add_argument("--max-rows", type=int, default=0)
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    _, exit_code = generate_assistive_prelabels(
        input_csv=args.input_csv,
        output_csv=args.output_csv,
        report_path=args.report,
        policy_path=args.policy,
        cost_policy_path=args.cost_policy,
        mode=args.mode,
        max_rows=args.max_rows,
        sleep_seconds=args.sleep_seconds,
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
