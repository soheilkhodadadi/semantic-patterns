from __future__ import annotations

import json

import pandas as pd

from semantic_ai_washing.classification.prepare_shadow_defer_review_sheet import run_prepare


def test_prepare_shadow_defer_review_sheet_conf_or_margin(tmp_path) -> None:
    input_root = tmp_path / "classifications"
    year_dir = input_root / "year=2024" / "model=layered_shadow"
    year_dir.mkdir(parents=True)
    pd.DataFrame(
        [
            {
                "sentence_id": "s1",
                "sentence": "We use AI in production.",
                "source_file": "a.txt",
                "sentence_index": 1,
                "source_section": "Business",
                "source_cik": "1",
                "source_year": 2024,
                "predicted_label": "Actionable",
                "local_label": "Actionable",
                "local_confidence": 0.82,
                "conditional_as_margin": 0.40,
                "binary_logreg_relevance_disagreement": False,
            },
            {
                "sentence_id": "s2",
                "sentence": "We plan to integrate AI.",
                "source_file": "a.txt",
                "sentence_index": 2,
                "source_section": "Business",
                "source_cik": "1",
                "source_year": 2024,
                "predicted_label": "Speculative",
                "local_label": "Speculative",
                "local_confidence": 0.70,
                "conditional_as_margin": 0.04,
                "binary_logreg_relevance_disagreement": False,
            },
        ]
    ).to_parquet(year_dir / "classified_sentences.parquet", index=False)

    output_csv = tmp_path / "deferred.csv"
    output_report = tmp_path / "report.json"
    args = type(
        "Args",
        (),
        {
            "input_root": str(input_root),
            "years": ["2024"],
            "model_id": "layered_shadow",
            "policy": "conf_or_margin",
            "output_csv": str(output_csv),
            "output_report": str(output_report),
        },
    )()

    report = run_prepare(args)
    deferred = pd.read_csv(output_csv)

    assert report["summary"]["rows_total"] == 2
    assert report["summary"]["deferred_rows"] == 1
    assert deferred["sentence_id"].tolist() == ["s2"]
    assert deferred["shadow_policy"].tolist() == ["conf_or_margin"]
    assert json.loads(output_report.read_text(encoding="utf-8"))["summary"]["deferred_rows"] == 1
