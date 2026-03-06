from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

from semantic_ai_washing.labeling.build_labeling_batch import build_labeling_batch
from semantic_ai_washing.labeling.common import normalize_sentence


def _sha1_short(payload: str) -> str:
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


def _sentence_row(
    *,
    sentence: str,
    source_file: str,
    quarter: int,
    sentence_index: int,
    manifest_id: str = "pilot_2024_10k_v1",
    cik: str = "1001",
    token_count: int | None = None,
    fragment_score: float = 0.0,
    sentence_text_id: str | None = None,
) -> dict[str, object]:
    sentence_norm = normalize_sentence(sentence)
    return {
        "sentence_id": _sha1_short(f"{source_file}|{sentence_index}|{sentence_norm}"),
        "sentence_text_id": sentence_text_id or _sha1_short(sentence_norm),
        "sentence": sentence,
        "sentence_norm": sentence_norm,
        "source_file": source_file,
        "source_year": 2024,
        "source_quarter": quarter,
        "source_form": "10-K",
        "source_cik": cik,
        "sentence_index": sentence_index,
        "extractor_version": "sentence_table_v1",
        "keyword_version": "keywords-v1",
        "manifest_id": manifest_id,
        "source_window_id": "active_2021_2024",
        "integrity_flags": "[]",
        "fragment_score": fragment_score,
        "token_count": token_count if token_count is not None else len(sentence.split()),
    }


def _manifest_row(
    *,
    path: str,
    quarter: int,
    manifest_row_id: str,
    cik: str,
    ff12_code: int,
    ff12_name: str,
    industry_metadata_source: str,
) -> dict[str, object]:
    return {
        "manifest_id": "pilot_2024_10k_v1",
        "manifest_row_id": manifest_row_id,
        "sampling_seed": 20260305,
        "selection_reason": "quarter_fill",
        "source_window_id": "active_2021_2024",
        "cik": cik,
        "year": 2024,
        "quarter": quarter,
        "form": "10-K",
        "filename": Path(path).name,
        "path": path,
        "sic": 3571 if industry_metadata_source != "unknown" else "",
        "ff12_code": ff12_code,
        "ff12_name": ff12_name,
        "industry_metadata_source": industry_metadata_source,
    }


def test_build_labeling_batch_filters_leakage_and_redistributes_quotas(tmp_path):
    manifest_rows = [
        _manifest_row(
            path="2024/QTR1/a.txt",
            quarter=1,
            manifest_row_id="m1",
            cik="1001",
            ff12_code=6,
            ff12_name="BusEq",
            industry_metadata_source="controls_by_firm_year",
        ),
        _manifest_row(
            path="2024/QTR1/b.txt",
            quarter=1,
            manifest_row_id="m2",
            cik="1002",
            ff12_code=12,
            ff12_name="Other",
            industry_metadata_source="unknown",
        ),
        _manifest_row(
            path="2024/QTR2/c.txt",
            quarter=2,
            manifest_row_id="m3",
            cik="1003",
            ff12_code=6,
            ff12_name="BusEq",
            industry_metadata_source="controls_by_firm_year",
        ),
        _manifest_row(
            path="2024/QTR2/d.txt",
            quarter=2,
            manifest_row_id="m4",
            cik="1004",
            ff12_code=11,
            ff12_name="Money",
            industry_metadata_source="controls_by_firm_year",
        ),
        _manifest_row(
            path="2024/QTR3/e.txt",
            quarter=3,
            manifest_row_id="m5",
            cik="1005",
            ff12_code=3,
            ff12_name="Manuf",
            industry_metadata_source="controls_by_firm_year",
        ),
        _manifest_row(
            path="2024/QTR3/f.txt",
            quarter=3,
            manifest_row_id="m6",
            cik="1006",
            ff12_code=12,
            ff12_name="Other",
            industry_metadata_source="unknown",
        ),
        _manifest_row(
            path="2024/QTR4/g.txt",
            quarter=4,
            manifest_row_id="m7",
            cik="1007",
            ff12_code=9,
            ff12_name="Shops",
            industry_metadata_source="controls_by_firm_year",
        ),
        _manifest_row(
            path="2024/QTR4/h.txt",
            quarter=4,
            manifest_row_id="m8",
            cik="1008",
            ff12_code=12,
            ff12_name="Other",
            industry_metadata_source="unknown",
        ),
    ]
    manifest = pd.DataFrame(manifest_rows)
    manifest_path = tmp_path / "manifest.csv"
    manifest.to_csv(manifest_path, index=False)

    duplicate_text_id = _sha1_short(normalize_sentence("Duplicate AI sentence for exact dedupe."))
    sentence_rows = [
        _sentence_row(
            sentence="Held out overlap sentence that must be removed.",
            source_file="2024/QTR1/a.txt",
            quarter=1,
            sentence_index=1,
            cik="1001",
        ),
        _sentence_row(
            sentence="Quarter one clean actionable sentence on current AI deployment.",
            source_file="2024/QTR1/b.txt",
            quarter=1,
            sentence_index=1,
            cik="1002",
        ),
        _sentence_row(
            sentence="Quarter two sentence one about current machine learning execution in operations.",
            source_file="2024/QTR2/c.txt",
            quarter=2,
            sentence_index=1,
            cik="1003",
        ),
        _sentence_row(
            sentence="Quarter two sentence two plans a future AI rollout with uncertain timelines.",
            source_file="2024/QTR2/c.txt",
            quarter=2,
            sentence_index=2,
            cik="1003",
        ),
        _sentence_row(
            sentence="Quarter two sentence three lists AI among concrete strategic priorities today.",
            source_file="2024/QTR2/d.txt",
            quarter=2,
            sentence_index=1,
            cik="1004",
        ),
        _sentence_row(
            sentence="Quarter two sentence four discusses machine learning risk and governance.",
            source_file="2024/QTR2/d.txt",
            quarter=2,
            sentence_index=2,
            cik="1004",
        ),
        _sentence_row(
            sentence="Duplicate AI sentence for exact dedupe.",
            source_file="2024/QTR3/e.txt",
            quarter=3,
            sentence_index=1,
            cik="1005",
            sentence_text_id=duplicate_text_id,
        ),
        _sentence_row(
            sentence="Duplicate AI sentence for exact dedupe.",
            source_file="2024/QTR3/f.txt",
            quarter=3,
            sentence_index=1,
            cik="1006",
            sentence_text_id=duplicate_text_id,
        ),
        _sentence_row(
            sentence="Quarter three distinct sentence on current AI product capabilities.",
            source_file="2024/QTR3/e.txt",
            quarter=3,
            sentence_index=2,
            cik="1005",
        ),
        _sentence_row(
            sentence="Quarter three exploratory AI strategy sentence with future language.",
            source_file="2024/QTR3/f.txt",
            quarter=3,
            sentence_index=2,
            cik="1006",
        ),
        _sentence_row(
            sentence="Quarter four sentence one on operational AI workflow improvement today.",
            source_file="2024/QTR4/g.txt",
            quarter=4,
            sentence_index=1,
            cik="1007",
        ),
        _sentence_row(
            sentence="Quarter four sentence two on future AI partnerships and expectations.",
            source_file="2024/QTR4/g.txt",
            quarter=4,
            sentence_index=2,
            cik="1007",
        ),
        _sentence_row(
            sentence="Quarter four sentence three generic AI market risk disclosure.",
            source_file="2024/QTR4/h.txt",
            quarter=4,
            sentence_index=1,
            cik="1008",
        ),
        _sentence_row(
            sentence="Quarter four short fragment",
            source_file="2024/QTR4/h.txt",
            quarter=4,
            sentence_index=2,
            cik="1008",
            token_count=4,
            fragment_score=0.25,
        ),
    ]
    sentences = pd.DataFrame(sentence_rows)
    sentences_path = tmp_path / "sentences.parquet"
    sentences.to_parquet(sentences_path, index=False)

    held_out_path = tmp_path / "held_out.csv"
    pd.DataFrame(
        [{"sentence": "Held out overlap sentence that must be removed.", "label": "Speculative"}]
    ).to_csv(held_out_path, index=False)

    output_parquet = tmp_path / "labeling_batch.parquet"
    output_csv = tmp_path / "labeling_batch.csv"
    report_path = tmp_path / "summary.json"

    summary = build_labeling_batch(
        sentences_path=str(sentences_path),
        manifest_path=str(manifest_path),
        held_out_path=str(held_out_path),
        output_parquet_path=str(output_parquet),
        output_csv_path=str(output_csv),
        report_path=str(report_path),
        batch_id="labeling_batch_v1",
        target_size=8,
        base_quarter_quota=2,
        min_tokens=6,
        max_tokens=120,
        seed=20260306,
    )

    batch = pd.read_parquet(output_parquet)
    assert len(batch) == 8
    assert batch["source_quarter"].value_counts().sort_index().to_dict() == {
        1: 1,
        2: 3,
        3: 2,
        4: 2,
    }
    assert batch["label"].tolist() == [""] * 8
    assert batch["is_uncertain"].tolist() == [""] * 8
    assert batch["uncertainty_note"].tolist() == [""] * 8
    assert (
        not batch["sentence_norm"]
        .isin({normalize_sentence("Held out overlap sentence that must be removed.")})
        .any()
    )
    assert int(batch["sentence_text_id"].duplicated().sum()) == 0
    assert set(batch["selection_reason"]) <= {
        "quarter_ff12_round_robin",
        "quarter_diversity_fill",
    }
    assert batch["batch_row_id"].is_unique

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload == summary
    assert payload["candidate_stats"]["heldout_overlap_removed"] == 1
    assert payload["candidate_stats"]["exact_text_duplicates_removed"] == 1
    assert payload["selection"]["quarter_quotas_used"] == {"1": 1, "2": 3, "3": 2, "4": 2}
    assert payload["quality"]["heldout_overlap_count"] == 0
    assert payload["quality"]["exact_duplicate_count"] == 0


def test_build_labeling_batch_fails_when_filtered_pool_is_too_small(tmp_path):
    manifest = pd.DataFrame(
        [
            _manifest_row(
                path="2024/QTR1/a.txt",
                quarter=1,
                manifest_row_id="m1",
                cik="1001",
                ff12_code=6,
                ff12_name="BusEq",
                industry_metadata_source="controls_by_firm_year",
            )
        ]
    )
    manifest_path = tmp_path / "manifest.csv"
    manifest.to_csv(manifest_path, index=False)

    sentences = pd.DataFrame(
        [
            _sentence_row(
                sentence="Only one clean AI sentence remains in the pool.",
                source_file="2024/QTR1/a.txt",
                quarter=1,
                sentence_index=1,
                cik="1001",
            )
        ]
    )
    sentences_path = tmp_path / "sentences.parquet"
    sentences.to_parquet(sentences_path, index=False)

    held_out_path = tmp_path / "held_out.csv"
    pd.DataFrame(columns=["sentence", "label"]).to_csv(held_out_path, index=False)

    with pytest.raises(ValueError, match="Eligible pool has 1 rows"):
        build_labeling_batch(
            sentences_path=str(sentences_path),
            manifest_path=str(manifest_path),
            held_out_path=str(held_out_path),
            output_parquet_path=str(tmp_path / "out.parquet"),
            output_csv_path=str(tmp_path / "out.csv"),
            report_path=str(tmp_path / "report.json"),
            target_size=2,
            base_quarter_quota=1,
        )
