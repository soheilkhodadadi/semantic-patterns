"""Optional LLM refinement for generated plans and runbooks."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from semantic_ai_washing.director.core.cost import CostController
from semantic_ai_washing.director.core.utils import now_utc_iso, sha256_text
from semantic_ai_washing.director.schemas import CostUsageRecord

OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"


def _extract_response_text(payload: dict[str, Any]) -> str:
    if isinstance(payload.get("output_text"), str) and payload["output_text"].strip():
        return payload["output_text"].strip()

    output = payload.get("output", [])
    chunks: list[str] = []
    for item in output:
        for content in item.get("content", []):
            text = content.get("text")
            if text:
                chunks.append(text)
    return "\n".join(chunks).strip()


def refine_plan_markdown(
    plan_markdown: str,
    context_payload: dict[str, Any],
    llm_config: dict[str, Any],
    cost_controller: CostController,
) -> tuple[str, dict[str, Any]]:
    """Return refined plan text and metadata.

    Deterministic path first:
      - if llm is disabled or no key, return original with explanatory metadata.
      - if enabled, run under budget caps with response caching.
    """
    if not llm_config.get("llm_enabled", False):
        return plan_markdown, {"used_llm": False, "reason": "llm_enabled=false"}

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return plan_markdown, {"used_llm": False, "reason": "OPENAI_API_KEY missing"}

    model = str(llm_config.get("model", "gpt-5-mini"))
    max_prompt_tokens = int(llm_config.get("max_prompt_tokens_per_call", 4000) or 4000)
    max_completion_tokens = int(llm_config.get("max_completion_tokens_per_call", 1200) or 1200)

    context_hash = sha256_text(json.dumps(context_payload, sort_keys=True))
    cache_key = cost_controller.cache_key(plan_markdown, context_hash)
    cached = cost_controller.cache_get(cache_key)
    if cached:
        usage = cached.get("usage", {})
        record = CostUsageRecord(
            usage_id=sha256_text(f"{cache_key}:cache"),
            component="planner_llm_refinement",
            model_name=model,
            prompt_tokens=int(usage.get("prompt_tokens", 0) or 0),
            completion_tokens=int(usage.get("completion_tokens", 0) or 0),
            total_tokens=int(usage.get("total_tokens", 0) or 0),
            estimated_cost_usd=float(usage.get("estimated_cost_usd", 0.0) or 0.0),
            cache_hit=True,
            metadata={"cached_at": cached.get("cached_at", "")},
        )
        cost_controller.record_usage(record)
        return cached.get("refined_markdown", plan_markdown), {
            "used_llm": True,
            "cache_hit": True,
            "model": model,
            "cache_key": cache_key,
        }

    allow, reason = cost_controller.can_spend(add_tokens=max_prompt_tokens + max_completion_tokens)
    if not allow:
        return plan_markdown, {"used_llm": False, "reason": reason}

    prompt = (
        "Refine this implementation plan for clarity and risk handling without changing intent. "
        "Return markdown only. Keep gates explicit and deterministic.\n\n"
        f"Context:\n{json.dumps(context_payload, indent=2, sort_keys=True)}\n\n"
        f"Plan:\n{plan_markdown}"
    )
    request_payload = {
        "model": model,
        "input": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are a strict engineering planner. Preserve constraints and avoid scope creep.",
                    }
                ],
            },
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            },
        ],
        "max_output_tokens": max_completion_tokens,
    }

    req = urllib.request.Request(
        OPENAI_RESPONSES_URL,
        data=json.dumps(request_payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
        data = json.loads(raw)
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        json.JSONDecodeError,
    ) as exc:
        return plan_markdown, {
            "used_llm": False,
            "reason": f"llm_call_failed: {type(exc).__name__}",
        }

    refined = _extract_response_text(data)
    if not refined:
        return plan_markdown, {"used_llm": False, "reason": "llm_empty_response"}

    usage = data.get("usage", {}) if isinstance(data, dict) else {}
    prompt_tokens = int(usage.get("input_tokens", usage.get("prompt_tokens", 0)) or 0)
    completion_tokens = int(usage.get("output_tokens", usage.get("completion_tokens", 0)) or 0)
    total_tokens = int(usage.get("total_tokens", prompt_tokens + completion_tokens) or 0)
    estimated_cost = cost_controller.estimate_cost_usd(prompt_tokens, completion_tokens)

    record = CostUsageRecord(
        usage_id=sha256_text(f"{cache_key}:live:{now_utc_iso()}"),
        component="planner_llm_refinement",
        model_name=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        estimated_cost_usd=estimated_cost,
        cache_hit=False,
        metadata={"cache_key": cache_key},
    )
    cost_controller.record_usage(record)

    cost_controller.cache_put(
        cache_key,
        {
            "cached_at": now_utc_iso(),
            "model": model,
            "refined_markdown": refined,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "estimated_cost_usd": estimated_cost,
            },
        },
    )

    return refined, {
        "used_llm": True,
        "cache_hit": False,
        "model": model,
        "cache_key": cache_key,
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": estimated_cost,
        },
    }
