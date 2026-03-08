from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from semantic_ai_washing.data.build_expanded_sentence_pool import build_expanded_sentence_pool
from semantic_ai_washing.director.core.cost import CostController
from semantic_ai_washing.labeling.assistive_prelabel_batch import generate_assistive_prelabels
from semantic_ai_washing.labeling.merge_labeling_batches import merge_labeling_batches


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
