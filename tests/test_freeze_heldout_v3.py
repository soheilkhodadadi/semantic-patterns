from __future__ import annotations

import json

import pandas as pd

from semantic_ai_washing.labeling.freeze_heldout_v3 import freeze_heldout_v3


def test_freeze_heldout_v3_requires_completed_labels(tmp_path):
    review_csv = tmp_path / "review.csv"
    out_csv = tmp_path / "heldout.csv"
    out_report = tmp_path / "freeze.json"

    pd.DataFrame(
        [
            {"sentence_id": "a", "sentence": "one", "label": "Actionable"},
            {"sentence_id": "b", "sentence": "two", "label": ""},
        ]
    ).to_csv(review_csv, index=False)

    report, exit_code = freeze_heldout_v3(
        reviewed_input=str(review_csv),
        output_csv=str(out_csv),
        output_report=str(out_report),
    )

    assert exit_code == 1
    assert report["summary"]["status"] == "pending_review"
    assert not out_csv.exists()
    assert json.loads(out_report.read_text(encoding="utf-8"))["summary"]["rows_pending_review"] == 1


def test_freeze_heldout_v3_writes_frozen_csv(tmp_path):
    review_csv = tmp_path / "review.csv"
    out_csv = tmp_path / "heldout.csv"
    out_report = tmp_path / "freeze.json"

    pd.DataFrame(
        [
            {"sentence_id": "a", "sentence": "one", "label": "Actionable", "legacy_candidate_label": "Speculative"},
            {"sentence_id": "b", "sentence": "two", "label": "Irrelevant", "legacy_candidate_label": "Irrelevant"},
        ]
    ).to_csv(review_csv, index=False)

    report, exit_code = freeze_heldout_v3(
        reviewed_input=str(review_csv),
        output_csv=str(out_csv),
        output_report=str(out_report),
    )

    frozen = pd.read_csv(out_csv)
    assert exit_code == 0
    assert report["summary"]["status"] == "frozen"
    assert "legacy_candidate_label" not in frozen.columns
    assert frozen["label"].tolist() == ["Actionable", "Irrelevant"]
