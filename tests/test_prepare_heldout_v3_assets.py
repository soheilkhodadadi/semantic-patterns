from __future__ import annotations

import json

import pandas as pd

from semantic_ai_washing.labeling.prepare_heldout_v3_assets import prepare_heldout_v3_assets


def test_prepare_heldout_v3_assets_excludes_and_resets_columns(tmp_path):
    source = pd.DataFrame(
        [
            {
                "sentence_id": "keep-1",
                "sentence": "We use AI in production.",
                "source_cik": 1,
                "source_year": 2024,
                "source_form": "10-K",
                "source_file": "a.txt",
                "sentence_index": 3,
                "candidate_label": "Actionable",
                "label": "",
                "review_note": "",
                "benchmark_asset_role": "canonical_current_rubric_evaluation_set_candidate",
                "assistive_label": "Actionable",
                "assistive_confidence": "high",
                "assistive_rationale": "current use",
                "assistive_model": "gpt-5-mini",
                "assistive_generated_at": "2026-03-17T00:00:00+00:00",
                "assistive_prompt_hash": "hash-1",
            },
            {
                "sentence_id": "drop-1",
                "sentence": "garbage row",
                "source_cik": 2,
                "source_year": 2024,
                "source_form": "10-K",
                "source_file": "b.txt",
                "sentence_index": 9,
                "candidate_label": "Irrelevant",
                "label": "",
                "review_note": "",
                "benchmark_asset_role": "canonical_current_rubric_evaluation_set_candidate",
                "assistive_label": "Irrelevant",
                "assistive_confidence": "low",
                "assistive_rationale": "garbage",
                "assistive_model": "gpt-5-mini",
                "assistive_generated_at": "2026-03-17T00:00:00+00:00",
                "assistive_prompt_hash": "hash-2",
            },
        ]
    )
    input_csv = tmp_path / "recovered.csv"
    candidate_csv = tmp_path / "candidate.csv"
    review_csv = tmp_path / "review.csv"
    slice_csv = tmp_path / "slice.csv"
    report_json = tmp_path / "report.json"
    source.to_csv(input_csv, index=False)

    report = prepare_heldout_v3_assets(
        input_csv=str(input_csv),
        candidate_output_csv=str(candidate_csv),
        review_output_csv=str(review_csv),
        slice_output_csv=str(slice_csv),
        output_report=str(report_json),
        slice_size=1,
        exclude_sentence_ids=["drop-1"],
    )

    assert report["summary"]["rows_after_exclusions"] == 1
    assert report["summary"]["rows_excluded"] == 1

    candidate = pd.read_csv(candidate_csv)
    assert list(candidate["sentence_id"]) == ["keep-1"]
    assert candidate.loc[0, "legacy_candidate_label"] == "Actionable"
    assert candidate.loc[0, "legacy_assistive_label"] == "Actionable"
    assert candidate.loc[0, "benchmark_name"] == "held_out_v3"
    assert candidate.loc[0, "benchmark_asset_role"] == "canonical_current_rubric_evaluation_set_candidate_v3"
    assert candidate.loc[0, "review_status"] == "pending"
    assert bool(candidate.loc[0, "prelabel_eligible"]) is True
    assert pd.isna(candidate.loc[0, "assistive_label"])
    assert pd.isna(candidate.loc[0, "label"])
    assert pd.isna(candidate.loc[0, "review_note"])

    slice_frame = pd.read_csv(slice_csv)
    assert len(slice_frame) == 1

    payload = json.loads(report_json.read_text(encoding="utf-8"))
    assert payload["summary"]["legacy_assistive_present_rows"] == 1
