from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ai_washing_member.data.build_refresh_extraction_manifests import build_manifests
from ai_washing_member.data.extract_refresh_year_batches import run_extraction
from ai_washing_member.data.index_refresh_window import run_refresh_index


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _make_filing(root: Path, quarter: str, name: str, text: str) -> None:
    _write_text(root / "2025" / quarter / name, text)


def test_refresh_2025_index_manifest_and_extraction_smoke(tmp_path: Path) -> None:
    sec_root = tmp_path / "sec_root"
    keywords = tmp_path / "keywords.txt"
    _write_text(keywords, "ai\nartificial intelligence\nmachine learning\n")

    _make_filing(
        sec_root,
        "QTR1",
        "20250103_10-K_edgar_data_1001_0001001-25-000001.txt",
        "We deploy artificial intelligence systems in production.",
    )
    _make_filing(
        sec_root,
        "QTR2",
        "20250503_10-K_edgar_data_1002_0001002-25-000001.txt",
        "Our machine learning platform supports operations today.",
    )
    _make_filing(
        sec_root,
        "QTR3",
        "20250803_10-K-A_edgar_data_1003_0001003-25-000001.txt",
        "Artificial intelligence is discussed in an amendment.",
    )
    _make_filing(
        sec_root,
        "QTR4",
        "20251103_10-Q_edgar_data_1004_0001004-25-000001.txt",
        "This quarterly filing should not be indexed in the annual lane.",
    )

    index_report = run_refresh_index(
        argparse.Namespace(
            source_root=str(sec_root),
            source_root_hint="",
            source_window_id="annual_10k_2025_refresh_v1",
            years=[2025],
            forms=["10-K", "10-K-A"],
            output_csv=str(tmp_path / "available_filings_index_2025_refresh_v1.csv"),
            output_source_windows=str(tmp_path / "source_windows_2025_refresh_v1.json"),
            output_summary=str(tmp_path / "source_index_summary_2025_refresh_v1.json"),
        )
    )
    assert index_report["indexed_row_count"] == 3

    manifest_report = build_manifests(
        argparse.Namespace(
            index_csv=str(tmp_path / "available_filings_index_2025_refresh_v1.csv"),
            source_window_id="annual_10k_2025_refresh_v1",
            year=2025,
            forms=["10-K"],
            output_dir=str(tmp_path / "manifests"),
            report_path=str(tmp_path / "manifest_summary.json"),
        )
    )
    assert manifest_report["summary"]["manifest_count"] == 2
    assert manifest_report["summary"]["total_rows"] == 2

    extraction_report = run_extraction(
        argparse.Namespace(
            manifest_dir=str(tmp_path / "manifests"),
            source_root=str(sec_root),
            year=2025,
            output_root=str(tmp_path / "processed" / "sentences_refresh_2025_v1"),
            output_report=str(tmp_path / "reports" / "extraction.json"),
            progress_report=str(tmp_path / "reports" / "extraction_progress.json"),
            keywords_path=str(keywords),
            min_tokens=6,
            max_tokens=120,
            segmentation_mode="default",
            sample_size=20,
        )
    )
    combined_path = (
        tmp_path / "processed" / "sentences_refresh_2025_v1" / "year=2025" / "ai_sentences.parquet"
    )
    assert combined_path.exists()
    frame = pd.read_parquet(combined_path)
    assert frame["source_form"].isin(["10-K"]).all()
    assert extraction_report["summary"]["combined_row_count"] == len(frame)
