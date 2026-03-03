"""Cost budget enforcement and usage tracking."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from semantic_ai_washing.director.core.audit import append_jsonl
from semantic_ai_washing.director.core.utils import ensure_dir, load_json, now_utc_iso, sha256_text
from semantic_ai_washing.director.schemas import CostUsageRecord


class CostController:
    def __init__(self, policy: dict[str, Any], usage_file: str | Path, cache_dir: str | Path):
        self.policy = policy
        self.usage_file = Path(usage_file)
        self.cache_dir = ensure_dir(cache_dir)

    def _records(self) -> list[dict[str, Any]]:
        if not self.usage_file.exists():
            return []
        rows: list[dict[str, Any]] = []
        for line in self.usage_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                import json

                rows.append(json.loads(line))
            except Exception:
                continue
        return rows

    def totals(self) -> dict[str, float]:
        tokens = 0
        cost = 0.0
        for row in self._records():
            payload = row.get("payload") or row
            tokens += int(payload.get("total_tokens", 0) or 0)
            cost += float(payload.get("estimated_cost_usd", 0.0) or 0.0)
        return {"total_tokens": tokens, "total_cost_usd": round(cost, 6)}

    def can_spend(self, add_tokens: int = 0, add_cost_usd: float = 0.0) -> tuple[bool, str]:
        totals = self.totals()
        token_cap = int(self.policy.get("max_tokens_per_run", 0) or 0)
        cost_cap = float(self.policy.get("max_cost_usd_per_run", 0.0) or 0.0)

        next_tokens = totals["total_tokens"] + int(add_tokens)
        next_cost = totals["total_cost_usd"] + float(add_cost_usd)

        if token_cap > 0 and next_tokens > token_cap:
            return False, f"token budget exceeded ({next_tokens}>{token_cap})"
        if cost_cap > 0 and next_cost > cost_cap:
            return False, f"cost budget exceeded ({next_cost:.4f}>{cost_cap:.4f})"
        return True, "within budget"

    def estimate_cost_usd(self, prompt_tokens: int, completion_tokens: int) -> float:
        prompt_rate = float(self.policy.get("price_per_1k_prompt_tokens_usd", 0.0) or 0.0)
        completion_rate = float(self.policy.get("price_per_1k_completion_tokens_usd", 0.0) or 0.0)
        return round(
            (prompt_tokens / 1000.0) * prompt_rate
            + (completion_tokens / 1000.0) * completion_rate,
            6,
        )

    def record_usage(self, record: CostUsageRecord) -> None:
        payload = record.as_deterministic_dict()
        payload["recorded_at"] = now_utc_iso()
        append_jsonl(self.usage_file, payload)

    def cache_key(self, prompt: str, context_hash: str) -> str:
        return sha256_text(f"{prompt}\n{context_hash}")

    def cache_get(self, key: str) -> dict[str, Any] | None:
        path = self.cache_dir / f"{key}.json"
        return load_json(path, default=None)

    def cache_put(self, key: str, payload: dict[str, Any]) -> Path:
        path = self.cache_dir / f"{key}.json"
        ensure_dir(path.parent)
        import json

        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return path
