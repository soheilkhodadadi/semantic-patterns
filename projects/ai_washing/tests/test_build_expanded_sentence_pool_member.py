from __future__ import annotations

from pathlib import Path

import pandas as pd

from ai_washing_member.data.build_expanded_sentence_pool import build_expanded_sentence_pool


def _write_csv(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def _make_index_and_source_root(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    source_root = tmp_path / "sec-root"
    controls = tmp_path / "controls.csv"
    crosswalk = tmp_path / "crosswalk.csv"
    keywords = tmp_path / "keywords.txt"

    filing_rows = []
    texts = {
        "2024/QTR1/f1.txt": "We use artificial intelligence in day to day operations today. Machine learning improves support forecasting across customer service teams.",
        "2024/QTR2/f2.txt": "Our artificial intelligence systems are deployed in compliance review workflows today. Machine learning helps current monitoring across the control function.",
        "2024/QTR3/f3.txt": "Artificial intelligence supports underwriting decisions in current production workflows. Machine learning improves current risk management across operating units.",
        "2024/QTR4/f4.txt": "We currently deploy artificial intelligence for analytics in core internal workflows. Machine learning improves ongoing planning and resource allocation decisions.",
    }
    cik_map = {
        "2024/QTR1/f1.txt": "1001",
        "2024/QTR2/f2.txt": "1002",
        "2024/QTR3/f3.txt": "1003",
        "2024/QTR4/f4.txt": "1004",
    }

    for relative_path, text in texts.items():
        file_path = source_root / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(text, encoding="utf-8")
        quarter = int(relative_path.split("/")[1].replace("QTR", ""))
        filing_rows.append(
            {
                "cik": cik_map[relative_path],
                "year": 2024,
                "quarter": quarter,
                "form": "10-K",
                "filename": Path(relative_path).name,
                "path": relative_path,
                "source_root": str(source_root),
                "index_timestamp": "2026-03-07T00:00:00Z",
                "source_window_id": "active_2021_2024",
            }
        )

    index_path = tmp_path / "available_filings_index.csv"
    pd.DataFrame(filing_rows).to_csv(index_path, index=False)
    _write_csv(
        controls,
        [
            {"cik": "1001", "year": 2024, "sic": 3571},
            {"cik": "1002", "year": 2024, "sic": 3571},
            {"cik": "1003", "year": 2024, "sic": 3571},
            {"cik": "1004", "year": 2024, "sic": 3571},
        ],
    )
    _write_csv(crosswalk, [{"cik": "1001", "sic": 3571}])
    keywords.write_text("artificial intelligence\nmachine learning\n", encoding="utf-8")
    return index_path, source_root, controls, keywords


def test_member_build_expanded_sentence_pool_smoke(tmp_path: Path) -> None:
    index_path, source_root, controls, keywords = _make_index_and_source_root(tmp_path)
    crosswalk = tmp_path / "crosswalk.csv"

    payload = build_expanded_sentence_pool(
        index_path=str(index_path),
        output_manifest_path=str(tmp_path / "manifest.csv"),
        output_sentences_path=str(tmp_path / "sentences.parquet"),
        report_path=str(tmp_path / "report.json"),
        controls_path=str(controls),
        crosswalk_path=str(crosswalk),
        keywords_path=str(keywords),
        source_root=str(source_root),
        target_firms=4,
        min_clean_sentences=4,
        manifest_id="member_sentence_pool",
        seed=123,
    )

    assert payload["manifest"]["selected_filing_count"] == 4
    assert payload["candidate_pool"]["firm_count"] == 4
    assert payload["selection"]["firm_target_satisfied"] is True
    assert payload["selection"]["clean_sentence_target_satisfied"] is True
