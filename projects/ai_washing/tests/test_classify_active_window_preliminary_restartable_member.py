from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from ai_washing_member.classification import (
    classify_active_window_preliminary_restartable as member_restartable,
)


def _write_sentence_year(path: Path, year: int, rows: int = 5) -> None:
    frame = pd.DataFrame(
        [
            {
                "sentence_id": f"{year}-{idx}",
                "sentence_text_id": f"{year}-text-{idx}",
                "sentence": f"We use AI technologies in year {year} example {idx}.",
                "sentence_norm": f"we use ai technologies in year {year} example {idx}",
                "source_file": f"{year}_{idx}.txt",
                "source_year": year,
                "source_quarter": 1,
                "source_form": "10-K",
                "source_section": "other",
                "source_cik": f"{year}{idx:04d}",
                "sentence_index": idx,
                "extractor_version": "test",
                "keyword_version": "kw",
                "manifest_id": "manifest",
                "source_window_id": "window",
                "integrity_flags": "[]",
                "fragment_score": 0.0,
                "token_count": 9,
            }
            for idx in range(rows)
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)


def test_member_restartable_classification_writes_outputs_and_progress(
    tmp_path: Path, monkeypatch
) -> None:
    input_root = tmp_path / "sentences"
    _write_sentence_year(input_root / "year=2021" / "ai_sentences.parquet", 2021, rows=5)

    monkeypatch.setattr(
        member_restartable,
        "_resolve_runtime",
        lambda args: (
            {"model_id": "binary_relevance_then_as_v1", "model_type": "binary_relevance_then_as"},
            {"status": "selected"},
            "binary_relevance_then_as_v1",
            "annual_10k_2016_2024_clean",
        ),
    )

    def fake_predict(sentences: list[str], runtime_manifest: dict[str, str]):
        return ["Actionable"] * len(sentences), [
            {"Actionable": 0.8, "Speculative": 0.1, "Irrelevant": 0.1} for _ in sentences
        ]

    monkeypatch.setattr(member_restartable, "predict_sentences", fake_predict)

    args = argparse.Namespace(
        input_root=str(input_root),
        years=["2021"],
        centroids="",
        model_metadata="",
        selected_model_manifest="artifacts/models/prelim_selected_model_v1.json",
        output_root=str(tmp_path / "classifications"),
        output_report=str(tmp_path / "classification_report.json"),
        progress_report=str(tmp_path / "classification_progress.json"),
        model_id="binary_relevance_then_as_v1",
        source_window_id="annual_10k_2016_2024_clean",
        chunk_size=2,
        force_recompute=False,
    )

    report = member_restartable.run_classification_restartable(args)

    assert report["status"] == "passed"
    assert report["summary"]["rows_by_year"] == {"2021": 5}
    progress = json.loads(Path(args.progress_report).read_text(encoding="utf-8"))
    assert progress["status"] == "completed"
