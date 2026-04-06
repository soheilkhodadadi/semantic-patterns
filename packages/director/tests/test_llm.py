from __future__ import annotations

from semantic_director.cost import CostController
from semantic_director.llm import refine_plan_markdown


def test_refine_plan_markdown_disabled_returns_original(tmp_path) -> None:
    controller = CostController(
        policy={}, usage_file=tmp_path / "usage.jsonl", cache_dir=tmp_path / "cache"
    )
    refined, meta = refine_plan_markdown(
        plan_markdown="# Plan\n- keep scope",
        context_payload={"phase": "alpha"},
        llm_config={"llm_enabled": False},
        cost_controller=controller,
    )
    assert refined == "# Plan\n- keep scope"
    assert meta == {"used_llm": False, "reason": "llm_enabled=false"}


def test_refine_plan_markdown_missing_key_returns_original(tmp_path, monkeypatch) -> None:
    controller = CostController(
        policy={}, usage_file=tmp_path / "usage.jsonl", cache_dir=tmp_path / "cache"
    )
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    refined, meta = refine_plan_markdown(
        plan_markdown="# Plan\n- keep scope",
        context_payload={"phase": "alpha"},
        llm_config={"llm_enabled": True},
        cost_controller=controller,
    )
    assert refined == "# Plan\n- keep scope"
    assert meta == {"used_llm": False, "reason": "OPENAI_API_KEY missing"}
