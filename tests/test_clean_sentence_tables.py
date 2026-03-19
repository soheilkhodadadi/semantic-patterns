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


def test_clean_sentence_tables_repairs_heading_and_drops_artifact_ai_and_ocr(tmp_path: Path) -> None:
    input_root = tmp_path / "sentences"
    year_dir = input_root / "year=2024"
    year_dir.mkdir(parents=True)
    frame = pd.DataFrame(
        [
            {
                "sentence_id": "keep-heading",
                "sentence_text_id": "keep-heading-text",
                "sentence_norm": "old",
                "sentence": (
                    "Developers and Enterprises We serve developers and enterprises of all sizes "
                    "through AWS machine learning services."
                ),
                "fragment_score": 0.0,
                "token_count": 15,
            },
            {
                "sentence_id": "keep-number-prefix",
                "sentence_text_id": "keep-number-prefix-text",
                "sentence_norm": "old",
                "sentence": (
                    "29 In addition to our use of AI technologies, we are exposed to risks arising "
                    "from bad actors."
                ),
                "fragment_score": 0.0,
                "token_count": 17,
            },
            {
                "sentence_id": "drop-clause-ai",
                "sentence_text_id": "drop-clause-ai-text",
                "sentence_norm": "old",
                "sentence": "(ai) Purchase Price has the meaning ascribed to that term in Clause 2.3(a).",
                "fragment_score": 0.0,
                "token_count": 13,
            },
            {
                "sentence_id": "drop-ocr",
                "sentence_text_id": "drop-ocr-text",
                "sentence_norm": "old",
                "sentence": (
                    "T h e f i n a n c ial's t a t e m e nts do not i n c l u d e a n y ad j u s t m ents."
                ),
                "fragment_score": 0.0,
                "token_count": 20,
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
    assert cleaned["sentence_id"].tolist() == ["keep-heading", "keep-number-prefix"]
    kept = cleaned.set_index("sentence_id")
    assert kept.loc["keep-heading", "sentence"].startswith("We serve developers")
    assert kept.loc["keep-number-prefix", "sentence"].startswith("In addition to our use")
    assert kept.loc["keep-heading", "sentence_norm"].startswith("we serve developers")
    assert report["years"]["2024"]["dropped_artifact_ai_false_positive"] == 1
    assert report["years"]["2024"]["dropped_ocr_like"] == 1
