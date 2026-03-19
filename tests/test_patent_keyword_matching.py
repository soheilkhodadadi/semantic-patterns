from __future__ import annotations

import pandas as pd

from semantic_ai_washing.patents.benchmark_keyword_sets import benchmark_keyword_set
from semantic_ai_washing.patents.keyword_matching import compile_boundary_pattern, matched_keywords


def test_compile_boundary_pattern_matches_hyphenated_phrases() -> None:
    pattern = compile_boundary_pattern(["machine learning", "deep learning"])
    text = "A machine-learning pipeline with deep-learning components."
    assert matched_keywords(text, pattern) == "deep learning | machine learning"


def test_benchmark_keyword_set_reports_matched_keywords(tmp_path) -> None:
    keywords_path = tmp_path / "keywords.txt"
    keywords_path.write_text("machine learning\nanomaly detection\n", encoding="utf-8")
    frame = pd.DataFrame(
        [
            {
                "cik": "1",
                "name": "Firm A",
                "year": 2024,
                "patent_id": "p1",
                "patent_title": "Fraud detection engine",
                "patent_abstract": "A machine-learning model performs anomaly detection.",
                "text": "Fraud detection engine A machine-learning model performs anomaly detection.",
            }
        ]
    )

    result, examples = benchmark_keyword_set(frame, "test", str(keywords_path), examples_per_set=5)

    assert result["total_patents_ai"] == 1
    assert len(examples) == 1
    assert examples.iloc[0]["matched_keywords"] == "anomaly detection | machine learning"
