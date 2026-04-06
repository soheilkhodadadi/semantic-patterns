from __future__ import annotations

import argparse

import pandas as pd

from ai_washing_member.labeling.adjudicate_irr_labels import run_adjudication


def test_run_adjudication_pending_then_finalized(tmp_path) -> None:
    master_path = tmp_path / "master.csv"
    r2_path = tmp_path / "rater2.xlsx"
    adjudication_input = tmp_path / "irr_adjudication_completed.xlsx"

    pd.DataFrame(
        [
            {
                "irr_item_id": "i1",
                "sample_id": "s1",
                "batch_row_id": "b1",
                "sentence_id": "t1",
                "sentence": "Sentence one uses AI.",
                "source_cik": "1001",
                "source_year": "2024",
                "source_form": "10-K",
                "source_file": "f1.txt",
                "sentence_index": 1,
                "ff12_code": "10",
                "ff12_name": "Tech",
                "rater1_label": "Actionable",
            },
            {
                "irr_item_id": "i2",
                "sample_id": "s2",
                "batch_row_id": "b2",
                "sentence_id": "t2",
                "sentence": "Sentence two may use AI.",
                "source_cik": "1002",
                "source_year": "2024",
                "source_form": "10-K",
                "source_file": "f2.txt",
                "sentence_index": 2,
                "ff12_code": "11",
                "ff12_name": "Shops",
                "rater1_label": "Speculative",
            },
        ]
    ).to_csv(master_path, index=False)

    pd.DataFrame(
        [
            {
                "irr_item_id": "i1",
                "sentence": "Sentence one uses AI.",
                "rater2_label": "Actionable",
            },
            {
                "irr_item_id": "i2",
                "sentence": "Sentence two may use AI.",
                "rater2_label": "Irrelevant",
            },
        ]
    ).to_excel(r2_path, index=False)

    args = argparse.Namespace(
        master=str(master_path),
        rater2=str(r2_path),
        adjudication_input=str(adjudication_input),
        output_sheet_csv=str(tmp_path / "irr_adjudication_sheet.csv"),
        output_sheet_xlsx=str(tmp_path / "irr_adjudication_sheet.xlsx"),
        output_parquet=str(tmp_path / "adjudication.parquet"),
        output_status=str(tmp_path / "adjudication_status.json"),
        allow_pending=True,
    )
    status_pending, code_pending = run_adjudication(args)
    assert code_pending == 0
    assert status_pending["summary"]["status"] == "pending_adjudication"

    sheet = pd.read_csv(tmp_path / "irr_adjudication_sheet.csv")
    sheet["final_label"] = sheet["final_label"].fillna("").astype(str)
    sheet["adjudication_note"] = sheet["adjudication_note"].fillna("").astype(str)
    sheet.loc[sheet["irr_item_id"] == "i2", "final_label"] = "Irrelevant"
    sheet.to_excel(adjudication_input, index=False)

    status_final, code_final = run_adjudication(args)
    assert code_final == 0
    assert status_final["summary"]["status"] == "finalized"
    adjudication = pd.read_parquet(tmp_path / "adjudication.parquet")
    assert adjudication["resolved_label"].tolist() == ["Actionable", "Irrelevant"]
