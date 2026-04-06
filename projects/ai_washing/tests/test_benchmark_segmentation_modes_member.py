from __future__ import annotations

import argparse

import pandas as pd

from ai_washing_member.data.benchmark_segmentation_modes import benchmark_modes


def test_member_benchmark_segmentation_modes_smoke(tmp_path, monkeypatch) -> None:
    index_csv = tmp_path / "index.csv"
    pd.DataFrame(
        [
            {
                "cik": "1001",
                "year": 2024,
                "quarter": 1,
                "form": "10-K",
                "filename": "f1.txt",
                "path": "2024/QTR1/f1.txt",
                "source_window_id": "active_2021_2024",
            },
            {
                "cik": "1002",
                "year": 2024,
                "quarter": 2,
                "form": "10-K",
                "filename": "f2.txt",
                "path": "2024/QTR2/f2.txt",
                "source_window_id": "active_2021_2024",
            },
        ]
    ).to_csv(index_csv, index=False)

    def _fake_extract_sentence_table(**kwargs):
        output_path = kwargs["output_path"]
        sample_output_path = kwargs["sample_output_path"]
        pd.DataFrame(
            [
                {
                    "sentence_id": "s1",
                    "sentence_text_id": "t1",
                    "sentence": "Artificial intelligence supports current workflows.",
                    "token_count": 6,
                    "fragment_score": 0.0,
                }
            ]
        ).to_parquet(output_path, index=False)
        pd.DataFrame([{"sentence_id": "s1"}]).to_csv(sample_output_path, index=False)
        return {"status": "passed", "segmentation_mode": kwargs["segmentation_mode"]}

    monkeypatch.setattr(
        "ai_washing_member.data.benchmark_segmentation_modes.extract_sentence_table",
        _fake_extract_sentence_table,
    )

    summary = benchmark_modes(
        argparse.Namespace(
            index_csv=str(index_csv),
            source_root=str(tmp_path / "sec-root"),
            year=2024,
            form="10-K",
            sample_filings=2,
            keywords_path=str(tmp_path / "keywords.txt"),
            min_tokens=6,
            max_tokens=120,
            max_fragment_score=0.0,
            sample_size=10,
            output_report=str(tmp_path / "benchmark.json"),
        )
    )

    assert summary["status"] == "passed"
    assert set(summary["results"]) == {"default", "fast"}
