from __future__ import annotations

from pathlib import Path

from ai_washing_member.classification import model_runtime as runtime_module
from ai_washing_member.classification.model_runtime import (
    build_legacy_two_stage_runtime,
    build_selective_defer_runtime,
    predict_sentences_with_metadata,
)
from ai_washing_member.classification.preliminary_pipeline import (
    _resolve_sentence_transformer_source,
    sha256_file,
)


def test_member_preliminary_pipeline_prefers_cached_snapshot(tmp_path: Path, monkeypatch) -> None:
    hub_root = tmp_path / "hf-cache"
    repo_root = hub_root / "models--sentence-transformers--all-mpnet-base-v2"
    snapshot = repo_root / "snapshots" / "abc123"
    snapshot.mkdir(parents=True)
    refs = repo_root / "refs"
    refs.mkdir(parents=True)
    (refs / "main").write_text("abc123\n", encoding="utf-8")
    monkeypatch.setenv("HUGGINGFACE_HUB_CACHE", str(hub_root))

    resolved = _resolve_sentence_transformer_source("sentence-transformers/all-mpnet-base-v2")

    assert resolved == str(snapshot)


def test_member_classification_support_helpers_smoke(tmp_path: Path) -> None:
    payload = tmp_path / "payload.txt"
    payload.write_text("alpha", encoding="utf-8")

    runtime = build_legacy_two_stage_runtime(model_id="legacy-test", tau=0.11, min_tokens=8)

    assert runtime["model_id"] == "legacy-test"
    assert runtime["runtime"]["tau"] == 0.11
    assert runtime["runtime"]["min_tokens"] == 8
    assert len(sha256_file(payload)) == 64


def test_member_selective_defer_runtime_uses_api_on_low_confidence(monkeypatch) -> None:
    runtime_manifest = {
        "model_id": "selective_defer_layered_api_a_conf49_v1",
        "model_type": "selective_defer_layered_api_a",
        "runtime": {
            "api_a_policy": "director/config/api_assistive_policy_heldout_v3_mini_high_output.yaml",
            "defer_low_confidence_threshold": 0.49,
        },
    }

    monkeypatch.setattr(
        runtime_module,
        "_predict_layered_local_rows",
        lambda _sentences, _runtime: [
            {
                "scores": {
                    "Actionable": 0.44,
                    "Speculative": 0.43,
                    "Irrelevant": 0.13,
                },
                "local_label": "Actionable",
                "local_confidence": 0.44,
                "conditional_as_margin": 0.01,
                "binary_label": "Non-Irrelevant",
                "logreg_label": "Actionable",
                "binary_logreg_relevance_disagreement": False,
            },
            {
                "scores": {
                    "Actionable": 0.82,
                    "Speculative": 0.11,
                    "Irrelevant": 0.07,
                },
                "local_label": "Actionable",
                "local_confidence": 0.82,
                "conditional_as_margin": 0.71,
                "binary_label": "Non-Irrelevant",
                "logreg_label": "Actionable",
                "binary_logreg_relevance_disagreement": False,
            },
        ],
    )
    monkeypatch.setattr(
        runtime_module,
        "_call_assistive_label",
        lambda *, sentence, source_section, policy_path: {
            "api_a_label": "Speculative",
            "api_a_confidence": "high",
            "api_a_rationale": f"api for {sentence}",
            "api_a_model": "gpt-5-mini",
        },
    )

    predicted, score_rows, metadata_rows = predict_sentences_with_metadata(
        ["low confidence sentence", "high confidence sentence"],
        runtime_manifest,
        source_sections=["", ""],
    )

    assert predicted == ["Speculative", "Actionable"]
    assert score_rows[0]["Actionable"] == 0.44
    assert metadata_rows[0]["deferred_to_api"] is True
    assert metadata_rows[0]["prediction_source"] == "api_a"
    assert metadata_rows[0]["api_a_label"] == "Speculative"
    assert metadata_rows[1]["deferred_to_api"] is False
    assert metadata_rows[1]["prediction_source"] == "local"


def test_member_build_selective_defer_runtime_smoke(tmp_path: Path) -> None:
    binary_meta = tmp_path / "binary.json"
    logreg_meta = tmp_path / "logreg.json"
    policy = tmp_path / "policy.yaml"
    binary_meta.write_text(
        '{"source_window_id":"active_2021_2024","runtime":{"relevance_model_pickle":"rel.pkl","relevance_model_pickle_sha256":"abc","embedding_backend":"hash","model_name":"hash://bow","hash_dim":32,"batch_size":8}}',
        encoding="utf-8",
    )
    logreg_meta.write_text(
        '{"runtime":{"model_pickle":"log.pkl","model_pickle_sha256":"def","embedding_backend":"hash","model_name":"hash://bow","hash_dim":32,"batch_size":8}}',
        encoding="utf-8",
    )
    policy.write_text("mode: assistive_only\nprovider: openai\ntransport: responses_api\nenv_var: OPENAI_API_KEY\nmodel: gpt-5-mini\nrequest: {store: false, timeout_seconds: 60, max_output_tokens: 600}\nbudget: {max_live_requests_per_run: 1, max_prompt_tokens_per_call: 1400, max_output_tokens_per_call: 600, max_estimated_cost_usd_per_run: 5.0}\nselection: {sample_input: sample.csv, min_tokens: 12, max_tokens: 220, require_fragment_score_max: 0.0}\ntelemetry: {usage_file: director/runs/cost_usage.jsonl, component: test, cache_allowed: false}\nusage_policy: {canonical: false, allowed_use_cases: [defer_validation], prohibited_use_cases: [canonical_training_labels]}\nprompt_spec: {reference_rubric_path: projects/ai_washing/docs/track_a_as_rubric_rewrite_v1.md, label_set: [Actionable, Speculative, Irrelevant], confidence_bands: [high, medium, low], system_prompt: test, user_prompt_template: test}\nsmoke_output: {report_path: out.json}\n", encoding="utf-8")

    runtime = build_selective_defer_runtime(
        binary_metadata_path=binary_meta,
        logreg_metadata_path=logreg_meta,
        api_policy_path=policy,
        low_confidence_threshold=0.49,
    )

    assert runtime["model_type"] == "selective_defer_layered_api_a"
    assert runtime["runtime"]["defer_low_confidence_threshold"] == 0.49
    assert runtime["runtime"]["api_a_policy"] == str(policy)
