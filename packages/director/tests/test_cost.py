from __future__ import annotations

from semantic_director.cost import CostController
from semantic_director.schemas import CostUsageRecord


def test_cost_limiter_blocks_additional_usage(tmp_path) -> None:
    usage = tmp_path / "cost_usage.jsonl"
    controller = CostController(
        policy={"max_tokens_per_run": 10, "max_cost_usd_per_run": 1.0},
        usage_file=usage,
        cache_dir=tmp_path / "cache",
    )

    controller.record_usage(
        CostUsageRecord(
            usage_id="u1",
            component="test",
            prompt_tokens=6,
            completion_tokens=3,
            total_tokens=9,
            estimated_cost_usd=0.2,
        )
    )
    ok, _ = controller.can_spend(add_tokens=3, add_cost_usd=0.1)
    assert not ok


def test_cost_cache_round_trip(tmp_path) -> None:
    controller = CostController(
        policy={},
        usage_file=tmp_path / "cost_usage.jsonl",
        cache_dir=tmp_path / "cache",
    )

    key = controller.cache_key("prompt", "ctx")
    payload = {"value": 1}
    controller.cache_put(key, payload)
    assert controller.cache_get(key) == payload
