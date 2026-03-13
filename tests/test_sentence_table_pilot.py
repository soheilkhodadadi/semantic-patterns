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
    assert clean_extracted_sentence(
        "Our Products and Suppliers We offer AI-enabled services."
    ) == ("We offer AI-enabled services.")
    assert clean_extracted_sentence(
        "Business Overview EPAM has used AI expertise to deliver services."
    ) == ("EPAM has used AI expertise to deliver services.")
    assert clean_extracted_sentence(
        "Executive Summary We have used AI expertise to deliver services."
    ) == ("We have used AI expertise to deliver services.")
    assert clean_extracted_sentence(
        "Data, Analytics and Artificial Intelligence With deep expertise, we build data tools."
    ) == ("With deep expertise, we build data tools.")
    assert clean_extracted_sentence(
        "The pace of FREDDIE MAC | 2023 Form 10-K 128 Risk Factors technological change matters."
    ) == ("The pace of technological change matters.")
    assert clean_extracted_sentence(
        "Our systems are vulnerable to disruptions, including 20 Table of Contents computer viruses."
    ) == ("Our systems are vulnerable to disruptions, including computer viruses.")
    assert clean_extracted_sentence(
        "Additionally, our information could be leaked, 89 Table of Contents disclosed or revealed."
    ) == ("Additionally, our information could be leaked, disclosed or revealed.")
    assert clean_extracted_sentence("N AI/ML - Artificial Intelligence/Machine Learning.") == ""


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
                "sentence": "N AI/ML - Artificial Intelligence/Machine Learning.",
                "assistive_label": "Speculative",
                "label": "",
                "is_uncertain": "",
                "uncertainty_note": "",
            },
            {
                "source_file": "2024/QTR1/sample_10k.txt",
                "sentence_id": "s3",
                "sentence_index": 3,
                "sentence": (
                    "Our IT systems are vulnerable to disruptions, including 20 Table of "
                    "Contents computer viruses and attacks enabled by AI."
                ),
                "assistive_label": "Irrelevant",
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

    rebuilt = pd.read_csv(output_path, keep_default_na=False)

    assert rebuilt.loc[0, "sentence"] == "Artificial intelligence supports workflows today."
    assert rebuilt.loc[0, "source_section"] == "item_1_business"
    assert rebuilt.loc[0, "match_status"] == "exact"
    assert rebuilt.loc[0, "prelabel_eligible"] in (True, "True")
    assert rebuilt.loc[0, "skip_reason"] in ("", None)
    assert rebuilt.loc[1, "match_status"] == "unmatched"
    assert rebuilt.loc[1, "sentence"] == ""
    assert rebuilt.loc[1, "prelabel_eligible"] in (False, "False")
    assert rebuilt.loc[1, "skip_reason"] == "unmatched_noise"
    assert "Table of Contents" not in rebuilt.loc[2, "sentence"]
    assert rebuilt.loc[2, "match_status"] in {"unmatched", "similarity", "exact"}
    assert rebuilt["label"].fillna("").tolist() == ["", "", ""]
    assert rebuilt["is_uncertain"].fillna("").tolist() == ["", "", ""]
    assert rebuilt["uncertainty_note"].fillna("").tolist() == ["", "", ""]
    assert rebuilt["assistive_label"].fillna("").tolist() == ["", "", ""]
    assert report["counts"]["slice_rows"] == 3
    assert report["counts"]["unmatched_rows"] == 2
    assert report["counts"]["unmatched_noise_rows"] == 2
    assert report["counts"]["unmatched_meaningful_rows"] == 0
    assert report["counts"]["prelabel_ineligible_rows"] == 2
    assert report["counts"]["cleaned_rows"] >= 2
    assert report["cleanup_hits"]["glossary_fragment"] == 1
    assert report["cleanup_hits"]["table_of_contents"] >= 1


def test_reextract_tranche_slice_rescues_meaningful_unmatched_rows(tmp_path):
    source_root = tmp_path / "sec-root"
    keywords_path = tmp_path / "keywords.txt"
    keywords_path.write_text("artificial intelligence\nai\nmachine learning\n", encoding="utf-8")

    filing_path = (
        source_root / "2024/QTR1/20240222_10-K_edgar_data_1352010_0001352010-24-000008.txt"
    )
    _write_text(
        filing_path,
        (
            "Item 1. Business. We have used our software engineering expertise to become "
            "a leading global provider of digital engineering, cloud and AI-enabled "
            "transformation services. "
            "Item 1A. Risk Factors. Any of these risks could expose us to liability or "
            "adverse legal or regulatory consequences. 29 In addition to our use of AI "
            "technologies, we are exposed to risks arising from the use of AI technologies "
            "by bad actors to commit fraud and misappropriate funds and to facilitate cyberattacks."
        ),
    )

    slice_path = tmp_path / "slice.csv"
    pd.DataFrame(
        [
            {
                "source_file": "2024/QTR1/20240222_10-K_edgar_data_1352010_0001352010-24-000008.txt",
                "sentence_id": "d585b999ea5eaa56",
                "sentence_index": 3,
                "sentence": (
                    "Data, Analytics and Artificial Intelligence With deep expertise in "
                    "data and analytics, business intelligence and cloud platform "
                    "development, we navigate the complexities of building and scaling "
                    "new data capabilities necessary for the evolving environment."
                ),
                "label": "",
                "is_uncertain": "",
                "uncertainty_note": "",
                "assistive_label": "",
            },
            {
                "source_file": "2024/QTR1/20240222_10-K_edgar_data_1352010_0001352010-24-000008.txt",
                "sentence_id": "349b4c7239a5efd0",
                "sentence_index": 9,
                "sentence": (
                    "29 In addition to our use of AI technologies, we are exposed to risks "
                    "arising from the use of AI technologies by bad actors to commit fraud "
                    "and misappropriate funds and to facilitate cyberattacks."
                ),
                "label": "",
                "is_uncertain": "",
                "uncertainty_note": "",
                "assistive_label": "",
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

    rebuilt = pd.read_csv(output_path, keep_default_na=False)

    provider_row = rebuilt.loc[rebuilt["sentence_id"] == "d585b999ea5eaa56"].iloc[0]
    assert provider_row["match_status"] == "rescued_similarity"
    assert "provider of digital engineering" in provider_row["sentence"]
    assert provider_row["prelabel_eligible"] in (True, "True")

    clause_row = rebuilt.loc[rebuilt["sentence_id"] == "349b4c7239a5efd0"].iloc[0]
    assert clause_row["match_status"] == "rescued_clause"
    assert clause_row["sentence"].startswith("In addition to our use of AI technologies")
    assert not clause_row["sentence"].startswith("29 ")

    assert report["counts"]["rescued_similarity_rows"] == 1
    assert report["counts"]["rescued_clause_rows"] == 1
    assert set(report["rescued_sentence_ids"]) == {
        "d585b999ea5eaa56",
        "349b4c7239a5efd0",
    }
