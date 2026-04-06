from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from semantic_ai_washing.data.build_expanded_sentence_pool import build_expanded_sentence_pool
from semantic_ai_washing.data.combine_expanded_sentence_pool_batches import (
    combine_expanded_sentence_pool_batches,
)
from semantic_ai_washing.director.core.api_assistive import (
    build_prompt_messages,
    load_api_assistive_policy,
)
from semantic_ai_washing.director.core.cost import CostController
from semantic_ai_washing.labeling.assistive_prelabel_batch import generate_assistive_prelabels
from semantic_ai_washing.labeling.benchmark_prompt_variants import benchmark_prompt_variants
from ai_washing_member.labeling.build_labeling_batch import build_labeling_batch
from semantic_ai_washing.labeling.initialize_review_sheet import initialize_review_sheet
from semantic_ai_washing.labeling.merge_labeling_batches import merge_labeling_batches
from semantic_ai_washing.labeling.score_prelabel_sheet import score_prelabel_sheet


def _write_csv(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def _make_index_and_source_root(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    source_root = tmp_path / "sec-root"
    controls = tmp_path / "controls.csv"
    crosswalk = tmp_path / "crosswalk.csv"
    keywords = tmp_path / "keywords.txt"

    filing_rows = []
    texts = {
        "2024/QTR1/f1.txt": "We use artificial intelligence in day to day operations today. Machine learning improves support forecasting across customer service teams.",
        "2024/QTR2/f2.txt": "Our artificial intelligence systems are deployed in compliance review workflows today. Machine learning helps current monitoring across the control function.",
        "2024/QTR3/f3.txt": "Artificial intelligence supports underwriting decisions in current production workflows. Machine learning improves current risk management across operating units.",
        "2024/QTR4/f4.txt": "We currently deploy artificial intelligence for analytics in core internal workflows. Machine learning improves ongoing planning and resource allocation decisions.",
    }
    cik_map = {
        "2024/QTR1/f1.txt": "1001",
        "2024/QTR2/f2.txt": "1002",
        "2024/QTR3/f3.txt": "1003",
        "2024/QTR4/f4.txt": "1004",
    }

    for relative_path, text in texts.items():
        file_path = source_root / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(text, encoding="utf-8")
        quarter = int(relative_path.split("/")[1].replace("QTR", ""))
        filing_rows.append(
            {
                "cik": cik_map[relative_path],
                "year": 2024,
                "quarter": quarter,
                "form": "10-K",
                "filename": Path(relative_path).name,
                "path": relative_path,
                "source_root": str(source_root),
                "index_timestamp": "2026-03-07T00:00:00Z",
                "source_window_id": "active_2021_2024",
            }
        )

    index_path = tmp_path / "available_filings_index.csv"
    pd.DataFrame(filing_rows).to_csv(index_path, index=False)
    _write_csv(
        controls,
        [
            {"cik": "1001", "year": 2024, "sic": 3571},
            {"cik": "1002", "year": 2024, "sic": 3571},
            {"cik": "1003", "year": 2024, "sic": 3571},
            {"cik": "1004", "year": 2024, "sic": 3571},
        ],
    )
    _write_csv(crosswalk, [{"cik": "1001", "sic": 3571}])
    keywords.write_text("artificial intelligence\nmachine learning\n", encoding="utf-8")
    return index_path, source_root, controls, keywords


def test_build_expanded_sentence_pool_is_deterministic(tmp_path):
    index_path, source_root, controls, keywords = _make_index_and_source_root(tmp_path)
    crosswalk = tmp_path / "crosswalk.csv"

    manifest_a = tmp_path / "manifest_a.csv"
    sentences_a = tmp_path / "sentences_a.parquet"
    report_a = tmp_path / "report_a.json"
    manifest_b = tmp_path / "manifest_b.csv"
    sentences_b = tmp_path / "sentences_b.parquet"
    report_b = tmp_path / "report_b.json"

    build_expanded_sentence_pool(
        index_path=str(index_path),
        output_manifest_path=str(manifest_a),
        output_sentences_path=str(sentences_a),
        report_path=str(report_a),
        controls_path=str(controls),
        crosswalk_path=str(crosswalk),
        keywords_path=str(keywords),
        source_root=str(source_root),
        target_firms=4,
        min_clean_sentences=4,
        manifest_id="test_expansion",
        seed=123,
    )
    build_expanded_sentence_pool(
        index_path=str(index_path),
        output_manifest_path=str(manifest_b),
        output_sentences_path=str(sentences_b),
        report_path=str(report_b),
        controls_path=str(controls),
        crosswalk_path=str(crosswalk),
        keywords_path=str(keywords),
        source_root=str(source_root),
        target_firms=4,
        min_clean_sentences=4,
        manifest_id="test_expansion",
        seed=123,
    )

    manifest_df_a = pd.read_csv(manifest_a)
    manifest_df_b = pd.read_csv(manifest_b)
    sentence_df_a = pd.read_parquet(sentences_a)
    sentence_df_b = pd.read_parquet(sentences_b)
    report_payload = json.loads(report_a.read_text(encoding="utf-8"))

    assert manifest_df_a.equals(manifest_df_b)
    assert sentence_df_a.equals(sentence_df_b)
    assert len(manifest_df_a) == 4
    assert report_payload["candidate_pool"]["clean_sentence_count"] >= 4
    assert report_payload["selection"]["firm_target_satisfied"] is True
    assert report_payload["selection"]["clean_sentence_target_satisfied"] is True


def test_build_expanded_sentence_pool_targets_unique_firms(tmp_path):
    index_path, source_root, controls, keywords = _make_index_and_source_root(tmp_path)
    crosswalk = tmp_path / "crosswalk.csv"

    index_df = pd.read_csv(index_path)
    duplicate_row = index_df.iloc[0].copy()
    duplicate_row["quarter"] = 2
    duplicate_row["filename"] = "f1_duplicate.txt"
    duplicate_row["path"] = "2024/QTR2/f1_duplicate.txt"
    pd.concat([index_df, pd.DataFrame([duplicate_row])], ignore_index=True).to_csv(
        index_path, index=False
    )
    (source_root / "2024/QTR2/f1_duplicate.txt").write_text(
        "Artificial intelligence supports current finance operations today.",
        encoding="utf-8",
    )

    manifest = tmp_path / "manifest.csv"
    sentences = tmp_path / "sentences.parquet"
    report = tmp_path / "report.json"

    payload = build_expanded_sentence_pool(
        index_path=str(index_path),
        output_manifest_path=str(manifest),
        output_sentences_path=str(sentences),
        report_path=str(report),
        controls_path=str(controls),
        crosswalk_path=str(crosswalk),
        keywords_path=str(keywords),
        source_root=str(source_root),
        target_firms=4,
        min_clean_sentences=4,
        manifest_id="test_expansion_unique_firms",
        seed=456,
    )

    manifest_df = pd.read_csv(manifest)

    assert int(manifest_df["cik"].astype(str).nunique()) == 4
    assert len(manifest_df) == 4
    assert payload["candidate_pool"]["firm_count"] == 4


def test_build_expanded_sentence_pool_excludes_prior_batch_manifests(tmp_path):
    index_path, source_root, controls, keywords = _make_index_and_source_root(tmp_path)
    crosswalk = tmp_path / "crosswalk.csv"

    batch1_manifest = tmp_path / "batch1_manifest.csv"
    batch1_sentences = tmp_path / "batch1_sentences.parquet"
    batch1_report = tmp_path / "batch1_report.json"
    build_expanded_sentence_pool(
        index_path=str(index_path),
        output_manifest_path=str(batch1_manifest),
        output_sentences_path=str(batch1_sentences),
        report_path=str(batch1_report),
        controls_path=str(controls),
        crosswalk_path=str(crosswalk),
        keywords_path=str(keywords),
        source_root=str(source_root),
        target_firms=2,
        min_clean_sentences=2,
        manifest_id="expansion_batch_01",
        seed=100,
    )

    batch2_manifest = tmp_path / "batch2_manifest.csv"
    batch2_sentences = tmp_path / "batch2_sentences.parquet"
    batch2_report = tmp_path / "batch2_report.json"
    payload = build_expanded_sentence_pool(
        index_path=str(index_path),
        output_manifest_path=str(batch2_manifest),
        output_sentences_path=str(batch2_sentences),
        report_path=str(batch2_report),
        controls_path=str(controls),
        crosswalk_path=str(crosswalk),
        keywords_path=str(keywords),
        source_root=str(source_root),
        target_firms=2,
        min_clean_sentences=2,
        manifest_id="expansion_batch_02",
        seed=101,
        exclude_manifest_paths=[str(batch1_manifest)],
    )

    batch1_ciks = set(pd.read_csv(batch1_manifest)["cik"].astype(str))
    batch2_ciks = set(pd.read_csv(batch2_manifest)["cik"].astype(str))

    assert batch1_ciks.isdisjoint(batch2_ciks)
    assert payload["manifest"]["excluded_prior_firm_count"] == 2
    assert payload["selection"]["excluded_prior_firms"] == 2


def test_combine_expanded_sentence_pool_batches_writes_cumulative_outputs(tmp_path):
    batch1_manifest = _write_csv(
        tmp_path / "batch1_manifest.csv",
        [
            {
                "manifest_id": "batch1",
                "manifest_row_id": "m1",
                "cik": "1001",
                "quarter": 1,
                "filename": "f1.txt",
                "path": "2024/QTR1/f1.txt",
                "industry_metadata_source": "controls",
            }
        ],
    )
    batch2_manifest = _write_csv(
        tmp_path / "batch2_manifest.csv",
        [
            {
                "manifest_id": "batch2",
                "manifest_row_id": "m2",
                "cik": "1002",
                "quarter": 2,
                "filename": "f2.txt",
                "path": "2024/QTR2/f2.txt",
                "industry_metadata_source": "unknown",
            }
        ],
    )
    batch1_sentences = tmp_path / "batch1_sentences.parquet"
    pd.DataFrame(
        [
            {
                "sentence_id": "s1",
                "sentence_text_id": "t1",
                "sentence": "AI improves current workflows.",
                "sentence_norm": "ai improves current workflows",
                "source_file": "2024/QTR1/f1.txt",
                "source_year": 2024,
                "source_quarter": 1,
                "source_form": "10-K",
                "source_cik": "1001",
                "sentence_index": 1,
                "manifest_id": "batch1",
                "source_window_id": "active_2021_2024",
                "token_count": 4,
                "fragment_score": 0.0,
                "integrity_flags": "",
            }
        ]
    ).to_parquet(batch1_sentences, index=False)
    batch2_sentences = tmp_path / "batch2_sentences.parquet"
    pd.DataFrame(
        [
            {
                "sentence_id": "s2",
                "sentence_text_id": "t2",
                "sentence": "Machine learning supports current planning.",
                "sentence_norm": "machine learning supports current planning",
                "source_file": "2024/QTR2/f2.txt",
                "source_year": 2024,
                "source_quarter": 2,
                "source_form": "10-K",
                "source_cik": "1002",
                "sentence_index": 1,
                "manifest_id": "batch2",
                "source_window_id": "active_2021_2024",
                "token_count": 5,
                "fragment_score": 0.0,
                "integrity_flags": "",
            }
        ]
    ).to_parquet(batch2_sentences, index=False)

    output_manifest = tmp_path / "combined_manifest.csv"
    output_sentences = tmp_path / "combined_sentences.parquet"
    report_path = tmp_path / "combined_report.json"
    report = combine_expanded_sentence_pool_batches(
        manifest_paths=[str(batch1_manifest), str(batch2_manifest)],
        sentence_paths=[str(batch1_sentences), str(batch2_sentences)],
        output_manifest_path=str(output_manifest),
        output_sentences_path=str(output_sentences),
        report_path=str(report_path),
    )

    assert output_manifest.exists()
    assert output_sentences.exists()
    assert report["candidate_pool"]["firm_count"] == 2
    assert report["candidate_pool"]["clean_sentence_count"] == 2
    assert report["quality"]["duplicate_firm_count"] == 0
    assert report["quality"]["post_combine_duplicate_sentence_text_count"] == 0


def test_generate_assistive_prelabels_keeps_canonical_label_blank(monkeypatch, tmp_path):
    input_csv = _write_csv(
        tmp_path / "labeling_batch.csv",
        [
            {
                "sentence_id": "s1",
                "sentence": "We use artificial intelligence in operations today.",
                "source_file": "2024/QTR1/f1.txt",
                "sentence_index": 1,
                "label": "",
            },
            {
                "sentence_id": "s2",
                "sentence": "We may use AI in the future.",
                "source_file": "2024/QTR2/f2.txt",
                "sentence_index": 2,
                "label": "Speculative",
            },
        ],
    )
    output_csv = tmp_path / "labeling_batch_prelabeled.csv"
    report_path = tmp_path / "assistive_prelabel_summary.json"
    usage_file = tmp_path / "cost_usage.jsonl"

    def _fake_call_responses_api(**_: object) -> dict[str, object]:
        return {"usage": {"input_tokens": 12, "output_tokens": 8, "total_tokens": 20}}

    def _fake_extract_response_text(_: dict[str, object]) -> str:
        return json.dumps(
            {
                "label": "Actionable",
                "confidence": "high",
                "rationale": "Current operational use is explicit.",
                "assistive_only": True,
            }
        )

    def _fake_cost_controller(_: str):
        controller = CostController(
            policy={},
            usage_file=usage_file,
            cache_dir=tmp_path / "cache",
        )
        return controller, {}

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(
        "semantic_ai_washing.labeling.assistive_prelabel_batch.call_responses_api",
        _fake_call_responses_api,
    )
    monkeypatch.setattr(
        "semantic_ai_washing.labeling.assistive_prelabel_batch.extract_response_text",
        _fake_extract_response_text,
    )
    monkeypatch.setattr(
        "semantic_ai_washing.labeling.assistive_prelabel_batch._build_cost_controller",
        _fake_cost_controller,
    )

    report, exit_code = generate_assistive_prelabels(
        input_csv=str(input_csv),
        output_csv=str(output_csv),
        report_path=str(report_path),
        policy_path="director/config/api_assistive_policy.yaml",
        mode="live",
    )

    output = pd.read_csv(output_csv)

    assert exit_code == 0
    assert report["status"] == "passed"
    assert output.loc[0, "label"] != output.loc[0, "assistive_label"]
    assert output.loc[0, "label"] != "Actionable"
    assert output.loc[0, "assistive_label"] == "Actionable"
    assert output.loc[1, "label"] == "Speculative"
    assert pd.isna(output.loc[1, "assistive_label"]) or output.loc[1, "assistive_label"] == ""
    assert report["usage"]["request_count"] == 1
    assert usage_file.exists()


def test_generate_assistive_prelabels_skips_ineligible_unmatched_noise_rows(monkeypatch, tmp_path):
    input_csv = _write_csv(
        tmp_path / "labeling_batch.csv",
        [
            {
                "sentence_id": "noise",
                "sentence": "",
                "source_file": "2024/QTR1/f1.txt",
                "sentence_index": 1,
                "label": "",
                "prelabel_eligible": False,
                "skip_reason": "unmatched_noise",
            },
            {
                "sentence_id": "s1",
                "sentence": "We offer artificial intelligence enabled products today.",
                "source_file": "2024/QTR1/f1.txt",
                "sentence_index": 2,
                "label": "",
                "prelabel_eligible": True,
                "skip_reason": "",
            },
        ],
    )
    output_csv = tmp_path / "labeling_batch_prelabeled.csv"
    report_path = tmp_path / "assistive_prelabel_summary.json"
    usage_file = tmp_path / "cost_usage.jsonl"

    def _fake_call_responses_api(**_: object) -> dict[str, object]:
        return {"usage": {"input_tokens": 12, "output_tokens": 8, "total_tokens": 20}}

    def _fake_extract_response_text(_: dict[str, object]) -> str:
        return json.dumps(
            {
                "label": "Actionable",
                "confidence": "high",
                "rationale": "Present-tense offering claim is factual.",
                "assistive_only": True,
            }
        )

    def _fake_cost_controller(_: str):
        controller = CostController(
            policy={},
            usage_file=usage_file,
            cache_dir=tmp_path / "cache",
        )
        return controller, {}

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(
        "semantic_ai_washing.labeling.assistive_prelabel_batch.call_responses_api",
        _fake_call_responses_api,
    )
    monkeypatch.setattr(
        "semantic_ai_washing.labeling.assistive_prelabel_batch.extract_response_text",
        _fake_extract_response_text,
    )
    monkeypatch.setattr(
        "semantic_ai_washing.labeling.assistive_prelabel_batch._build_cost_controller",
        _fake_cost_controller,
    )

    report, exit_code = generate_assistive_prelabels(
        input_csv=str(input_csv),
        output_csv=str(output_csv),
        report_path=str(report_path),
        policy_path="director/config/api_assistive_policy.yaml",
        mode="live",
    )

    output = pd.read_csv(output_csv)

    assert exit_code == 0
    assert report["status"] == "passed"
    assert report["counts"]["skipped_unmatched_noise_rows"] == 1
    assert report["counts"]["skipped_blank_sentence_rows"] == 0
    assert report["usage"]["request_count"] == 1
    assert output.loc[0, "assistive_label"] in ("", None) or pd.isna(
        output.loc[0, "assistive_label"]
    )
    assert output.loc[1, "assistive_label"] == "Actionable"


def test_generate_assistive_prelabels_flushes_checkpoint_progress(monkeypatch, tmp_path):
    input_csv = _write_csv(
        tmp_path / "labeling_batch.csv",
        [
            {
                "sentence_id": "s1",
                "sentence": "We use artificial intelligence in operations today.",
                "source_file": "2024/QTR1/f1.txt",
                "sentence_index": 1,
                "label": "",
            },
            {
                "sentence_id": "s2",
                "sentence": "We currently use machine learning in underwriting.",
                "source_file": "2024/QTR2/f2.txt",
                "sentence_index": 2,
                "label": "",
            },
        ],
    )
    output_csv = tmp_path / "labeling_batch_prelabeled.csv"
    report_path = tmp_path / "assistive_prelabel_summary.json"
    usage_file = tmp_path / "cost_usage.jsonl"

    call_count = {"value": 0}

    def _fake_call_responses_api(**_: object) -> dict[str, object]:
        call_count["value"] += 1
        if call_count["value"] == 2:
            raise OpenAIResponsesHTTPError(500, "boom", "")
        return {"usage": {"input_tokens": 12, "output_tokens": 8, "total_tokens": 20}}

    def _fake_extract_response_text(_: dict[str, object]) -> str:
        return json.dumps(
            {
                "label": "Actionable",
                "confidence": "high",
                "rationale": "Current operational use is explicit.",
                "assistive_only": True,
            }
        )

    def _fake_cost_controller(_: str):
        controller = CostController(
            policy={},
            usage_file=usage_file,
            cache_dir=tmp_path / "cache",
        )
        return controller, {}

    from semantic_ai_washing.director.core.openai_responses import OpenAIResponsesHTTPError

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(
        "semantic_ai_washing.labeling.assistive_prelabel_batch.call_responses_api",
        _fake_call_responses_api,
    )
    monkeypatch.setattr(
        "semantic_ai_washing.labeling.assistive_prelabel_batch.extract_response_text",
        _fake_extract_response_text,
    )
    monkeypatch.setattr(
        "semantic_ai_washing.labeling.assistive_prelabel_batch._build_cost_controller",
        _fake_cost_controller,
    )

    report, exit_code = generate_assistive_prelabels(
        input_csv=str(input_csv),
        output_csv=str(output_csv),
        report_path=str(report_path),
        policy_path="director/config/api_assistive_policy.yaml",
        mode="live",
        checkpoint_every=1,
    )

    output = pd.read_csv(output_csv)

    assert exit_code == 1
    assert report["status"] == "request_failed"
    assert output.loc[0, "assistive_label"] == "Actionable"
    assert output.loc[1, "assistive_label"] in ("", None) or pd.isna(
        output.loc[1, "assistive_label"]
    )
    assert report["counts"]["processed_rows"] == 1


def test_generate_assistive_prelabels_returns_success_for_bounded_chunk_resume(
    monkeypatch, tmp_path
):
    input_csv = _write_csv(
        tmp_path / "labeling_batch.csv",
        [
            {
                "sentence_id": "s1",
                "sentence": "We use artificial intelligence in operations today.",
                "source_file": "2024/QTR1/f1.txt",
                "sentence_index": 1,
                "label": "",
            },
            {
                "sentence_id": "s2",
                "sentence": "We currently use machine learning in underwriting.",
                "source_file": "2024/QTR2/f2.txt",
                "sentence_index": 2,
                "label": "",
            },
        ],
    )
    output_csv = tmp_path / "labeling_batch_prelabeled.csv"
    report_path = tmp_path / "assistive_prelabel_summary.json"
    usage_file = tmp_path / "cost_usage.jsonl"

    def _fake_call_responses_api(**_: object) -> dict[str, object]:
        return {"usage": {"input_tokens": 12, "output_tokens": 8, "total_tokens": 20}}

    def _fake_extract_response_text(_: dict[str, object]) -> str:
        return json.dumps(
            {
                "label": "Actionable",
                "confidence": "high",
                "rationale": "Current operational use is explicit.",
                "assistive_only": True,
            }
        )

    def _fake_cost_controller(_: str):
        controller = CostController(
            policy={},
            usage_file=usage_file,
            cache_dir=tmp_path / "cache",
        )
        return controller, {}

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(
        "semantic_ai_washing.labeling.assistive_prelabel_batch.call_responses_api",
        _fake_call_responses_api,
    )
    monkeypatch.setattr(
        "semantic_ai_washing.labeling.assistive_prelabel_batch.extract_response_text",
        _fake_extract_response_text,
    )
    monkeypatch.setattr(
        "semantic_ai_washing.labeling.assistive_prelabel_batch._build_cost_controller",
        _fake_cost_controller,
    )

    report, exit_code = generate_assistive_prelabels(
        input_csv=str(input_csv),
        output_csv=str(output_csv),
        report_path=str(report_path),
        policy_path="director/config/api_assistive_policy.yaml",
        mode="live",
        max_rows=1,
        checkpoint_every=1,
    )

    output = pd.read_csv(output_csv)
    assert exit_code == 0
    assert report["status"] == "in_progress"
    assert report["counts"]["processed_rows"] == 1
    assert report["counts"]["pending_rows_after_run"] == 1
    assert output["assistive_label"].fillna("").astype(str).eq("Actionable").sum() == 1

    report_2, exit_code_2 = generate_assistive_prelabels(
        input_csv=str(input_csv),
        output_csv=str(output_csv),
        report_path=str(report_path),
        policy_path="director/config/api_assistive_policy.yaml",
        mode="live",
        max_rows=1,
        checkpoint_every=1,
    )

    output_2 = pd.read_csv(output_csv)
    assert exit_code_2 == 0
    assert report_2["status"] == "passed"
    assert report_2["counts"]["processed_rows"] == 1
    assert report_2["counts"]["pending_rows_after_run"] == 0
    assert report_2["usage"]["request_count"] == 2
    assert output_2["assistive_label"].fillna("").astype(str).eq("Actionable").sum() == 2


def test_initialize_review_sheet_creates_blank_canonical_columns_and_slice(tmp_path):
    input_csv = _write_csv(
        tmp_path / "prelabeled.csv",
        [
            {
                "sentence_id": "s1",
                "sentence": "We use artificial intelligence in operations today.",
                "source_file": "2024/QTR1/f1.txt",
                "sentence_index": 1,
                "label": "Speculative",
                "is_uncertain": "1",
                "uncertainty_note": "old note",
                "assistive_label": "Actionable",
            },
            {
                "sentence_id": "s2",
                "sentence": "We may use AI in the future.",
                "source_file": "2024/QTR2/f2.txt",
                "sentence_index": 2,
                "label": "",
                "is_uncertain": "",
                "uncertainty_note": "",
                "assistive_label": "Speculative",
            },
        ],
    )
    output_csv = tmp_path / "filled_v2_1.csv"
    slice_csv = tmp_path / "filled_v2_1_slice40.csv"

    total_rows, slice_rows = initialize_review_sheet(
        input_csv=str(input_csv),
        output_csv=str(output_csv),
        slice_output_csv=str(slice_csv),
        slice_size=1,
    )

    written = pd.read_csv(output_csv)
    slice_written = pd.read_csv(slice_csv)

    assert total_rows == 2
    assert slice_rows == 1
    assert written["label"].fillna("").tolist() == ["", ""]
    assert written["is_uncertain"].fillna("").tolist() == ["", ""]
    assert written["uncertainty_note"].fillna("").tolist() == ["", ""]
    assert written["assistive_label"].tolist() == ["Actionable", "Speculative"]
    assert len(slice_written) == 1


def test_initialize_review_sheet_can_carry_forward_existing_review_labels(tmp_path):
    input_csv = _write_csv(
        tmp_path / "prelabeled.csv",
        [
            {
                "sentence_id": "s1",
                "sentence": "We use artificial intelligence in operations today.",
                "assistive_label": "Actionable",
            },
            {
                "sentence_id": "s2",
                "sentence": "We may use AI in the future.",
                "assistive_label": "Speculative",
            },
        ],
    )
    existing_review_csv = _write_csv(
        tmp_path / "existing_review.csv",
        [
            {
                "sentence_id": "s1",
                "label": "Actionable",
                "is_uncertain": "",
                "uncertainty_note": "",
            },
            {
                "sentence_id": "s2",
                "label": "",
                "is_uncertain": "1",
                "uncertainty_note": "needs follow-up",
            },
        ],
    )
    output_csv = tmp_path / "filled_v2_4.csv"

    total_rows, slice_rows = initialize_review_sheet(
        input_csv=str(input_csv),
        output_csv=str(output_csv),
        existing_review_csv=str(existing_review_csv),
    )

    written = pd.read_csv(output_csv)

    assert total_rows == 2
    assert slice_rows == 0
    assert written["label"].fillna("").tolist() == ["Actionable", ""]
    assert written["is_uncertain"].fillna("").astype(str).replace("nan", "").tolist() == [
        "",
        "1.0",
    ]
    assert written["uncertainty_note"].fillna("").tolist() == ["", "needs follow-up"]
    assert written["assistive_label"].tolist() == ["Actionable", "Speculative"]


def test_build_prompt_messages_includes_section_context_and_v24_rules():
    policy, _ = load_api_assistive_policy(
        "director/config/api_assistive_policy.yaml",
        repo_root=".",
    )

    messages = build_prompt_messages(
        policy,
        "Artificial intelligence could expose us to cyber risks.",
        source_section="item_1a_risk_factors",
    )

    system_text = messages[0]["content"][0]["text"]
    user_text = messages[1]["content"][0]["text"]
    combined = f"{system_text}\n{user_text}"

    assert "present or past factual claim" in combined
    assert "primary function of the sentence is risk disclosure" in combined
    assert "Source section: item_1a_risk_factors" in user_text


def test_build_labeling_batch_excludes_multiple_prior_batches(tmp_path):
    sentences_path = tmp_path / "sentences.parquet"
    manifest_path = tmp_path / "manifest.csv"
    held_out_path = _write_csv(
        tmp_path / "held_out.csv",
        [{"sentence": "held out sentence"}],
    )
    pd.DataFrame(
        [
            {
                "sentence_id": "s1",
                "sentence_text_id": "t1",
                "sentence": "We use AI in operations.",
                "sentence_norm": "we use ai in operations",
                "source_file": "2024/QTR1/f1.txt",
                "source_year": 2024,
                "source_quarter": 1,
                "source_form": "10-K",
                "source_cik": "1001",
                "sentence_index": 1,
                "manifest_id": "m1",
                "source_window_id": "active_2021_2024",
                "token_count": 6,
                "fragment_score": 0.0,
                "integrity_flags": "",
            },
            {
                "sentence_id": "s2",
                "sentence_text_id": "t2",
                "sentence": "AI supports underwriting decisions.",
                "sentence_norm": "ai supports underwriting decisions",
                "source_file": "2024/QTR2/f2.txt",
                "source_year": 2024,
                "source_quarter": 2,
                "source_form": "10-K",
                "source_cik": "1002",
                "sentence_index": 1,
                "manifest_id": "m2",
                "source_window_id": "active_2021_2024",
                "token_count": 6,
                "fragment_score": 0.0,
                "integrity_flags": "",
            },
            {
                "sentence_id": "s3",
                "sentence_text_id": "t3",
                "sentence": "AI improves planning processes.",
                "sentence_norm": "ai improves planning processes",
                "source_file": "2024/QTR3/f3.txt",
                "source_year": 2024,
                "source_quarter": 3,
                "source_form": "10-K",
                "source_cik": "1003",
                "sentence_index": 1,
                "manifest_id": "m3",
                "source_window_id": "active_2021_2024",
                "token_count": 6,
                "fragment_score": 0.0,
                "integrity_flags": "",
            },
        ]
    ).to_parquet(sentences_path, index=False)
    _write_csv(
        manifest_path,
        [
            {
                "path": "2024/QTR1/f1.txt",
                "manifest_id": "m1",
                "manifest_row_id": "mr1",
                "selection_reason": "seed",
                "sic": 3571,
                "ff12_code": 6,
                "ff12_name": "Business Equipment",
                "industry_metadata_source": "controls",
            },
            {
                "path": "2024/QTR2/f2.txt",
                "manifest_id": "m2",
                "manifest_row_id": "mr2",
                "selection_reason": "seed",
                "sic": 3571,
                "ff12_code": 6,
                "ff12_name": "Business Equipment",
                "industry_metadata_source": "controls",
            },
            {
                "path": "2024/QTR3/f3.txt",
                "manifest_id": "m3",
                "manifest_row_id": "mr3",
                "selection_reason": "seed",
                "sic": 3571,
                "ff12_code": 6,
                "ff12_name": "Business Equipment",
                "industry_metadata_source": "controls",
            },
        ],
    )
    tranche1 = _write_csv(tmp_path / "tranche1.csv", [{"sentence_text_id": "t1"}])
    tranche2 = _write_csv(tmp_path / "tranche2.csv", [{"sentence_text_id": "t2"}])
    output_parquet = tmp_path / "batch.parquet"
    output_csv = tmp_path / "batch.csv"
    report_path = tmp_path / "batch_summary.json"

    summary = build_labeling_batch(
        sentences_path=str(sentences_path),
        manifest_path=str(manifest_path),
        held_out_path=str(held_out_path),
        output_parquet_path=str(output_parquet),
        output_csv_path=str(output_csv),
        report_path=str(report_path),
        batch_id="batch",
        target_size=1,
        base_quarter_quota=1,
        exclude_existing_csvs=[str(tranche1), str(tranche2)],
    )

    output = pd.read_csv(output_csv)

    assert output["sentence_text_id"].tolist() == ["t3"]
    assert summary["candidate_stats"]["existing_batch_excluded"] == 2


def test_merge_labeling_batches_writes_master_outputs(tmp_path):
    tranche1 = _write_csv(
        tmp_path / "tranche1.csv",
        [
            {
                "batch_id": "labeling_batch_v1",
                "sentence_id": "s1",
                "sentence_text_id": "t1",
                "sentence": "We use artificial intelligence in operations.",
                "sentence_norm": "we use artificial intelligence in operations",
                "label": "Actionable",
                "is_uncertain": "",
                "uncertainty_note": "",
                "source_file": "2024/QTR1/f1.txt",
                "source_year": 2024,
                "source_quarter": 1,
                "source_form": "10-K",
                "source_cik": "1001",
                "sentence_index": 1,
                "assistive_label": "Actionable",
            }
        ],
    )
    tranche2 = _write_csv(
        tmp_path / "tranche2.csv",
        [
            {
                "batch_id": "labeling_batch_v2",
                "sentence_id": "s2",
                "sentence_text_id": "t2",
                "sentence": "We may use AI in the future.",
                "sentence_norm": "we may use ai in the future",
                "label": "Speculative",
                "is_uncertain": "",
                "uncertainty_note": "",
                "source_file": "2024/QTR2/f2.txt",
                "source_year": 2024,
                "source_quarter": 2,
                "source_form": "10-K",
                "source_cik": "1002",
                "sentence_index": 2,
                "assistive_label": "",
            }
        ],
    )
    held_out = _write_csv(
        tmp_path / "held_out.csv",
        [{"sentence": "Completely unrelated held out sentence."}],
    )
    output_parquet = tmp_path / "labels_master.parquet"
    output_review_csv = tmp_path / "labels_master_review.csv"
    report_path = tmp_path / "label_expansion_summary.json"

    summary, exit_code = merge_labeling_batches(
        input_csvs=[str(tranche1), str(tranche2)],
        held_out_path=str(held_out),
        output_parquet_path=str(output_parquet),
        output_review_csv_path=str(output_review_csv),
        report_path=str(report_path),
    )

    assert exit_code == 0
    assert output_parquet.exists()
    assert output_review_csv.exists()
    assert summary["summary"]["total_canonical_labeled_rows"] == 2
    assert summary["quality"]["heldout_overlap_count"] == 0
    assert summary["quality"]["exact_duplicate_count"] == 0
    assert summary["assistive_provenance"]["rows_with_assistive_columns"] == 1


def test_merge_labeling_batches_excludes_blank_and_heldout_rows(tmp_path):
    tranche = _write_csv(
        tmp_path / "tranche.csv",
        [
            {
                "batch_id": "labeling_batch_v1",
                "sentence_id": "s1",
                "sentence_text_id": "t1",
                "sentence": "We use artificial intelligence in operations.",
                "sentence_norm": "we use artificial intelligence in operations",
                "label": "Actionable",
                "is_uncertain": "",
                "uncertainty_note": "",
                "source_file": "2024/QTR1/f1.txt",
                "source_year": 2024,
                "source_quarter": 1,
                "source_form": "10-K",
                "source_cik": "1001",
                "sentence_index": 1,
                "assistive_label": "Actionable",
            },
            {
                "batch_id": "labeling_batch_v1",
                "sentence_id": "s2",
                "sentence_text_id": "t2",
                "sentence": "",
                "sentence_norm": "",
                "label": "",
                "is_uncertain": "",
                "uncertainty_note": "",
                "source_file": "2024/QTR1/f1.txt",
                "source_year": 2024,
                "source_quarter": 1,
                "source_form": "10-K",
                "source_cik": "1001",
                "sentence_index": 2,
                "assistive_label": "",
            },
            {
                "batch_id": "labeling_batch_v2",
                "sentence_id": "s3",
                "sentence_text_id": "t3",
                "sentence": "We may use AI in the future.",
                "sentence_norm": "we may use ai in the future",
                "label": "Speculative",
                "is_uncertain": "",
                "uncertainty_note": "",
                "source_file": "2024/QTR2/f2.txt",
                "source_year": 2024,
                "source_quarter": 2,
                "source_form": "10-K",
                "source_cik": "1002",
                "sentence_index": 3,
                "assistive_label": "Speculative",
            },
        ],
    )
    held_out = _write_csv(
        tmp_path / "held_out.csv",
        [{"sentence": "We may use AI in the future."}],
    )
    output_parquet = tmp_path / "labels_master.parquet"
    output_review_csv = tmp_path / "labels_master_review.csv"
    report_path = tmp_path / "label_expansion_summary.json"

    summary, exit_code = merge_labeling_batches(
        input_csvs=[str(tranche)],
        held_out_path=str(held_out),
        output_parquet_path=str(output_parquet),
        output_review_csv_path=str(output_review_csv),
        report_path=str(report_path),
    )

    assert exit_code == 0
    assert output_parquet.exists()
    assert output_review_csv.exists()
    assert summary["summary"]["total_input_rows"] == 3
    assert summary["summary"]["total_canonical_labeled_rows"] == 1
    assert summary["summary"]["blank_label_rows_excluded"] == 1
    assert summary["summary"]["heldout_overlap_rows_removed"] == 1
    assert summary["quality"]["heldout_overlap_count"] == 0
    assert summary["quality"]["heldout_overlap_removed_count"] == 1
    assert summary["quality"]["invalid_label_count"] == 0
    assert summary["assistive_provenance"]["rows_with_assistive_columns"] == 1


def test_benchmark_prompt_variants_picks_best_eligible_variant(monkeypatch, tmp_path):
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
    input_csv = _write_csv(tmp_path / "input.csv", input_rows)
    benchmark_csv = _write_csv(tmp_path / "benchmark.csv", benchmark_rows)
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
        *,
        input_csv: str,
        output_csv: str,
        report_path: str,
        policy_path: str,
        **_: object,
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
        "semantic_ai_washing.labeling.benchmark_prompt_variants.generate_assistive_prelabels",
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
    assert result["variants"][0]["score"]["overall"]["matches"] == 35
    assert result["variants"][1]["score"]["overall"]["matches"] == 38
    assert result["variants"][1]["score"]["action_spec"]["matches"] == 10


def test_benchmark_prompt_variants_reports_no_winner_when_gate_fails(monkeypatch, tmp_path):
    input_csv = _write_csv(
        tmp_path / "input.csv",
        [
            {
                "sentence_id": "s1",
                "sentence": "We offer AI-enabled products.",
                "label": "",
                "source_file": "f1.txt",
                "sentence_index": 1,
                "source_section": "item_1_business",
            },
            {
                "sentence_id": "s2",
                "sentence": "We may find opportunities by applying AI.",
                "label": "",
                "source_file": "f2.txt",
                "sentence_index": 2,
                "source_section": "item_1_business",
            },
        ],
    )
    benchmark_csv = _write_csv(
        tmp_path / "benchmark.csv",
        [
            {"sentence_id": "s1", "label": "Actionable"},
            {"sentence_id": "s2", "label": "Speculative"},
        ],
    )
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
""",
        encoding="utf-8",
    )

    def fake_generate_assistive_prelabels(
        *,
        input_csv: str,
        output_csv: str,
        report_path: str,
        **_: object,
    ):
        rows = pd.read_csv(input_csv)
        rows["assistive_label"] = ["Irrelevant", "Irrelevant"]
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
        "semantic_ai_washing.labeling.benchmark_prompt_variants.generate_assistive_prelabels",
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

    assert result["winner"] is None or result["winner"]["gate_passed"] is False


def test_score_prelabel_sheet_reports_raw_and_eligible_scores(tmp_path):
    benchmark_csv = _write_csv(
        tmp_path / "benchmark.csv",
        [
            {"sentence_id": "s1", "label": "Actionable"},
            {"sentence_id": "s2", "label": "Irrelevant"},
            {"sentence_id": "s3", "label": "Irrelevant"},
        ],
    )
    assistive_csv = _write_csv(
        tmp_path / "assistive.csv",
        [
            {
                "sentence_id": "s1",
                "assistive_label": "Actionable",
                "assistive_confidence": "high",
                "assistive_rationale": "fact",
                "source_section": "item_1_business",
                "sentence": "We offer AI-enabled services.",
                "prelabel_eligible": True,
                "skip_reason": "",
            },
            {
                "sentence_id": "s2",
                "assistive_label": "",
                "assistive_confidence": "",
                "assistive_rationale": "",
                "source_section": "other",
                "sentence": "",
                "prelabel_eligible": False,
                "skip_reason": "unmatched_noise",
            },
            {
                "sentence_id": "s3",
                "assistive_label": "Speculative",
                "assistive_confidence": "medium",
                "assistive_rationale": "future",
                "source_section": "item_1_business",
                "sentence": "We may find opportunities with AI.",
                "prelabel_eligible": True,
                "skip_reason": "",
            },
        ],
    )

    payload = score_prelabel_sheet(
        benchmark_csv=str(benchmark_csv),
        assistive_csv=str(assistive_csv),
    )

    assert payload["score"]["gate_basis"] == "eligible"
    assert payload["score"]["raw_overall"] == {"matches": 1, "total": 3}
    assert payload["score"]["eligible_overall"] == {"matches": 1, "total": 2}
    assert payload["score"]["overall"] == {"matches": 1, "total": 2}
    assert payload["score"]["excluded_from_gate"]["count"] == 1
    assert payload["score"]["excluded_from_gate"]["sentence_ids"] == ["s2"]


def test_benchmark_prompt_variants_regenerates_full_tranche_for_winner(monkeypatch, tmp_path):
    input_rows = []
    benchmark_rows = []
    for idx in range(40):
        sentence_id = f"s{idx + 1}"
        input_rows.append(
            {
                "sentence_id": sentence_id,
                "sentence": f"Sentence {idx + 1}",
                "label": "",
                "source_file": f"f{(idx % 4) + 1}.txt",
                "sentence_index": idx + 1,
                "source_section": "item_1_business",
            }
        )
        benchmark_rows.append(
            {
                "sentence_id": sentence_id,
                "label": (
                    "Actionable" if idx < 5 else "Speculative" if idx < 12 else "Irrelevant"
                ),
            }
        )
    input_csv = _write_csv(tmp_path / "input.csv", input_rows)
    benchmark_csv = _write_csv(tmp_path / "benchmark.csv", benchmark_rows)
    full_input_csv = _write_csv(
        tmp_path / "full_input.csv",
        [
            {
                "sentence_id": "full1",
                "sentence": "We offer AI-enabled services.",
                "label": "",
                "source_file": "full1.txt",
                "sentence_index": 1,
                "source_section": "item_1_business",
            },
            {
                "sentence_id": "full2",
                "sentence": "We may find opportunities with AI.",
                "label": "",
                "source_file": "full2.txt",
                "sentence_index": 2,
                "source_section": "item_1_business",
            },
        ],
    )
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
        *,
        input_csv: str,
        output_csv: str,
        report_path: str,
        policy_path: str,
        **_: object,
    ):
        policy_text = Path(policy_path).read_text(encoding="utf-8")
        rows = pd.read_csv(input_csv)
        if "variant b" in policy_text:
            if len(rows) == 40:
                labels = ["Actionable"] * 5 + ["Speculative"] * 5 + ["Irrelevant"] * 30
            else:
                labels = ["Actionable", "Speculative"]
        else:
            labels = ["Irrelevant"] * len(rows)
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
        "semantic_ai_washing.labeling.benchmark_prompt_variants.generate_assistive_prelabels",
        fake_generate_assistive_prelabels,
    )

    full_output = tmp_path / "full_prelabeled.csv"
    full_filled = tmp_path / "full_filled.csv"
    full_report = tmp_path / "full_report.json"
    result = benchmark_prompt_variants(
        input_csv=str(input_csv),
        benchmark_csv=str(benchmark_csv),
        base_policy_path=str(base_policy),
        variants_path=str(variants),
        report_json=str(tmp_path / "benchmark.json"),
        report_md=str(tmp_path / "benchmark.md"),
        full_input_csv=str(full_input_csv),
        full_output_csv=str(full_output),
        full_filled_csv=str(full_filled),
        full_report_json=str(full_report),
        regenerate_full_on_success=True,
    )

    assert result["winner"]["variant_id"] == "v2_4b"
    assert result["full_tranche"]["generated"] is True
    assert full_output.exists()
    assert full_filled.exists()
    generated = pd.read_csv(full_filled)
    assert generated["label"].fillna("").eq("").all()
