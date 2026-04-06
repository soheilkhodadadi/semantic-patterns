from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from ai_washing_member.data.materialize_active_window_sentences import run_materialization
from semantic_ai_washing.core import sentence_filter

pytest.importorskip(
    "pyarrow", reason="pyarrow is required for parquet-backed materialization tests"
)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _make_filing(root: Path, year: int, cik: str, stem: str, text: str) -> None:
    filing = root / f"{year}" / "QTR1" / f"{year}0101_10-K_edgar_data_{cik}_{stem}.txt"
    _write_text(filing, text)


def test_member_materialize_active_window_sentences_builds_and_reuses_outputs(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(sentence_filter, "_get_spacy", lambda: None)
    source_root = tmp_path / "sec"
    keywords = tmp_path / "keywords.txt"
    index_csv = tmp_path / "available_filings_index.csv"
    index_csv.write_text("", encoding="utf-8")
    _write_text(keywords, "ai\nartificial intelligence\nmachine learning\n")

    for year, cik in [(2021, "1001"), (2022, "1002"), (2023, "1003"), (2024, "1004")]:
        _make_filing(
            source_root,
            year,
            cik,
            f"000{year}",
            "We deploy artificial intelligence systems in production. This improved workflows.",
        )

    args = argparse.Namespace(
        index_csv=str(index_csv),
        source_root=str(source_root),
        source_root_hint=str(tmp_path / "sec_source_dir.txt"),
        source_windows_json=str(tmp_path / "source_windows.json"),
        index_summary_json=str(tmp_path / "source_index_summary.json"),
        source_window_id="active_2021_2024",
        years=["2021", "2022", "2023", "2024"],
        output_root=str(tmp_path / "processed" / "sentences"),
        output_report=str(tmp_path / "reports" / "active_window_sentence_inventory_v1.json"),
        keywords_path=str(keywords),
        min_tokens=6,
        sample_size=10,
        refresh_index_if_missing_or_empty=True,
    )
    report = run_materialization(args)
    assert report["summary"]["status"] == "passed"
    assert report["summary"]["completed_year_count"] == 4
    assert report["summary"]["index_refresh_performed"] is True

    rerun = run_materialization(args)
    assert rerun["summary"]["years_reused"] == [2021, 2022, 2023, 2024]
