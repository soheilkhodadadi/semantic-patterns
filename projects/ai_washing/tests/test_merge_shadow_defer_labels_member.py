from __future__ import annotations

import json

import pandas as pd

from semantic_ai_washing.classification.merge_shadow_defer_labels import run_merge


def test_merge_shadow_defer_labels_overrides_deferred_rows(tmp_path) -> None:
    input_root = tmp_path / "classifications_local"
    input_dir = input_root / "year=2024" / "model=layered_shadow"
    input_dir.mkdir(parents=True)
    pd.DataFrame(
        [
            {
                "sentence_id": "s1",
                "sentence": "We use AI in production.",
                "predicted_label": "Actionable",
                "prediction_source": "local",
                "deferred_to_api": False,
                "source_year": 2024,
            },
            {
                "sentence_id": "s2",
                "sentence": "We plan to integrate AI.",
                "predicted_label": "Speculative",
                "prediction_source": "local",
                "deferred_to_api": False,
                "source_year": 2024,
            },
        ]
    ).to_parquet(input_dir / "classified_sentences.parquet", index=False)

    deferred_csv = tmp_path / "deferred.csv"
    pd.DataFrame(
        [
            {
                "sentence_id": "s2",
                "assistive_label": "Irrelevant",
                "assistive_confidence": "medium",
                "assistive_rationale": "Market trend, not firm capability.",
                "assistive_model": "gpt-5-mini",
            }
        ]
    ).to_csv(deferred_csv, index=False)

    output_root = tmp_path / "classifications_hybrid"
    output_report = tmp_path / "merge.json"
    args = type(
        "Args",
        (),
        {
            "input_root": str(input_root),
            "input_model_id": "layered_shadow",
            "years": ["2024"],
            "deferred_csv": str(deferred_csv),
            "output_root": str(output_root),
            "output_model_id": "hybrid_shadow",
            "output_report": str(output_report),
        },
    )()

    report = run_merge(args)
    merged = pd.read_parquet(
        output_root / "year=2024" / "model=hybrid_shadow" / "classified_sentences.parquet"
    )

    assert report["summary"]["api_rows_total"] == 1
    assert merged.loc[merged["sentence_id"] == "s2", "predicted_label"].item() == "Irrelevant"
    assert merged.loc[merged["sentence_id"] == "s2", "prediction_source"].item() == "api_a"
    assert bool(merged.loc[merged["sentence_id"] == "s2", "deferred_to_api"].item()) is True
    assert json.loads(output_report.read_text(encoding="utf-8"))["summary"]["api_rows_total"] == 1
