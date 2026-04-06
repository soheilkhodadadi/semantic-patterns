from __future__ import annotations

import json
import pandas as pd
import yaml

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
