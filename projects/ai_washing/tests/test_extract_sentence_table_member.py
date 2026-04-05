from __future__ import annotations

from pathlib import Path

import pandas as pd

from ai_washing_member.data.extract_sentence_table import _segment_text, extract_sentence_table


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_member_segment_text_dispatches_default_and_fast(monkeypatch) -> None:
    monkeypatch.setattr(
        "ai_washing_member.data.extract_sentence_table.segment_sentences_fast",
        lambda text: ["fast"],
    )
    monkeypatch.setattr(
        "ai_washing_member.data.extract_sentence_table.segment_sentences",
        lambda text: ["default"],
    )
    assert _segment_text("hello", "fast") == ["fast"]
    assert _segment_text("hello", "default") == ["default"]


def test_member_extract_sentence_table_smoke(tmp_path) -> None:
    source_root = tmp_path / "sec_root"
    filing_path = source_root / "2024" / "QTR1" / "20240101_10-K_edgar_data_1001_0001.txt"
    _write_text(
        filing_path,
        "Artificial intelligence supports automation. Machine learning improves forecasting.",
    )

    manifest_path = tmp_path / "manifest.csv"
    pd.DataFrame(
        [
            {
                "manifest_id": "pilot_2024_10k_v1",
                "manifest_row_id": "abc123",
                "sampling_seed": 1,
                "selection_reason": "quarter_fill",
                "source_window_id": "active_2021_2024",
                "cik": "1001",
                "year": 2024,
                "quarter": 1,
                "form": "10-K",
                "filename": filing_path.name,
                "path": "2024/QTR1/20240101_10-K_edgar_data_1001_0001.txt",
                "sic": "3571",
                "ff12_code": 6,
                "ff12_name": "BusEq",
                "industry_metadata_source": "controls_by_firm_year",
            }
        ]
    ).to_csv(manifest_path, index=False)

    keywords_path = tmp_path / "keywords.txt"
    _write_text(keywords_path, "artificial intelligence\nmachine learning\n")

    output_path = tmp_path / "sentences.parquet"
    sample_output_path = tmp_path / "sentences_sample.csv"
    report_path = tmp_path / "report.json"

    report = extract_sentence_table(
        manifest_path=str(manifest_path),
        output_path=str(output_path),
        sample_output_path=str(sample_output_path),
        report_path=str(report_path),
        source_root=str(source_root),
        keywords_path=str(keywords_path),
        min_tokens=3,
        sample_size=1,
    )

    written = pd.read_parquet(output_path)
    assert not written.empty
    assert report["manifest_metadata"]["filings_succeeded"] == 1
