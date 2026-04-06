from __future__ import annotations

from pathlib import Path

import pandas as pd

from ai_washing_member.data.combine_expanded_sentence_pool_batches import (
    combine_expanded_sentence_pool_batches,
)


def _write_csv(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def test_member_combine_expanded_sentence_pool_batches_smoke(tmp_path: Path) -> None:
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

    report = combine_expanded_sentence_pool_batches(
        manifest_paths=[str(batch1_manifest), str(batch2_manifest)],
        sentence_paths=[str(batch1_sentences), str(batch2_sentences)],
        output_manifest_path=str(tmp_path / "combined_manifest.csv"),
        output_sentences_path=str(tmp_path / "combined_sentences.parquet"),
        report_path=str(tmp_path / "combined_report.json"),
    )

    assert report["candidate_pool"]["firm_count"] == 2
    assert report["candidate_pool"]["clean_sentence_count"] == 2
    assert report["quality"]["duplicate_firm_count"] == 0
