from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
import yaml

from semantic_ai_washing.director.core.api_assistive import (
    load_api_assistive_policy,
    select_smoke_sentence,
)
from semantic_ai_washing.director.tasks.api_bootstrap import run_api_bootstrap


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "sentence_id": "bbb",
                "sentence": "short fragment",
                "source_file": "2024/QTR1/file_b.txt",
                "source_year": 2024,
                "source_quarter": 1,
                "source_cik": "2",
                "sentence_index": 2,
                "token_count": 2,
                "fragment_score": 0.5,
            },
            {
                "sentence_id": "aaa",
                "sentence": "We currently use artificial intelligence to automate claims processing.",
                "source_file": "2024/QTR1/file_a.txt",
                "source_year": 2024,
                "source_quarter": 1,
                "source_cik": "1",
                "sentence_index": 1,
                "token_count": 9,
                "fragment_score": 0.0,
            },
            {
                "sentence_id": "ccc",
                "sentence": "We plan to expand our AI roadmap next year.",
                "source_file": "2024/QTR2/file_c.txt",
                "source_year": 2024,
                "source_quarter": 2,
                "source_cik": "3",
                "sentence_index": 3,
                "token_count": 30,
                "fragment_score": 0.0,
            },
        ]
    )


def _write_policy(repo_root: Path, *, mode: str = "assistive_only") -> Path:
    _write(repo_root / "docs" / "labeling_protocol.md", "# protocol\n")
    payload = {
        "schema_version": "1.0.0",
        "mode": mode,
        "provider": "openai",
        "transport": "responses_api",
        "env_var": "OPENAI_API_KEY",
        "model": "gpt-5-mini",
        "request": {
            "store": False,
            "timeout_seconds": 60,
            "max_output_tokens": 200,
        },
        "budget": {
            "max_live_requests_per_run": 1,
            "max_prompt_tokens_per_call": 1200,
            "max_output_tokens_per_call": 200,
            "max_estimated_cost_usd_per_run": 0.10,
        },
        "selection": {
            "sample_input": "data/processed/sentences/year=2024/ai_sentences_sample.csv",
            "min_tokens": 12,
            "max_tokens": 120,
            "require_fragment_score_max": 0.0,
        },
        "telemetry": {
            "usage_file": "director/runs/cost_usage.jsonl",
            "component": "api_assistive_smoke_test",
            "cache_allowed": False,
        },
        "usage_policy": {
            "canonical": False,
            "allowed_use_cases": ["rubric_check"],
            "prohibited_use_cases": ["canonical_training_labels"],
        },
        "prompt_spec": {
            "reference_rubric_path": "docs/labeling_protocol.md",
            "label_set": ["Actionable", "Speculative", "Irrelevant"],
            "confidence_bands": ["high", "medium", "low"],
            "system_prompt": "Return JSON only.",
            "user_prompt_template": "Label this sentence.",
        },
        "smoke_output": {
            "report_path": "reports/api/api_bootstrap_smoke_test.json",
        },
    }
    policy_path = repo_root / "director" / "config" / "api_assistive_policy.yaml"
    policy_path.parent.mkdir(parents=True, exist_ok=True)
    policy_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return policy_path


def _write_cost_policy(repo_root: Path) -> Path:
    path = repo_root / "director" / "config" / "cost_policy.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(
            {
                "llm_enabled": False,
                "model": "gpt-5-mini",
                "max_tokens_per_run": 15000,
                "max_cost_usd_per_run": 2.0,
                "max_prompt_tokens_per_call": 4000,
                "max_completion_tokens_per_call": 1200,
                "price_per_1k_prompt_tokens_usd": 0.0,
                "price_per_1k_completion_tokens_usd": 0.0,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return path


def _write_sample(repo_root: Path) -> Path:
    path = repo_root / "data" / "processed" / "sentences" / "year=2024" / "ai_sentences_sample.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    _sample_df().to_csv(path, index=False)
    return path


def test_load_api_assistive_policy_validates_expected_shape(tmp_path):
    policy_path = _write_policy(tmp_path)
    policy, resolved = load_api_assistive_policy(policy_path, repo_root=tmp_path)

    assert resolved == policy_path.resolve()
    assert policy.mode == "assistive_only"
    assert policy.prompt_spec.label_set == ["Actionable", "Speculative", "Irrelevant"]


def test_load_api_assistive_policy_rejects_invalid_mode(tmp_path):
    policy_path = _write_policy(tmp_path, mode="canonical")
    with pytest.raises(ValueError, match="assistive_only"):
        load_api_assistive_policy(policy_path, repo_root=tmp_path)


def test_select_smoke_sentence_prefers_clean_bounded_row(tmp_path):
    sample_path = _write_sample(tmp_path)
    selected, fallback = select_smoke_sentence(
        sample_path,
        repo_root=tmp_path,
        min_tokens=12,
        max_tokens=120,
        require_fragment_score_max=0.0,
    )

    assert selected["sentence_id"] == "ccc"
    assert fallback is False


def test_run_api_bootstrap_dry_run_writes_report(tmp_path):
    policy_path = _write_policy(tmp_path)
    _write_sample(tmp_path)
    cost_policy = _write_cost_policy(tmp_path)

    payload, exit_code = run_api_bootstrap(
        policy_path=str(policy_path),
        mode="dry-run",
        repo_root=str(tmp_path),
        cost_policy_path=str(cost_policy),
    )

    report_path = tmp_path / "reports" / "api" / "api_bootstrap_smoke_test.json"
    assert exit_code == 0
    assert report_path.exists()
    assert payload["status"] == "dry_run"
    assert payload["selected_sentence"]["sentence_id"] == "ccc"


def test_run_api_bootstrap_live_missing_key_writes_truthful_failure(tmp_path, monkeypatch):
    policy_path = _write_policy(tmp_path)
    _write_sample(tmp_path)
    cost_policy = _write_cost_policy(tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    payload, exit_code = run_api_bootstrap(
        policy_path=str(policy_path),
        mode="live",
        repo_root=str(tmp_path),
        cost_policy_path=str(cost_policy),
    )

    assert exit_code == 1
    assert payload["status"] == "missing_key"
    assert payload["error"]["type"] == "missing_key"


def test_run_api_bootstrap_live_success_records_usage(tmp_path, monkeypatch):
    policy_path = _write_policy(tmp_path)
    _write_sample(tmp_path)
    cost_policy = _write_cost_policy(tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-proj-abcdefghijklmnopqrstuvwxyz123456")

    def _fake_call(**_: object) -> dict[str, object]:
        return {
            "id": "resp_test",
            "output_text": json.dumps(
                {
                    "label": "Actionable",
                    "confidence": "high",
                    "rationale": "Explicit current operational use.",
                    "assistive_only": True,
                }
            ),
            "usage": {
                "input_tokens": 111,
                "output_tokens": 29,
                "total_tokens": 140,
            },
        }

    monkeypatch.setattr(
        "semantic_ai_washing.director.tasks.api_bootstrap.call_responses_api",
        _fake_call,
    )

    payload, exit_code = run_api_bootstrap(
        policy_path=str(policy_path),
        mode="live",
        repo_root=str(tmp_path),
        cost_policy_path=str(cost_policy),
    )

    usage_file = tmp_path / "director" / "runs" / "cost_usage.jsonl"
    assert exit_code == 0
    assert payload["status"] == "passed"
    assert payload["response_summary"]["label"] == "Actionable"
    assert payload["usage"]["total_tokens"] == 140
    assert usage_file.exists()
