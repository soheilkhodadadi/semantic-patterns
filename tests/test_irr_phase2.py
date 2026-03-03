from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from semantic_ai_washing.labeling.adjudicate_irr_labels import run_adjudication
from semantic_ai_washing.labeling.compute_irr_metrics import run_metrics
from semantic_ai_washing.labeling.prepare_irr_subset import run_prepare


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)


def test_prepare_irr_subset_stratified_and_text_blinded(tmp_path):
    input_path = tmp_path / "expanded.csv"
    output_dir = tmp_path / "irr"
    report_dir = tmp_path / "reports"

    rows = []
    labels = ["Actionable", "Speculative", "Irrelevant"]
    years = ["2023", "2024"]
    ff12 = ["10", "20", "30"]
    idx = 0
    for label in labels:
        for year in years:
            for bucket in ff12:
                for rep in range(3):
                    idx += 1
                    rows.append(
                        {
                            "sample_id": f"s{idx}",
                            "sentence_id": f"t{idx}",
                            "sentence": f"sentence {label} {year} {bucket} {rep}",
                            "label": label,
                            "source_year": year,
                            "source_form": "10-K",
                            "source_cik": "1001",
                            "source_file": f"f{idx}.txt",
                            "sentence_index": idx,
                            "ff12_code": bucket,
                            "ff12_name": "Bucket",
                        }
                    )
    _write_csv(input_path, rows)

    args = argparse.Namespace(
        input=str(input_path),
        output_dir=str(output_dir),
        report_dir=str(report_dir),
        subset_fraction=0.30,
        min_per_class=5,
        seed=20260303,
        blind_mode="text_only",
    )
    report = run_prepare(args)

    master = pd.read_csv(output_dir / "irr_subset_master.csv")
    blinded = pd.read_csv(output_dir / "irr_subset_rater2_blinded.csv")

    assert len(master) == report["summary"]["rows_selected"]
    counts = master["rater1_label"].value_counts().to_dict()
    assert counts["Actionable"] >= 5
    assert counts["Speculative"] >= 5
    assert counts["Irrelevant"] >= 5
    assert list(blinded.columns) == ["irr_item_id", "sentence", "rater2_label", "rater2_note"]


def test_compute_irr_metrics_pending_modes(tmp_path):
    master_path = tmp_path / "master.csv"
    _write_csv(
        master_path,
        [
            {"irr_item_id": "i1", "rater1_label": "Actionable"},
            {"irr_item_id": "i2", "rater1_label": "Speculative"},
        ],
    )

    args_infra = argparse.Namespace(
        master=str(master_path),
        rater2=str(tmp_path / "missing.csv"),
        output_report=str(tmp_path / "report_infra.json"),
        output_confusion=str(tmp_path / "conf_infra.csv"),
        output_transitions=str(tmp_path / "trans_infra.csv"),
        output_status=str(tmp_path / "status_infra.json"),
        min_kappa=0.60,
        gate_mode="infrastructure",
    )
    _, status_infra, code_infra = run_metrics(args_infra)
    assert code_infra == 0
    assert status_infra["gate_result"] == "deferred"

    args_strict = argparse.Namespace(
        master=str(master_path),
        rater2=str(tmp_path / "missing.csv"),
        output_report=str(tmp_path / "report_strict.json"),
        output_confusion=str(tmp_path / "conf_strict.csv"),
        output_transitions=str(tmp_path / "trans_strict.csv"),
        output_status=str(tmp_path / "status_strict.json"),
        min_kappa=0.60,
        gate_mode="strict",
    )
    _, status_strict, code_strict = run_metrics(args_strict)
    assert code_strict == 1
    assert status_strict["gate_result"] == "deferred"


def test_compute_irr_metrics_happy_path_and_transitions(tmp_path):
    master_path = tmp_path / "master.csv"
    r2_path = tmp_path / "r2.csv"
    _write_csv(
        master_path,
        [
            {"irr_item_id": "i1", "rater1_label": "Actionable"},
            {"irr_item_id": "i2", "rater1_label": "Speculative"},
            {"irr_item_id": "i3", "rater1_label": "Irrelevant"},
            {"irr_item_id": "i4", "rater1_label": "Actionable"},
        ],
    )
    _write_csv(
        r2_path,
        [
            {"irr_item_id": "i1", "rater2_label": "Actionable"},
            {"irr_item_id": "i2", "rater2_label": "Actionable"},
            {"irr_item_id": "i3", "rater2_label": "Irrelevant"},
            {"irr_item_id": "i4", "rater2_label": "Speculative"},
        ],
    )

    args = argparse.Namespace(
        master=str(master_path),
        rater2=str(r2_path),
        output_report=str(tmp_path / "report.json"),
        output_confusion=str(tmp_path / "conf.csv"),
        output_transitions=str(tmp_path / "trans.csv"),
        output_status=str(tmp_path / "status.json"),
        min_kappa=0.10,
        gate_mode="strict",
    )
    report, status, code = run_metrics(args)
    assert code == 0
    assert status["gate_result"] == "pass"
    assert abs(float(report["summary"]["kappa"]) - 0.2) < 1e-6

    transitions = pd.read_csv(tmp_path / "trans.csv").set_index("transition")["count"].to_dict()
    assert transitions["A->S"] == 1
    assert transitions["S->A"] == 1


def test_adjudication_scaffold_pending(tmp_path):
    master_path = tmp_path / "master.csv"
    source_path = tmp_path / "source.csv"
    _write_csv(
        master_path,
        [
            {
                "irr_item_id": "i1",
                "sample_id": "s1",
                "sentence_id": "t1",
                "sentence": "sentence one",
                "source_year": "2024",
                "ff12_code": "10",
                "rater1_label": "Actionable",
            }
        ],
    )
    _write_csv(
        source_path, [{"sample_id": "s1", "label": "Actionable", "sentence": "sentence one"}]
    )

    args = argparse.Namespace(
        master=str(master_path),
        rater2=str(tmp_path / "missing.csv"),
        output_disagreements=str(tmp_path / "disagreements.csv"),
        output_adjudication=str(tmp_path / "adjudication.csv"),
        source_dataset=str(source_path),
        final_output=str(tmp_path / "final.csv"),
        output_status=str(tmp_path / "status.json"),
        allow_pending=True,
    )
    status, code = run_adjudication(args)
    assert code == 0
    assert status["summary"]["status"] == "pending_rater2"
    assert (tmp_path / "adjudication.csv").exists()
    assert not status["summary"]["final_output_written"]


def test_adjudication_merge_writes_final_dataset(tmp_path):
    master_path = tmp_path / "master.csv"
    r2_path = tmp_path / "r2.csv"
    source_path = tmp_path / "source.csv"
    out_adj = tmp_path / "adjudication.csv"
    out_final = tmp_path / "final.csv"

    _write_csv(
        master_path,
        [
            {
                "irr_item_id": "i1",
                "sample_id": "s1",
                "sentence_id": "t1",
                "sentence": "sentence one",
                "source_year": "2024",
                "ff12_code": "10",
                "rater1_label": "Actionable",
            },
            {
                "irr_item_id": "i2",
                "sample_id": "s2",
                "sentence_id": "t2",
                "sentence": "sentence two",
                "source_year": "2024",
                "ff12_code": "20",
                "rater1_label": "Speculative",
            },
        ],
    )
    _write_csv(
        r2_path,
        [
            {"irr_item_id": "i1", "rater2_label": "Actionable"},
            {"irr_item_id": "i2", "rater2_label": "Irrelevant"},
        ],
    )
    _write_csv(
        source_path,
        [
            {"sample_id": "s1", "label": "Actionable", "sentence": "sentence one"},
            {"sample_id": "s2", "label": "Speculative", "sentence": "sentence two"},
        ],
    )

    args = argparse.Namespace(
        master=str(master_path),
        rater2=str(r2_path),
        output_disagreements=str(tmp_path / "disagreements.csv"),
        output_adjudication=str(out_adj),
        source_dataset=str(source_path),
        final_output=str(out_final),
        output_status=str(tmp_path / "status.json"),
        allow_pending=True,
    )
    status_first, code_first = run_adjudication(args)
    assert code_first == 0
    assert status_first["summary"]["status"] == "pending_adjudication"

    adj = pd.read_csv(out_adj)
    adj["final_label"] = adj["final_label"].fillna("").astype(str)
    adj.loc[adj["irr_item_id"] == "i2", "final_label"] = "Irrelevant"
    adj.to_csv(out_adj, index=False)

    status_second, code_second = run_adjudication(args)
    assert code_second == 0
    assert status_second["summary"]["status"] == "finalized"
    assert status_second["summary"]["final_output_written"]

    final_df = pd.read_csv(out_final)
    labels = final_df.set_index("sample_id")["label"].to_dict()
    assert labels["s1"] == "Actionable"
    assert labels["s2"] == "Irrelevant"
