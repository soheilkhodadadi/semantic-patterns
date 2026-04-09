from __future__ import annotations

import json

import pandas as pd

from ai_washing_member.labeling.prepare_heldout_v4_from_adjudication import build_heldout_v4


def test_build_heldout_v4_from_adjudication(tmp_path) -> None:
    master = tmp_path / "master.csv"
    rater2 = tmp_path / "rater2.xlsx"
    adjudication = tmp_path / "adjudication.parquet"
    benchmark_csv = tmp_path / "held_out_v4.csv"
    input_csv = tmp_path / "held_out_v4_input.csv"
    report_json = tmp_path / "build.json"

    pd.DataFrame(
        [
            {
                "irr_item_id": "irr1",
                "sample_id": "samp1",
                "batch_row_id": "batch1",
                "sentence_id": "sent1",
                "sentence": "We use AI in production.",
                "source_cik": "1000",
                "source_year": "2024",
                "source_form": "10-K",
                "source_file": "f1.txt",
                "sentence_index": "1",
                "ff12_code": "12",
                "ff12_name": "Other",
                "rater1_label": "Actionable",
            },
            {
                "irr_item_id": "irr2",
                "sample_id": "samp2",
                "batch_row_id": "batch2",
                "sentence_id": "sent2",
                "sentence": "We may invest in AI.",
                "source_cik": "1001",
                "source_year": "2024",
                "source_form": "10-K",
                "source_file": "f2.txt",
                "sentence_index": "2",
                "ff12_code": "12",
                "ff12_name": "Other",
                "rater1_label": "Speculative",
            },
        ]
    ).to_csv(master, index=False)
    pd.DataFrame(
        [
            {"irr_item_id": "irr1", "sentence": "We use AI in production.", "rater2_label": "Actionable", "rater2_note": "Current use"},
            {"irr_item_id": "irr2", "sentence": "We may invest in AI.", "rater2_label": "Irrelevant", "rater2_note": "Risk context"},
        ]
    ).to_excel(rater2, index=False)
    pd.DataFrame(
        [
            {
                "irr_item_id": "irr1",
                "resolved_label": "Actionable",
                "resolution_source": "agreement",
                "disagreement_pair": "",
                "transition": "",
                "adjudication_note": "",
            },
            {
                "irr_item_id": "irr2",
                "resolved_label": "Speculative",
                "resolution_source": "third_adjudicator",
                "disagreement_pair": "I_vs_S",
                "transition": "S->I",
                "adjudication_note": "Future-facing intent without current deployment.",
            },
        ]
    ).to_parquet(adjudication, index=False)

    report = build_heldout_v4(
        master_path=str(master),
        rater2_path=str(rater2),
        adjudication_path=str(adjudication),
        benchmark_csv=str(benchmark_csv),
        input_csv=str(input_csv),
        report_path=str(report_json),
    )

    benchmark = pd.read_csv(benchmark_csv)
    input_frame = pd.read_csv(input_csv)

    assert report["summary"]["status"] == "built"
    assert benchmark["label"].tolist() == ["Actionable", "Speculative"]
    assert benchmark["review_note"].tolist() == ["Current use", "Future-facing intent without current deployment."]
    assert input_frame["label"].fillna("").astype(str).tolist() == ["", ""]
    assert input_frame["benchmark_label"].tolist() == ["Actionable", "Speculative"]
    assert "assistive_label" in input_frame.columns
    assert json.loads(report_json.read_text(encoding="utf-8"))["summary"]["rows_total"] == 2
