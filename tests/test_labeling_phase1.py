from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import pandas as pd

from semantic_ai_washing.labeling.build_labeling_sample import run_build
from semantic_ai_washing.labeling.common import (
    compute_sample_id,
    compute_sentence_id,
    normalize_sentence,
)
from semantic_ai_washing.labeling.dedupe_labeled_sentences import OUTPUT_COLUMNS, run_dedupe
from semantic_ai_washing.labeling.qa_labeled_dataset import run_qa


def _write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _base_row(
    sentence: str,
    label: str = "Actionable",
    sample_id: str | None = None,
    sentence_id: str | None = None,
    source_file: str = "file_a",
    sentence_index: int = 1,
) -> dict:
    sentence_norm = normalize_sentence(sentence)
    return {
        "sample_id": sample_id or compute_sample_id(source_file, sentence_index, sentence_norm),
        "sentence_id": sentence_id or compute_sentence_id(sentence_norm),
        "sentence": sentence,
        "sentence_norm": sentence_norm,
        "label": label,
        "is_uncertain": 0,
        "uncertainty_note": "",
        "source_file": source_file,
        "source_year": "2024",
        "source_form": "10-K",
        "source_cik": "1001",
        "sentence_index": sentence_index,
        "sic": "3571",
        "sic2": "35",
        "ff12_code": 6,
        "ff12_name": "BusEq",
        "token_count": len(sentence.split()),
        "length_bin": "medium",
        "edge_case_flag": 0,
    }


def test_normalization_collapses_punctuation_case_and_whitespace():
    variant_a = "AI   systems, ARE deployed."
    variant_b = "ai systems are deployed"
    assert normalize_sentence(variant_a) == normalize_sentence(variant_b)


def test_stable_ids_are_deterministic():
    sentence_norm = normalize_sentence("We deploy AI models into production")
    sample_1 = compute_sample_id("path/file.txt", 7, sentence_norm)
    sample_2 = compute_sample_id("path/file.txt", 7, sentence_norm)
    sent_1 = compute_sentence_id(sentence_norm)
    sent_2 = compute_sentence_id(sentence_norm)
    assert sample_1 == sample_2
    assert sent_1 == sent_2


def test_build_sample_excludes_heldout_overlap(tmp_path):
    base_labeled = tmp_path / "base.csv"
    held_out = tmp_path / "held_out.csv"
    controls = tmp_path / "controls.csv"
    crosswalk = tmp_path / "crosswalk.csv"
    input_dir = tmp_path / "sec"
    output_dir = tmp_path / "out"
    report_dir = tmp_path / "report"

    _write_csv(
        base_labeled,
        [{"sentence": "Existing base sentence", "label": "Actionable"}],
        ["sentence", "label"],
    )
    _write_csv(
        held_out,
        [{"sentence": "Held out sentence overlap", "label": "Speculative"}],
        ["sentence", "label"],
    )
    _write_csv(controls, [{"cik": "1001", "year": "2024", "sic": "3571"}], ["cik", "year", "sic"])
    _write_csv(crosswalk, [{"cik": "1001", "sic": "3571"}], ["cik", "sic"])

    ai_file = input_dir / "2024" / "20240101_10-K_edgar_data_1001_0001_ai_sentences.txt"
    ai_file.parent.mkdir(parents=True, exist_ok=True)
    ai_file.write_text("Held out sentence overlap\nNew unique sentence\n", encoding="utf-8")

    classified_csv = ai_file.with_name(
        ai_file.name.replace("_ai_sentences.txt", "_classified.csv")
    )
    _write_csv(
        classified_csv,
        [
            {"sentence": "Held out sentence overlap", "label_pred": "Speculative"},
            {"sentence": "New unique sentence", "label_pred": "Actionable"},
        ],
        ["sentence", "label_pred"],
    )

    args = argparse.Namespace(
        target_total=10,
        held_out=str(held_out),
        base_labeled=str(base_labeled),
        input_dir=str(input_dir),
        controls=str(controls),
        crosswalk=str(crosswalk),
        output_dir=str(output_dir),
        report_dir=str(report_dir),
        seed=123,
        min_tokens=1,
        min_class_target=1,
    )
    run_build(args)

    manual = pd.read_csv(output_dir / "labeling_sheet_for_manual.csv")
    norms = set(manual["sentence_norm"].tolist())
    assert normalize_sentence("Held out sentence overlap") not in norms
    assert normalize_sentence("New unique sentence") in norms


def test_exact_dedupe_keeps_single_row(tmp_path):
    held_out = tmp_path / "held_out.csv"
    _write_csv(held_out, [], ["sentence", "label"])

    base = tmp_path / "base.csv"
    new = tmp_path / "new.csv"
    out = tmp_path / "preqa.csv"
    uncertain = tmp_path / "uncertain.csv"
    conflicts = tmp_path / "conflicts.csv"
    report = tmp_path / "dedupe_report.json"

    row = _base_row("We deployed AI in finance workflows", label="Actionable")
    _write_csv(base, [row], OUTPUT_COLUMNS)
    _write_csv(new, [row], OUTPUT_COLUMNS)

    run_dedupe(
        argparse.Namespace(
            base=str(base),
            new=str(new),
            held_out=str(held_out),
            near_threshold=0.95,
            output=str(out),
            uncertain_output=str(uncertain),
            conflicts_output=str(conflicts),
            report=str(report),
        )
    )
    df = pd.read_csv(out)
    assert len(df) == 1


def test_near_dupe_same_label_dedupes(tmp_path):
    held_out = tmp_path / "held_out.csv"
    _write_csv(held_out, [], ["sentence", "label"])

    base = tmp_path / "base.csv"
    new = tmp_path / "new.csv"
    out = tmp_path / "preqa.csv"
    uncertain = tmp_path / "uncertain.csv"
    conflicts = tmp_path / "conflicts.csv"
    report = tmp_path / "dedupe_report.json"

    row_a = _base_row(
        "We deployed AI system for billing operations", label="Actionable", sentence_index=1
    )
    row_b = _base_row(
        "We deployed AI systems for billing operations", label="Actionable", sentence_index=2
    )
    _write_csv(base, [row_a], OUTPUT_COLUMNS)
    _write_csv(new, [row_b], OUTPUT_COLUMNS)

    run_dedupe(
        argparse.Namespace(
            base=str(base),
            new=str(new),
            held_out=str(held_out),
            near_threshold=0.95,
            output=str(out),
            uncertain_output=str(uncertain),
            conflicts_output=str(conflicts),
            report=str(report),
        )
    )

    df = pd.read_csv(out)
    conflicts_df = pd.read_csv(conflicts)
    assert len(df) == 1
    assert conflicts_df.empty


def test_near_dupe_conflict_routes_to_conflicts_file(tmp_path):
    held_out = tmp_path / "held_out.csv"
    _write_csv(held_out, [], ["sentence", "label"])

    base = tmp_path / "base.csv"
    new = tmp_path / "new.csv"
    out = tmp_path / "preqa.csv"
    uncertain = tmp_path / "uncertain.csv"
    conflicts = tmp_path / "conflicts.csv"
    report = tmp_path / "dedupe_report.json"

    row_a = _base_row(
        "We deployed AI system for billing operations", label="Actionable", sentence_index=1
    )
    row_b = _base_row(
        "We deployed AI systems for billing operations", label="Speculative", sentence_index=2
    )
    _write_csv(base, [row_a], OUTPUT_COLUMNS)
    _write_csv(new, [row_b], OUTPUT_COLUMNS)

    run_dedupe(
        argparse.Namespace(
            base=str(base),
            new=str(new),
            held_out=str(held_out),
            near_threshold=0.95,
            output=str(out),
            uncertain_output=str(uncertain),
            conflicts_output=str(conflicts),
            report=str(report),
        )
    )

    df = pd.read_csv(out)
    conflicts_df = pd.read_csv(conflicts)
    assert len(df) == 0
    assert len(conflicts_df) == 1


def test_uncertain_rows_are_split_from_final_dataset(tmp_path):
    held_out = tmp_path / "held_out.csv"
    _write_csv(held_out, [], ["sentence", "label"])

    base = tmp_path / "base.csv"
    new = tmp_path / "new.csv"
    out = tmp_path / "preqa.csv"
    uncertain = tmp_path / "uncertain.csv"
    conflicts = tmp_path / "conflicts.csv"
    report = tmp_path / "dedupe_report.json"

    sure = _base_row(
        "Our AI recommendation engine runs in production", label="Actionable", sentence_index=1
    )
    unsure = _base_row("We might explore AI options", label="", sentence_index=2)
    unsure["is_uncertain"] = 1
    unsure["uncertainty_note"] = "borderline"
    _write_csv(base, [sure], OUTPUT_COLUMNS)
    _write_csv(new, [unsure], OUTPUT_COLUMNS)

    run_dedupe(
        argparse.Namespace(
            base=str(base),
            new=str(new),
            held_out=str(held_out),
            near_threshold=0.95,
            output=str(out),
            uncertain_output=str(uncertain),
            conflicts_output=str(conflicts),
            report=str(report),
        )
    )

    final_df = pd.read_csv(out)
    uncertain_df = pd.read_csv(uncertain)
    assert len(final_df) == 1
    assert len(uncertain_df) == 1


def test_qa_fails_on_missing_label_and_empty_sentence(tmp_path):
    preqa = tmp_path / "preqa.csv"
    held_out = tmp_path / "held_out.csv"
    out = tmp_path / "final.csv"
    report = tmp_path / "qa_report.json"
    leakage = tmp_path / "leakage.csv"
    metadata = tmp_path / "dataset_metadata.json"

    row = _base_row("", label="", sentence_index=1)
    row["sentence_norm"] = ""
    row["token_count"] = 0
    _write_csv(preqa, [row], OUTPUT_COLUMNS)
    _write_csv(held_out, [], ["sentence", "label"])

    result = run_qa(
        argparse.Namespace(
            input=str(preqa),
            held_out=str(held_out),
            min_tokens=6,
            min_class_count=1,
            target_size=1,
            allow_target_size_mismatch=False,
            near_threshold=0.95,
            output=str(out),
            report=str(report),
            leakage_report=str(leakage),
            metadata_output=str(metadata),
            rubric_path="docs/labeling_protocol.md",
            sampling_summary="missing.json",
            dedupe_report="missing.json",
        )
    )
    assert result["summary"]["status"] == "fail"
    violations = result["summary"]["violations"]
    assert any(v.startswith("empty_sentence_count=") for v in violations)
    assert any(v.startswith("missing_label_count=") for v in violations)
    assert not out.exists()


def test_qa_fails_when_class_balance_below_minimum(tmp_path):
    preqa = tmp_path / "preqa.csv"
    held_out = tmp_path / "held_out.csv"
    out = tmp_path / "final.csv"
    report = tmp_path / "qa_report.json"
    leakage = tmp_path / "leakage.csv"
    metadata = tmp_path / "dataset_metadata.json"

    rows = []
    for i in range(120):
        rows.append(
            _base_row(
                f"Actionable sentence {i} with enough tokens for qa checks",
                "Actionable",
                sentence_index=i + 1,
            )
        )
    _write_csv(preqa, rows, OUTPUT_COLUMNS)
    _write_csv(held_out, [], ["sentence", "label"])

    result = run_qa(
        argparse.Namespace(
            input=str(preqa),
            held_out=str(held_out),
            min_tokens=6,
            min_class_count=60,
            target_size=120,
            allow_target_size_mismatch=False,
            near_threshold=0.95,
            output=str(out),
            report=str(report),
            leakage_report=str(leakage),
            metadata_output=str(metadata),
            rubric_path="docs/labeling_protocol.md",
            sampling_summary="missing.json",
            dedupe_report="missing.json",
        )
    )
    assert result["summary"]["status"] == "fail"
    assert any("class_count_below_min:Speculative" in v for v in result["summary"]["violations"])


def test_qa_passes_end_to_end_toy_dataset_and_writes_metadata(tmp_path):
    preqa = tmp_path / "preqa.csv"
    held_out = tmp_path / "held_out.csv"
    out = tmp_path / "final.csv"
    report = tmp_path / "qa_report.json"
    leakage = tmp_path / "leakage.csv"
    metadata = tmp_path / "dataset_metadata.json"
    sampling_summary = tmp_path / "sampling_summary.json"
    dedupe_report = tmp_path / "dedupe_report.json"

    rows = []
    labels = (["Actionable"] * 140) + (["Speculative"] * 130) + (["Irrelevant"] * 130)
    for idx, label in enumerate(labels, start=1):
        sentence = f"{label} training sentence {idx} with enough distinct words for checks"
        rows.append(_base_row(sentence, label=label, sentence_index=idx, source_file=f"src_{idx}"))
    _write_csv(preqa, rows, OUTPUT_COLUMNS)
    _write_csv(
        held_out,
        [{"sentence": "held out sentence x", "label": "Irrelevant"}],
        ["sentence", "label"],
    )
    sampling_summary.write_text(json.dumps({"parameters": {"seed": 20260227}}), encoding="utf-8")
    dedupe_report.write_text(json.dumps({"stats": {"rows_combined": 410}}), encoding="utf-8")

    result = run_qa(
        argparse.Namespace(
            input=str(preqa),
            held_out=str(held_out),
            min_tokens=6,
                min_class_count=60,
                target_size=400,
                allow_target_size_mismatch=False,
                near_threshold=1.0,
                output=str(out),
            report=str(report),
            leakage_report=str(leakage),
            metadata_output=str(metadata),
            rubric_path="docs/labeling_protocol.md",
            sampling_summary=str(sampling_summary),
            dedupe_report=str(dedupe_report),
        )
    )

    assert result["summary"]["status"] == "pass"
    final_df = pd.read_csv(out)
    assert len(final_df) == 400

    metadata_payload = json.loads(metadata.read_text(encoding="utf-8"))
    assert metadata_payload["rubric_path"] == "docs/labeling_protocol.md"
    assert metadata_payload["final_dataset"]["rows"] == 400
