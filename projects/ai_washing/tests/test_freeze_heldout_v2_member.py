from __future__ import annotations

import argparse

import pandas as pd

from ai_washing_member.labeling import freeze_heldout_v2


def test_run_freeze_balanced_review_sheet(tmp_path) -> None:
    reviewed = tmp_path / "reviewed.csv"
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
    pd.DataFrame.from_records(records).to_csv(reviewed, index=False)

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
