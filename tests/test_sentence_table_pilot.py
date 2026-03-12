from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from semantic_ai_washing.core.sentence_filter import (
    clean_extracted_sentence,
    filter_ai_sentences_with_sections,
    get_sentence_integrity_flags,
    normalize_sentence_text,
)
from semantic_ai_washing.data.build_filing_manifest import build_manifest
from semantic_ai_washing.data.extract_sentence_table import extract_sentence_table
from semantic_ai_washing.data.reextract_tranche_slice import reextract_tranche_slice


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _build_index_frame(per_quarter: int = 2) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    cik_seed = 1000
    for quarter in (1, 2, 3, 4):
        for offset in range(per_quarter):
            cik = str(cik_seed + quarter * 10 + offset)
            rows.append(
                {
                    "cik": cik,
                    "year": 2024,
                    "quarter": quarter,
                    "form": "10-K",
                    "filename": f"20240{quarter:01d}01_10-K_edgar_data_{cik}_000{offset}.txt",
                    "path": f"2024/QTR{quarter}/20240{quarter:01d}01_10-K_edgar_data_{cik}_000{offset}.txt",
                    "source_root": "env:SEC_SOURCE_DIR",
                    "index_timestamp": "2026-03-06T00:00:00+00:00",
                    "source_window_id": "active_2021_2024",
                }
            )
    return pd.DataFrame(rows)


def test_build_manifest_enforces_quarter_quota_and_contract(tmp_path):
    index_path = tmp_path / "index.csv"
    controls_path = tmp_path / "controls.csv"
    crosswalk_path = tmp_path / "crosswalk.csv"

    index = _build_index_frame(per_quarter=3)
    index.to_csv(index_path, index=False)
    pd.DataFrame(
        [
            {"cik": "1010", "year": 2024, "sic": 3571},
            {"cik": "1011", "year": 2024, "sic": 2834},
            {"cik": "1020", "year": 2024, "sic": 4800},
            {"cik": "1021", "year": 2024, "sic": 6021},
        ]
    ).to_csv(controls_path, index=False)
    pd.DataFrame(
        [
            {"cik": "1030", "gvkey": 1, "sic": 3714},
            {"cik": "1040", "gvkey": 2, "sic": 7372},
        ]
    ).to_csv(crosswalk_path, index=False)

    manifest, summary = build_manifest(
        index_path=str(index_path),
        year=2024,
        form="10-K",
        target_size=8,
        quarter_quota=2,
        controls_path=str(controls_path),
        crosswalk_path=str(crosswalk_path),
        manifest_id="pilot",
        seed=7,
    )

    assert len(manifest) == 8
    assert manifest["year"].tolist() == [2024] * 8
    assert set(manifest["form"]) == {"10-K"}
    assert manifest["quarter"].value_counts().to_dict() == {1: 2, 2: 2, 3: 2, 4: 2}
    assert set(manifest["selection_reason"]).issubset({"quarter_ff12_round_robin", "quarter_fill"})
    assert manifest["manifest_row_id"].is_unique
    assert summary["quota_satisfied"] is True
    assert summary["selected_quarter_counts"] == {"1": 2, "2": 2, "3": 2, "4": 2}


def test_build_manifest_fails_when_a_quarter_cannot_meet_quota(tmp_path):
    index_path = tmp_path / "index.csv"
    controls_path = tmp_path / "controls.csv"
    crosswalk_path = tmp_path / "crosswalk.csv"

    index = _build_index_frame(per_quarter=2)
    index = index[~((index["quarter"] == 4) & (index["cik"] == "1041"))].copy()
    index.to_csv(index_path, index=False)
    pd.DataFrame(columns=["cik", "year", "sic"]).to_csv(controls_path, index=False)
    pd.DataFrame(columns=["cik", "gvkey", "sic"]).to_csv(crosswalk_path, index=False)

    with pytest.raises(ValueError, match="required quota"):
        build_manifest(
            index_path=str(index_path),
            year=2024,
            form="10-K",
            target_size=8,
            quarter_quota=2,
            controls_path=str(controls_path),
            crosswalk_path=str(crosswalk_path),
        )


def test_sentence_filter_helpers_are_deterministic():
    assert normalize_sentence_text(" AI,\nSentence!!  ") == "ai sentence"
    flags = get_sentence_integrity_flags("artificial intelligence", min_tokens=3)
    assert "missing_terminal_punct" in flags
    assert "lowercase_start" in flags
    assert "short_sentence" in flags


def test_clean_extracted_sentence_removes_obvious_noise():
    assert clean_extracted_sentence("Table of Contents | Artificial intelligence strategy.") == (
        "Artificial intelligence strategy."
    )
    assert clean_extracted_sentence(
        "FORM 10-K 12 Artificial intelligence supports workflows."
    ) == ("Artificial intelligence supports workflows.")
    assert clean_extracted_sentence(
        "Business Overview Artificial intelligence supports workflows."
    ) == ("Artificial intelligence supports workflows.")
    assert clean_extracted_sentence("- Artificial intelligence") == ""
    assert clean_extracted_sentence("N Artificial intelligence supports workflows.") == (
        "Artificial intelligence supports workflows."
    )
    assert clean_extracted_sentence("Artificial intelligence ) supports workflows.") == (
        "Artificial intelligence supports workflows."
    )


def test_filter_ai_sentences_with_sections_tags_common_10k_sections():
    sentences = [
        "Item 1. Business",
        "Artificial intelligence supports current operating workflows.",
        "Item 1A. Risk Factors",
        "Artificial intelligence could expose us to cyber risks.",
        "Item 7. Management's Discussion and Analysis",
        "We expect artificial intelligence to improve future productivity.",
    ]
    tagged = filter_ai_sentences_with_sections(
        sentences, ["artificial intelligence", "machine learning"]
    )

    assert tagged == [
        (
            "Artificial intelligence supports current operating workflows.",
            "item_1_business",
        ),
        ("Artificial intelligence could expose us to cyber risks.", "item_1a_risk_factors"),
        (
            "We expect artificial intelligence to improve future productivity.",
            "item_7_mda",
        ),
    ]


def test_extract_sentence_table_writes_contract_outputs_and_report(tmp_path):
    source_root = tmp_path / "sec_root"
    filing_path = source_root / "2024" / "QTR1" / "20240101_10-K_edgar_data_1001_0001.txt"
    _write_text(
        filing_path,
        (
            "Artificial intelligence supports automation. "
            "Machine learning improves forecasting. "
            "artificial intelligence transforms workflows"
        ),
    )

    manifest_path = tmp_path / "manifest.csv"
    manifest = pd.DataFrame(
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
            },
            {
                "manifest_id": "pilot_2024_10k_v1",
                "manifest_row_id": "missing1",
                "sampling_seed": 1,
                "selection_reason": "quarter_fill",
                "source_window_id": "active_2021_2024",
                "cik": "1002",
                "year": 2024,
                "quarter": 1,
                "form": "10-K",
                "filename": "missing.txt",
                "path": "2024/QTR1/missing.txt",
                "sic": "",
                "ff12_code": 12,
                "ff12_name": "Other",
                "industry_metadata_source": "unknown",
            },
        ]
    )
    manifest.to_csv(manifest_path, index=False)

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
    assert written.columns.tolist() == [
        "sentence_id",
        "sentence_text_id",
        "sentence",
        "sentence_norm",
        "source_file",
        "source_year",
        "source_quarter",
        "source_form",
        "source_section",
        "source_cik",
        "sentence_index",
        "extractor_version",
        "keyword_version",
        "manifest_id",
        "source_window_id",
        "integrity_flags",
        "fragment_score",
        "token_count",
    ]
    assert len(written) >= 2
    assert set(written["source_section"]).issubset(
        {"item_1_business", "item_1a_risk_factors", "item_7_mda", "other"}
    )
    assert sample_output_path.exists()
    sample = pd.read_csv(sample_output_path)
    assert len(sample) == 1

    report_payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert report_payload["quality_metrics"]["fragment_rate"] >= 0.0
    assert report_payload["failure_summary"]["read_errors_count"] == 1
    assert report_payload["output_fingerprints"]["parquet_sha256"]
    assert report == report_payload


def test_reextract_tranche_slice_rebuilds_rows_and_marks_unmatched(tmp_path):
    source_root = tmp_path / "sec_root"
    filing_path = source_root / "2024" / "QTR1" / "sample_10k.txt"
    _write_text(
        filing_path,
        (
            "Table of Contents\n"
            "Item 1. Business\n"
            "Business Overview Artificial intelligence supports workflows today.\n"
            "Item 1A. Risk Factors\n"
            "Artificial intelligence could expose us to cyber risks.\n"
        ),
    )

    keywords_path = tmp_path / "keywords.txt"
    _write_text(keywords_path, "artificial intelligence\nmachine learning\n")

    slice_path = tmp_path / "slice40.csv"
    pd.DataFrame(
        [
            {
                "source_file": "2024/QTR1/sample_10k.txt",
                "sentence_id": "s1",
                "sentence_index": 1,
                "sentence": "Business Overview Artificial intelligence supports workflows today.",
                "assistive_label": "Actionable",
                "label": "",
                "is_uncertain": "",
                "uncertainty_note": "",
            },
            {
                "source_file": "2024/QTR1/sample_10k.txt",
                "sentence_id": "s2",
                "sentence_index": 2,
                "sentence": "Artificial intelligence sentence never present in the filing.",
                "assistive_label": "Speculative",
                "label": "",
                "is_uncertain": "",
                "uncertainty_note": "",
            },
        ]
    ).to_csv(slice_path, index=False)

    output_path = tmp_path / "reextracted.csv"
    report_path = tmp_path / "report.json"

    report = reextract_tranche_slice(
        input_csv=str(slice_path),
        output_csv=str(output_path),
        report_path=str(report_path),
        source_root=str(source_root),
        keywords_path=str(keywords_path),
    )

    rebuilt = pd.read_csv(output_path)

    assert rebuilt.loc[0, "sentence"] == "Artificial intelligence supports workflows today."
    assert rebuilt.loc[0, "source_section"] == "item_1_business"
    assert rebuilt.loc[0, "match_status"] == "similarity"
    assert rebuilt.loc[1, "match_status"] == "unmatched"
    assert rebuilt["label"].fillna("").tolist() == ["", ""]
    assert rebuilt["is_uncertain"].fillna("").tolist() == ["", ""]
    assert rebuilt["uncertainty_note"].fillna("").tolist() == ["", ""]
    assert report["counts"]["slice_rows"] == 2
    assert report["counts"]["unmatched_rows"] == 1
