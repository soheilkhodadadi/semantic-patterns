from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from ai_washing_member.labeling import freeze_heldout_v2, sample_heldout_v2_candidates


REQUIRED_COLUMNS = [
    "sentence_id",
    "sentence",
    "source_cik",
    "source_year",
    "source_form",
    "source_file",
    "sentence_index",
]


def _write_sentence_year(path: Path, year: int, rows_per_label: int = 80) -> None:
    records = []
    labels = ["Actionable", "Speculative", "Irrelevant"]
    for label_idx, label in enumerate(labels):
        for idx in range(rows_per_label):
            global_idx = label_idx * rows_per_label + idx
            records.append(
                {
                    "sentence_id": f"{year}-{label}-{idx}",
                    "sentence": f"{label} sentence {year} {idx}",
                    "source_cik": f"{year}{label_idx:02d}{idx:04d}",
                    "source_year": year,
                    "source_form": "10-K",
                    "source_file": f"{year}_{label}_{idx}.txt",
                    "sentence_index": global_idx,
                }
            )
    frame = pd.DataFrame.from_records(records, columns=REQUIRED_COLUMNS)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)


def test_sample_heldout_v2_candidates_builds_review_pack(tmp_path: Path, monkeypatch) -> None:
    input_root = tmp_path / "sentences"
    _write_sentence_year(input_root / "year=2021" / "ai_sentences.parquet", 2021)
    _write_sentence_year(input_root / "year=2024" / "ai_sentences.parquet", 2024)

    labels_master = tmp_path / "labels_master.parquet"
    pd.DataFrame({"sentence": ["existing labeled sentence"]}).to_parquet(
        labels_master, index=False
    )
    historical = tmp_path / "historical.csv"
    pd.DataFrame({"sentence": ["historical heldout sentence"]}).to_csv(historical, index=False)

    monkeypatch.setattr(
        sample_heldout_v2_candidates, "build_legacy_two_stage_runtime", lambda: object()
    )

    def fake_predict(sentences: list[str], _runtime):
        labels = []
        for text in sentences:
            if text.startswith("Actionable"):
                labels.append("Actionable")
            elif text.startswith("Speculative"):
                labels.append("Speculative")
            else:
                labels.append("Irrelevant")
        return labels, None

    monkeypatch.setattr(sample_heldout_v2_candidates, "predict_sentences", fake_predict)

    args = argparse.Namespace(
        input_root=str(input_root),
        years=["2021", "2024"],
        labels_master=str(labels_master),
        historical_held_out=str(historical),
        output_csv=str(tmp_path / "heldout_v2_review.csv"),
        output_xlsx=str(tmp_path / "heldout_v2_review.xlsx"),
        output_report=str(tmp_path / "heldout_v2_report.json"),
        prelabeler="legacy_two_stage",
    )

    report = sample_heldout_v2_candidates.run_sampling(args)

    review = pd.read_csv(args.output_csv)
    assert len(review) == 180
    assert review["candidate_label"].value_counts().to_dict() == {
        "Actionable": 60,
        "Speculative": 60,
        "Irrelevant": 60,
    }
    assert Path(args.output_xlsx).exists()
    assert report["status"] == "pending_review"
    saved_report = json.loads(Path(args.output_report).read_text())
    assert saved_report["summary"]["rows_selected"] == 180


def test_sample_heldout_v2_candidates_supports_heuristic_prelabeler(tmp_path: Path) -> None:
    input_root = tmp_path / "sentences"

    def write_heuristic_year(path: Path, year: int) -> None:
        records = []
        for idx in range(80):
            records.append(
                {
                    "sentence_id": f"{year}-A-{idx}",
                    "sentence": (
                        f"We deployed AI systems into production workflows in {year} case {idx}."
                    ),
                    "source_cik": f"{year}A{idx:04d}",
                    "source_year": year,
                    "source_form": "10-K",
                    "source_file": f"{year}_actionable_{idx}.txt",
                    "sentence_index": idx,
                }
            )
            records.append(
                {
                    "sentence_id": f"{year}-S-{idx}",
                    "sentence": (
                        "We plan to focus on AI capabilities in future releases "
                        f"for {year} case {idx}."
                    ),
                    "source_cik": f"{year}S{idx:04d}",
                    "source_year": year,
                    "source_form": "10-K",
                    "source_file": f"{year}_speculative_{idx}.txt",
                    "sentence_index": 1000 + idx,
                }
            )
            records.append(
                {
                    "sentence_id": f"{year}-I-{idx}",
                    "sentence": (
                        "Our AI infrastructure and laws and regulations discussion "
                        f"continued in {year} case {idx}."
                    ),
                    "source_cik": f"{year}I{idx:04d}",
                    "source_year": year,
                    "source_form": "10-K",
                    "source_file": f"{year}_irrelevant_{idx}.txt",
                    "sentence_index": 2000 + idx,
                }
            )
        frame = pd.DataFrame.from_records(records, columns=REQUIRED_COLUMNS)
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_parquet(path, index=False)

    write_heuristic_year(input_root / "year=2021" / "ai_sentences.parquet", 2021)
    write_heuristic_year(input_root / "year=2024" / "ai_sentences.parquet", 2024)

    labels_master = tmp_path / "labels_master.parquet"
    pd.DataFrame({"sentence": ["existing labeled sentence"]}).to_parquet(
        labels_master, index=False
    )
    historical = tmp_path / "historical.csv"
    pd.DataFrame({"sentence": ["historical heldout sentence"]}).to_csv(historical, index=False)

    args = argparse.Namespace(
        input_root=str(input_root),
        years=["2021", "2024"],
        labels_master=str(labels_master),
        historical_held_out=str(historical),
        output_csv=str(tmp_path / "heldout_v2_review.csv"),
        output_xlsx=str(tmp_path / "heldout_v2_review.xlsx"),
        output_report=str(tmp_path / "heldout_v2_report.json"),
        prelabeler="heuristic",
    )

    report = sample_heldout_v2_candidates.run_sampling(args)

    review = pd.read_csv(args.output_csv)
    assert len(review) == 180
    assert report["status"] == "pending_review"


def test_freeze_heldout_v2_requires_complete_balanced_labels(tmp_path: Path) -> None:
    reviewed = tmp_path / "reviewed.xlsx"
    records = []
    for label in ["Actionable", "Speculative", "Irrelevant"]:
        for idx in range(60):
            records.append(
                {
                    "sentence_id": f"{label}-{idx}",
                    "sentence": f"{label} sentence {idx}",
                    "candidate_label": label,
                    "label": label,
                }
            )
    pd.DataFrame.from_records(records).to_excel(reviewed, index=False)

    args = argparse.Namespace(
        reviewed_input=str(reviewed),
        output_csv=str(tmp_path / "held_out_v2.csv"),
        output_report=str(tmp_path / "held_out_v2_report.json"),
    )

    report, exit_code = freeze_heldout_v2.run_freeze(args)

    assert exit_code == 0
    assert report["status"] == "frozen"
    frozen = pd.read_csv(args.output_csv)
    assert len(frozen) == 180
    assert "candidate_label" not in frozen.columns


def test_freeze_heldout_v2_allows_reviewed_unbalanced_asset_with_exclusions(
    tmp_path: Path,
) -> None:
    reviewed = tmp_path / "reviewed.csv"
    pd.DataFrame.from_records(
        [
            {
                "sentence_id": "keep-actionable",
                "sentence": "Actionable sentence",
                "candidate_label": "Actionable",
                "label": "Actionable",
            },
            {
                "sentence_id": "keep-irrelevant",
                "sentence": "Irrelevant sentence",
                "candidate_label": "Irrelevant",
                "label": "Irrelevant",
            },
            {
                "sentence_id": "drop-invalid",
                "sentence": "Broken OCR",
                "candidate_label": "Irrelevant",
                "label": "Irrelevant",
            },
        ]
    ).to_csv(reviewed, index=False)

    args = argparse.Namespace(
        reviewed_input=str(reviewed),
        output_csv=str(tmp_path / "held_out_v2.csv"),
        output_report=str(tmp_path / "held_out_v2_report.json"),
        exclude_sentence_ids=["drop-invalid"],
        enforce_target_counts=False,
    )

    report, exit_code = freeze_heldout_v2.run_freeze(args)

    assert exit_code == 0
    assert report["status"] == "frozen"
    assert report["summary"]["target_counts_met"] is False
    assert report["summary"]["enforce_target_counts"] is False
    assert report["summary"]["rows_excluded"] == 1
    frozen = pd.read_csv(args.output_csv)
    assert len(frozen) == 2
    assert "drop-invalid" not in set(frozen["sentence_id"])
