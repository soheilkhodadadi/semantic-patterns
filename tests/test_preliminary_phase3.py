from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import pytest

from semantic_ai_washing.aggregation.build_preliminary_narrative_measures import run_measure_build
from semantic_ai_washing.analysis.audit_preliminary_panel_inputs import run_audit
from ai_washing_member.classification.classify_active_window_preliminary import (
    run_classification,
)
from ai_washing_member.classification.evaluate_preliminary_heldout import run_evaluation
from ai_washing_member.classification.train_preliminary_centroids import run_training
from semantic_ai_washing.core import sentence_filter
from semantic_ai_washing.data.materialize_active_window_sentences import run_materialization

pytest.importorskip("pyarrow", reason="pyarrow is required for parquet-backed preliminary tests")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _make_filing(root: Path, year: int, cik: str, stem: str, text: str) -> None:
    filing = root / f"{year}" / "QTR1" / f"{year}0101_10-K_edgar_data_{cik}_{stem}.txt"
    _write_text(filing, text)


def test_materialize_active_window_sentences_builds_and_reuses_outputs(tmp_path, monkeypatch):
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
    for year in (2021, 2022, 2023, 2024):
        assert (
            tmp_path / "processed" / "sentences" / f"year={year}" / "ai_sentences.parquet"
        ).exists()

    rerun = run_materialization(args)
    assert rerun["summary"]["years_reused"] == [2021, 2022, 2023, 2024]


def test_preliminary_training_eval_classification_and_measures_hash_backend(tmp_path):
    labels_master = tmp_path / "labels_master.parquet"
    split_registry = tmp_path / "split_registry_v1.csv"
    held_out = tmp_path / "held_out_sentences.csv"

    labels_rows = [
        {
            "sentence_id": "a1",
            "sentence": "We deployed AI systems across operations.",
            "label": "Actionable",
            "source_cik": "1001",
            "source_year": 2024,
        },
        {
            "sentence_id": "a2",
            "sentence": "Our AI tools improved workflow efficiency.",
            "label": "Actionable",
            "source_cik": "1002",
            "source_year": 2024,
        },
        {
            "sentence_id": "s1",
            "sentence": "We plan to expand AI capabilities next year.",
            "label": "Speculative",
            "source_cik": "1003",
            "source_year": 2024,
        },
        {
            "sentence_id": "s2",
            "sentence": "Management intends to build new AI products.",
            "label": "Speculative",
            "source_cik": "1004",
            "source_year": 2024,
        },
        {
            "sentence_id": "i1",
            "sentence": "Generic AI regulation and market risk language.",
            "label": "Irrelevant",
            "source_cik": "1005",
            "source_year": 2024,
        },
        {
            "sentence_id": "i2",
            "sentence": "Artificial intelligence trends are widely discussed.",
            "label": "Irrelevant",
            "source_cik": "1006",
            "source_year": 2024,
        },
        {
            "sentence_id": "v1",
            "sentence": "AI deployment supports our products today.",
            "label": "Actionable",
            "source_cik": "1007",
            "source_year": 2024,
        },
        {
            "sentence_id": "v2",
            "sentence": "We may launch AI features in the future.",
            "label": "Speculative",
            "source_cik": "1008",
            "source_year": 2024,
        },
        {
            "sentence_id": "v3",
            "sentence": "This paragraph only mentions AI as a trend.",
            "label": "Irrelevant",
            "source_cik": "1009",
            "source_year": 2024,
        },
    ]
    pd.DataFrame(labels_rows).to_parquet(labels_master, index=False)
    pd.DataFrame(
        [
            {"sentence_id": "a1", "split": "train", "split_version": "v1", "seed": 20260315},
            {"sentence_id": "a2", "split": "train", "split_version": "v1", "seed": 20260315},
            {"sentence_id": "s1", "split": "train", "split_version": "v1", "seed": 20260315},
            {"sentence_id": "s2", "split": "train", "split_version": "v1", "seed": 20260315},
            {"sentence_id": "i1", "split": "train", "split_version": "v1", "seed": 20260315},
            {"sentence_id": "i2", "split": "train", "split_version": "v1", "seed": 20260315},
            {"sentence_id": "v1", "split": "validation", "split_version": "v1", "seed": 20260315},
            {"sentence_id": "v2", "split": "validation", "split_version": "v1", "seed": 20260315},
            {"sentence_id": "v3", "split": "validation", "split_version": "v1", "seed": 20260315},
        ]
    ).to_csv(split_registry, index=False)
    pd.DataFrame(
        [
            {
                "sentence": "Our deployed AI platform supports customers now.",
                "label": "Actionable",
            },
            {"sentence": "We intend to expand AI capabilities next year.", "label": "Speculative"},
            {"sentence": "AI market trends are discussed generically.", "label": "Irrelevant"},
        ]
    ).to_csv(held_out, index=False)

    sentence_root = tmp_path / "processed" / "sentences"
    for year in (2021, 2022, 2023, 2024):
        year_dir = sentence_root / f"year={year}"
        year_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(
            [
                {
                    "sentence_id": f"{year}_1",
                    "sentence": f"Firm {year} deployed AI tools in production.",
                    "source_year": year,
                    "source_cik": f"{year}001",
                    "source_file": f"{year}_a.txt",
                },
                {
                    "sentence_id": f"{year}_2",
                    "sentence": f"Firm {year} plans future AI capabilities.",
                    "source_year": year,
                    "source_cik": f"{year}002",
                    "source_file": f"{year}_b.txt",
                },
            ]
        ).to_parquet(year_dir / "ai_sentences.parquet", index=False)

    metadata = run_training(
        argparse.Namespace(
            labels_master=str(labels_master),
            split_registry=str(split_registry),
            embeddings_output=str(
                tmp_path / "artifacts" / "mpnet_prelim_v1" / "embeddings.parquet"
            ),
            centroids_output=str(tmp_path / "artifacts" / "mpnet_prelim_v1" / "centroids.json"),
            metadata_output=str(tmp_path / "artifacts" / "mpnet_prelim_v1" / "metadata.json"),
            model_id="mpnet_prelim_v1",
            source_window_id="active_2021_2024",
            embedding_backend="hash",
            model_name="hash://bow",
            batch_size=8,
            hash_dim=32,
        )
    )
    assert metadata["status"] == "trained"
    assert metadata["summary"]["rows_train"] == 6

    eval_report = run_evaluation(
        argparse.Namespace(
            held_out=str(held_out),
            labels_master=str(labels_master),
            centroids=str(tmp_path / "artifacts" / "mpnet_prelim_v1" / "centroids.json"),
            model_metadata=str(tmp_path / "artifacts" / "mpnet_prelim_v1" / "metadata.json"),
            output_report=str(tmp_path / "reports" / "heldout_eval_prelim_v1.json"),
            model_id="mpnet_prelim_v1",
            source_window_id="active_2021_2024",
            embedding_backend="hash",
            model_name="hash://bow",
            batch_size=8,
            hash_dim=32,
            accuracy_threshold=0.8,
        )
    )
    assert eval_report["summary"]["status"] == "passed"
    assert eval_report["summary"]["leakage_detected"] is False

    classify_report = run_classification(
        argparse.Namespace(
            input_root=str(sentence_root),
            years=["2021", "2022", "2023", "2024"],
            centroids=str(tmp_path / "artifacts" / "mpnet_prelim_v1" / "centroids.json"),
            model_metadata=str(tmp_path / "artifacts" / "mpnet_prelim_v1" / "metadata.json"),
            output_root=str(tmp_path / "processed" / "classifications"),
            output_report=str(tmp_path / "reports" / "active_window_coverage_prelim_v1.json"),
            model_id="mpnet_prelim_v1",
            source_window_id="active_2021_2024",
            embedding_backend="hash",
            model_name="hash://bow",
            batch_size=8,
            hash_dim=32,
        )
    )
    assert classify_report["summary"]["completed_year_count"] == 4

    measure_report = run_measure_build(
        argparse.Namespace(
            input_root=str(tmp_path / "processed" / "classifications"),
            years=["2021", "2022", "2023", "2024"],
            model_id="mpnet_prelim_v1",
            source_window_id="active_2021_2024",
            output_ai_metrics=str(
                tmp_path / "processed" / "aggregates" / "firm_year_ai_metrics_prelim_v1.parquet"
            ),
            output_measures=str(
                tmp_path
                / "processed"
                / "aggregates"
                / "firm_year_narrative_measures_prelim_v1.parquet"
            ),
            output_report=str(
                tmp_path / "reports" / "firm_year_narrative_measures_prelim_v1.json"
            ),
        )
    )
    assert measure_report["summary"]["named_measures_complete"] is True
    measures = pd.read_parquet(
        tmp_path / "processed" / "aggregates" / "firm_year_narrative_measures_prelim_v1.parquet"
    )
    assert {"AI_Focus", "log_1p_A", "log_1p_S", "SpecShare", "CredAI", "A_S"}.issubset(
        measures.columns
    )


def test_audit_preliminary_panel_inputs_blocks_sample_and_accepts_full(tmp_path):
    narrative_measures = tmp_path / "firm_year_narrative_measures_prelim_v1.parquet"
    pd.DataFrame(
        [
            {"source_cik": "0000001001", "source_year": 2021},
            {"source_cik": "0000001001", "source_year": 2022},
            {"source_cik": "0000001002", "source_year": 2023},
            {"source_cik": "0000001002", "source_year": 2024},
        ]
    ).to_parquet(narrative_measures, index=False)

    controls = tmp_path / "controls_by_firm_year.csv"
    patents = tmp_path / "ai_patent_counts_filtered_2019plus.csv"
    crosswalk = tmp_path / "cik_gvkey.csv"
    pd.DataFrame(
        [
            {"cik": "1001", "year": 2021},
            {"cik": "1001", "year": 2022},
            {"cik": "1002", "year": 2023},
            {"cik": "1002", "year": 2024},
        ]
    ).to_csv(controls, index=False)
    pd.DataFrame(
        [
            {"cik": "1001", "year": 2021},
            {"cik": "1001", "year": 2022},
            {"cik": "1002", "year": 2023},
            {"cik": "1002", "year": 2024},
        ]
    ).to_csv(patents, index=False)
    pd.DataFrame([{"cik": "1001", "gvkey": "1"}, {"cik": "1002", "gvkey": "2"}]).to_csv(
        crosswalk, index=False
    )

    sample_report = run_audit(
        argparse.Namespace(
            controls=str(controls),
            patents=str(patents),
            crosswalk=str(crosswalk),
            narrative_measures=str(narrative_measures),
            raw_controls=[str(tmp_path / "compustat_sample.csv")],
            raw_patents=[str(tmp_path / "sample_patents.csv")],
            controls_cik_column="cik",
            controls_year_column="year",
            patents_cik_column="cik",
            patents_year_column="year",
            source_window_id="active_2021_2024",
            output_report=str(tmp_path / "reports" / "sample_manifest.json"),
        )
    )
    assert sample_report["status"] == "blocked_refresh_required"
    assert sample_report["summary"]["controls_source_mode"] == "sample"
    assert sample_report["summary"]["patents_source_mode"] == "sample"

    ready_report = run_audit(
        argparse.Namespace(
            controls=str(controls),
            patents=str(patents),
            crosswalk=str(crosswalk),
            narrative_measures=str(narrative_measures),
            raw_controls=[str(tmp_path / "compustat_full_extract.csv")],
            raw_patents=[str(tmp_path / "patents_full_extract.csv")],
            controls_cik_column="cik",
            controls_year_column="year",
            patents_cik_column="cik",
            patents_year_column="year",
            source_window_id="active_2021_2024",
            output_report=str(tmp_path / "reports" / "ready_manifest.json"),
        )
    )
    assert ready_report["status"] == "ready"
    assert ready_report["summary"]["controls_year_coverage"] == [2021, 2022, 2023, 2024]
    assert ready_report["summary"]["patents_year_coverage"] == [2021, 2022, 2023, 2024]
