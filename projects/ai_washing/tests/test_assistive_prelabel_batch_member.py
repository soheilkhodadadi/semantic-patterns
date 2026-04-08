from __future__ import annotations

import json
import pandas as pd
import yaml
from semantic_director.cost import CostController

from ai_washing_member.labeling.assistive_prelabel_batch import generate_assistive_prelabels


def test_assistive_prelabel_batch_member_dry_run_writes_expected_report(tmp_path) -> None:
    input_csv = tmp_path / "labeling_batch.csv"
    output_csv = tmp_path / "labeling_batch_prelabeled.csv"
    report_path = tmp_path / "assistive_prelabel_summary.json"
    rubric_path = tmp_path / "docs" / "labeling_protocol.md"
    policy_path = tmp_path / "director" / "config" / "api_assistive_policy.yaml"

    rubric_path.parent.mkdir(parents=True, exist_ok=True)
    rubric_path.write_text("# protocol\n", encoding="utf-8")
    policy_path.parent.mkdir(parents=True, exist_ok=True)
    policy_path.write_text(
        yaml.safe_dump(
            {
                "schema_version": "1.0.0",
                "mode": "assistive_only",
                "provider": "openai",
                "transport": "responses_api",
                "env_var": "OPENAI_API_KEY",
                "model": "gpt-5-mini",
                "request": {"store": False, "timeout_seconds": 60, "max_output_tokens": 200},
                "budget": {
                    "max_live_requests_per_run": 1,
                    "max_prompt_tokens_per_call": 1200,
                    "max_output_tokens_per_call": 200,
                    "max_estimated_cost_usd_per_run": 0.10,
                },
                "selection": {
                    "sample_input": "data/sample.csv",
                    "min_tokens": 12,
                    "max_tokens": 120,
                    "require_fragment_score_max": 0.0,
                },
                "telemetry": {
                    "usage_file": "director/runs/cost_usage.jsonl",
                    "component": "assistive_prelabel_batch",
                    "cache_allowed": False,
                },
                "usage_policy": {
                    "canonical": False,
                    "allowed_use_cases": ["rubric_check"],
                    "prohibited_use_cases": ["canonical_training_labels"],
                },
                "prompt_spec": {
                    "reference_rubric_path": str(rubric_path),
                    "label_set": ["Actionable", "Speculative", "Irrelevant"],
                    "confidence_bands": ["high", "medium", "low"],
                    "system_prompt": "Return JSON only.",
                    "user_prompt_template": "Label this sentence.",
                },
                "smoke_output": {"report_path": str(report_path)},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    pd.DataFrame(
        [
            {
                "sentence_id": "s1",
                "sentence": "We use artificial intelligence in operations today.",
                "source_file": "2024/QTR1/f1.txt",
                "sentence_index": 1,
                "label": "",
            }
        ]
    ).to_csv(input_csv, index=False)

    report, exit_code = generate_assistive_prelabels(
        input_csv=str(input_csv),
        output_csv=str(output_csv),
        report_path=str(report_path),
        policy_path=str(policy_path),
        mode="dry-run",
    )

    assert exit_code == 0
    assert report["status"] == "dry_run"
    written = json.loads(report_path.read_text(encoding="utf-8"))
    assert written["status"] == "dry_run"
    assert written["counts"]["pending_rows_before_run"] == 1


def test_assistive_prelabel_batch_member_retries_parse_failures(tmp_path, monkeypatch) -> None:
    input_csv = tmp_path / "labeling_batch.csv"
    output_csv = tmp_path / "labeling_batch_prelabeled.csv"
    report_path = tmp_path / "assistive_prelabel_summary.json"
    rubric_path = tmp_path / "docs" / "labeling_protocol.md"
    policy_path = tmp_path / "director" / "config" / "api_assistive_policy.yaml"
    usage_file = tmp_path / "cost_usage.jsonl"

    rubric_path.parent.mkdir(parents=True, exist_ok=True)
    rubric_path.write_text("# protocol\n", encoding="utf-8")
    policy_path.parent.mkdir(parents=True, exist_ok=True)
    policy_path.write_text(
        yaml.safe_dump(
            {
                "schema_version": "1.0.0",
                "mode": "assistive_only",
                "provider": "openai",
                "transport": "responses_api",
                "env_var": "OPENAI_API_KEY",
                "model": "gpt-5-mini",
                "request": {"store": False, "timeout_seconds": 60, "max_output_tokens": 200},
                "budget": {
                    "max_live_requests_per_run": 1,
                    "max_prompt_tokens_per_call": 1200,
                    "max_output_tokens_per_call": 200,
                    "max_estimated_cost_usd_per_run": 0.10,
                },
                "selection": {
                    "sample_input": "data/sample.csv",
                    "min_tokens": 12,
                    "max_tokens": 120,
                    "require_fragment_score_max": 0.0,
                },
                "telemetry": {
                    "usage_file": "director/runs/cost_usage.jsonl",
                    "component": "assistive_prelabel_batch",
                    "cache_allowed": False,
                },
                "usage_policy": {
                    "canonical": False,
                    "allowed_use_cases": ["rubric_check"],
                    "prohibited_use_cases": ["canonical_training_labels"],
                },
                "prompt_spec": {
                    "reference_rubric_path": str(rubric_path),
                    "label_set": ["Actionable", "Speculative", "Irrelevant"],
                    "confidence_bands": ["high", "medium", "low"],
                    "system_prompt": "Return JSON only.",
                    "user_prompt_template": "Label this sentence.",
                },
                "smoke_output": {"report_path": str(report_path)},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    pd.DataFrame(
        [
            {
                "sentence_id": "s1",
                "sentence": "We use artificial intelligence in operations today.",
                "source_file": "2024/QTR1/f1.txt",
                "sentence_index": 1,
                "label": "",
            }
        ]
    ).to_csv(input_csv, index=False)

    call_count = {"value": 0}
    response_texts = iter(
        [
            "",
            json.dumps(
                {
                    "label": "Actionable",
                    "confidence": "high",
                    "rationale": "Current operational use is explicit.",
                    "assistive_only": True,
                }
            ),
        ]
    )

    def _fake_call_responses_api(**_: object) -> dict[str, object]:
        call_count["value"] += 1
        return {"id": f"resp-{call_count['value']}", "status": "completed", "usage": {"input_tokens": 12, "output_tokens": 8, "total_tokens": 20}}

    def _fake_extract_response_text(_: dict[str, object]) -> str:
        return next(response_texts)

    def _fake_cost_controller(_: str):
        controller = CostController(
            policy={},
            usage_file=usage_file,
            cache_dir=tmp_path / "cache",
        )
        return controller, {}

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(
        "ai_washing_member.labeling.assistive_prelabel_batch.call_responses_api",
        _fake_call_responses_api,
    )
    monkeypatch.setattr(
        "ai_washing_member.labeling.assistive_prelabel_batch.extract_response_text",
        _fake_extract_response_text,
    )
    monkeypatch.setattr(
        "ai_washing_member.labeling.assistive_prelabel_batch._build_cost_controller",
        _fake_cost_controller,
    )

    report, exit_code = generate_assistive_prelabels(
        input_csv=str(input_csv),
        output_csv=str(output_csv),
        report_path=str(report_path),
        policy_path=str(policy_path),
        mode="live",
        checkpoint_every=1,
    )

    output = pd.read_csv(output_csv)
    assert exit_code == 0
    assert report["status"] == "passed"
    assert output.loc[0, "assistive_label"] == "Actionable"
    assert call_count["value"] == 2
