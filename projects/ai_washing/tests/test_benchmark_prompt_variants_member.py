from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ai_washing_member.labeling.benchmark_prompt_variants import benchmark_prompt_variants


def test_benchmark_prompt_variants_member_selects_winner(tmp_path, monkeypatch) -> None:
    input_rows = []
    benchmark_rows = []
    manual_labels = ["Actionable"] * 5 + ["Speculative"] * 7 + ["Irrelevant"] * 28
    for index, label in enumerate(manual_labels, start=1):
        input_rows.append(
            {
                "sentence_id": f"s{index}",
                "sentence": f"Sentence {index}",
                "label": "",
                "source_file": f"f{index}.txt",
                "sentence_index": index,
                "source_section": "item_1_business",
            }
        )
        benchmark_rows.append({"sentence_id": f"s{index}", "label": label})

    input_csv = tmp_path / "input.csv"
    benchmark_csv = tmp_path / "benchmark.csv"
    input_csv.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(input_rows).to_csv(input_csv, index=False)
    pd.DataFrame(benchmark_rows).to_csv(benchmark_csv, index=False)

    base_policy = tmp_path / "policy.yaml"
    base_policy.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "mode": "assistive_only",
                "provider": "openai",
                "transport": "responses_api",
                "env_var": "OPENAI_API_KEY",
                "model": "gpt-5-mini",
                "request": {"store": False, "timeout_seconds": 60, "max_output_tokens": 50},
                "budget": {"max_live_requests_per_run": 1},
                "selection": {
                    "sample_input": "sample.csv",
                    "min_tokens": 1,
                    "max_tokens": 10,
                    "require_fragment_score_max": 0.0,
                },
                "telemetry": {
                    "usage_file": "director/runs/cost_usage.jsonl",
                    "component": "assistive_prelabel_smoke",
                    "cache_allowed": False,
                },
                "usage_policy": {
                    "canonical": False,
                    "allowed_use_cases": ["bounded_smoke_test"],
                    "prohibited_use_cases": ["canonical_training_labels"],
                },
                "prompt_spec": {
                    "reference_rubric_path": "docs/labeling_protocol.md",
                    "label_set": ["Actionable", "Speculative", "Irrelevant"],
                    "confidence_bands": ["high", "medium", "low"],
                    "system_prompt": "base",
                    "user_prompt_template": "base",
                },
                "smoke_output": {"report_path": "report.json"},
            }
        ),
        encoding="utf-8",
    )
    variants = tmp_path / "variants.yaml"
    variants.write_text(
        """
schema_version: "1.0.0"
version_family: "v2.4"
variants:
  - variant_id: "v2_4a"
    label: "weak"
    description: "weak"
    system_prompt: "variant a"
    user_prompt_template: "variant a"
  - variant_id: "v2_4b"
    label: "strong"
    description: "strong"
    system_prompt: "variant b"
    user_prompt_template: "variant b"
""",
        encoding="utf-8",
    )

    def fake_generate_assistive_prelabels(
        *, input_csv: str, output_csv: str, report_path: str, policy_path: str, **_: object
    ):
        policy_text = Path(policy_path).read_text(encoding="utf-8")
        rows = pd.read_csv(input_csv)
        if "variant b" in policy_text:
            labels = ["Actionable"] * 5 + ["Speculative"] * 5 + ["Irrelevant"] * 30
        else:
            labels = ["Irrelevant"] * 2 + ["Speculative"] * 10 + ["Irrelevant"] * 28
        rows["assistive_label"] = labels
        rows["assistive_confidence"] = "high"
        rows["assistive_rationale"] = "test"
        rows["assistive_model"] = "gpt-5-mini"
        rows["assistive_generated_at"] = "2026-03-10T00:00:00Z"
        rows["assistive_prompt_hash"] = "hash"
        Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
        rows.to_csv(output_csv, index=False)
        payload = {"status": "passed", "usage": {"request_count": len(rows)}}
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        Path(report_path).write_text(json.dumps(payload), encoding="utf-8")
        return payload, 0

    monkeypatch.setattr(
        "ai_washing_member.labeling.benchmark_prompt_variants.generate_assistive_prelabels",
        fake_generate_assistive_prelabels,
    )

    result = benchmark_prompt_variants(
        input_csv=str(input_csv),
        benchmark_csv=str(benchmark_csv),
        base_policy_path=str(base_policy),
        variants_path=str(variants),
        report_json=str(tmp_path / "benchmark.json"),
        report_md=str(tmp_path / "benchmark.md"),
        regenerate_full_on_success=False,
    )

    assert result["winner"]["variant_id"] == "v2_4b"
    assert result["winner"]["gate_passed"] is True
