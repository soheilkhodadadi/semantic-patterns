from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from semantic_ai_washing.data.clean_sentence_tables import clean_sentence_tables


def test_clean_sentence_tables_drops_long_fragment_and_table_like_rows(tmp_path: Path) -> None:
    input_root = tmp_path / "sentences"
    year_dir = input_root / "year=2024"
    year_dir.mkdir(parents=True)
    frame = pd.DataFrame(
        [
            {
                "sentence_id": "keep-1",
                "sentence": "We deployed artificial intelligence tools across our underwriting workflow.",
                "fragment_score": 0.0,
                "token_count": 9,
            },
            {
                "sentence_id": "drop-long",
                "sentence": "word " * 200,
                "fragment_score": 0.0,
                "token_count": 200,
            },
            {
                "sentence_id": "drop-fragment",
                "sentence": "fragment without punctuation",
                "fragment_score": 0.25,
                "token_count": 3,
            },
            {
                "sentence_id": "drop-table",
                "sentence": "Exhibit A Asserting Party Servicing Platform Applicable Certification Period",
                "fragment_score": 0.0,
                "token_count": 9,
            },
        ]
    )
    frame.to_parquet(year_dir / "ai_sentences.parquet", index=False)

    args = argparse.Namespace(
        input_root=str(input_root),
        output_root=str(tmp_path / "sentences_clean"),
        output_report=str(tmp_path / "cleanup_report.json"),
        years=["2024"],
        min_tokens=6,
        max_tokens=120,
        max_fragment_score=0.0,
    )

    report = clean_sentence_tables(args)

    cleaned = pd.read_parquet(Path(args.output_root) / "year=2024" / "ai_sentences.parquet")
    assert cleaned["sentence_id"].tolist() == ["keep-1"]
    assert report["years"]["2024"]["rows_dropped"] == 3
    saved = json.loads(Path(args.output_report).read_text(encoding="utf-8"))
    assert saved["summary"]["rows_dropped"] == 3
