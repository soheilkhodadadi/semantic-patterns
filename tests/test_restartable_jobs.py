from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

import pandas as pd

from semantic_ai_washing.data.run_historical_backfill import run_backfill
from semantic_ai_washing.labeling.sample_heldout_v2_restartable import run_sampling_restartable


def _write_sentence_table(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(path, index=False)


def test_run_sampling_restartable_creates_progress_and_outputs(tmp_path, monkeypatch) -> None:
    input_root = tmp_path / "sentences"
    rows_by_year: dict[int, list[dict[str, object]]] = {}
    for year in (2021, 2022, 2023, 2024):
        rows: list[dict[str, object]] = []
        for prefix, label_word in (
            ("a", "actionable"),
            ("s", "speculative"),
            ("i", "irrelevant"),
        ):
            for idx in range(16):
                cik_value = year * 1_000_000 + (ord(prefix) * 100) + idx
                rows.append(
                    {
                        "sentence_id": f"{prefix}-{year}-{idx:02d}",
                        "sentence": f"{label_word} sentence {year}-{idx}",
                        "source_cik": cik_value,
                        "source_year": year,
                        "source_form": "10-K",
                        "source_file": f"{cik_value}.txt",
                        "sentence_index": idx,
                    }
                )
        rows_by_year[year] = rows
        _write_sentence_table(input_root / f"year={year}" / "ai_sentences.parquet", rows)

    labels_master = tmp_path / "labels_master.parquet"
    pd.DataFrame({"sentence": ["already labeled sentence"]}).to_parquet(labels_master, index=False)
    held_out = tmp_path / "held_out.csv"
    pd.DataFrame({"sentence": ["historical sentence"]}).to_csv(held_out, index=False)

    def fake_predict(sentences, *, prelabeler="legacy_two_stage"):
        assert prelabeler == "legacy_two_stage"
        predicted = []
        for sentence in sentences:
            lowered = sentence.lower()
            if "actionable" in lowered:
                predicted.append("Actionable")
            elif "speculative" in lowered:
                predicted.append("Speculative")
            else:
                predicted.append("Irrelevant")
        return predicted

    monkeypatch.setattr(
        "semantic_ai_washing.labeling.sample_heldout_v2_restartable.predict_candidate_labels",
        fake_predict,
    )

    args = Namespace(
        input_root=str(input_root),
        years=["2021", "2022", "2023", "2024"],
        labels_master=str(labels_master),
        historical_held_out=str(held_out),
        output_csv=str(tmp_path / "held_out_v2.csv"),
        output_xlsx=str(tmp_path / "held_out_v2.xlsx"),
        output_report=str(tmp_path / "held_out_v2_report.json"),
        progress_report=str(tmp_path / "held_out_v2_progress.json"),
        cache_dir=str(tmp_path / "cache"),
        batch_size=10,
        prelabeler="legacy_two_stage",
        force_recompute=False,
    )

    report = run_sampling_restartable(args)

    assert report["status"] == "pending_review"
    progress = json.loads(Path(args.progress_report).read_text(encoding="utf-8"))
    assert progress["status"] == "completed"
    assert Path(args.output_csv).exists()
    assert Path(args.output_xlsx).exists()
    assert Path(args.output_report).exists()
    selected = pd.read_csv(args.output_csv)
    assert int(selected["source_cik"].astype(str).nunique()) == 180


def test_run_backfill_indexes_only_annual_forms(tmp_path) -> None:
    root = tmp_path / "sec"
    (root / "2016" / "QTR1").mkdir(parents=True)
    (root / "2017" / "QTR2").mkdir(parents=True)
    annual = root / "2016" / "QTR1" / "20160115_10-K_edgar_data_1000_example.txt"
    quarterly = root / "2016" / "QTR1" / "20160315_10-Q_edgar_data_2000_example.txt"
    annual_2 = root / "2017" / "QTR2" / "20170415_10-K-A_edgar_data_3000_example.txt"
    annual.write_text("annual", encoding="utf-8")
    quarterly.write_text("quarterly", encoding="utf-8")
    annual_2.write_text("annual amended", encoding="utf-8")

    args = Namespace(
        source_root=str(root),
        source_root_hint="",
        years=["2016", "2017"],
        forms=["10-K", "10-K-A"],
        output_csv=str(tmp_path / "index.csv"),
        output_source_windows=str(tmp_path / "source_windows.json"),
        output_summary=str(tmp_path / "summary.json"),
        progress_report=str(tmp_path / "progress.json"),
        cache_dir=str(tmp_path / "cache"),
        materialize_years=[],
        output_root=str(tmp_path / "sentences"),
        keywords_path="data/metadata/ai_keywords.txt",
        min_tokens=6,
        sample_size=10,
        materialization_report_template=str(tmp_path / "materialization_{year}.json"),
        force_recompute=False,
    )

    report = run_backfill(args)

    assert report["status"] == "completed"
    frame = pd.read_csv(args.output_csv, dtype={"cik": str})
    assert sorted(frame["form"].unique().tolist()) == ["10-K", "10-K-A"]
    assert len(frame) == 2
    progress = json.loads(Path(args.progress_report).read_text(encoding="utf-8"))
    assert progress["status"] == "completed"


def test_run_backfill_fails_when_requested_year_is_missing(tmp_path) -> None:
    root = tmp_path / "sec"
    (root / "2016" / "QTR1").mkdir(parents=True)
    (root / "2016" / "QTR1" / "20160115_10-K_edgar_data_1000_example.txt").write_text(
        "annual",
        encoding="utf-8",
    )

    args = Namespace(
        source_root=str(root),
        source_root_hint="",
        years=["2016", "2017"],
        forms=["10-K", "10-K-A"],
        output_csv=str(tmp_path / "index.csv"),
        output_source_windows=str(tmp_path / "source_windows.json"),
        output_summary=str(tmp_path / "summary.json"),
        progress_report=str(tmp_path / "progress.json"),
        cache_dir=str(tmp_path / "cache"),
        materialize_years=[],
        output_root=str(tmp_path / "sentences"),
        keywords_path="data/metadata/ai_keywords.txt",
        min_tokens=6,
        sample_size=10,
        materialization_report_template=str(tmp_path / "materialization_{year}.json"),
        force_recompute=False,
    )

    report = run_backfill(args)

    assert report["status"] == "failed"
    assert report["summary"]["missing_years"] == [2017]
    progress = json.loads(Path(args.progress_report).read_text(encoding="utf-8"))
    assert progress["status"] == "failed"
