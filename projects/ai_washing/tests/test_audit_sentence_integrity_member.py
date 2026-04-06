from __future__ import annotations

import argparse

import pandas as pd

from ai_washing_member.labeling.audit_sentence_integrity import run_audit


def test_run_audit_writes_pass_report(tmp_path) -> None:
    input_path = tmp_path / "labels_master_review.csv"
    report_path = tmp_path / "reports" / "irr_sentence_quality.json"

    pd.DataFrame(
        [
            {"sentence": "Firm 1 uses AI capability sentence."},
            {"sentence": "Firm 2 deploys AI workflow sentence."},
            {"sentence": "Firm 3 explains AI operations sentence."},
            {"sentence": "Firm 4 describes AI production sentence."},
            {"sentence": "Firm 5 supports AI deployment sentence."},
        ]
    ).to_csv(input_path, index=False)

    report = run_audit(
        argparse.Namespace(
            input_csv=str(input_path),
            output_report=str(report_path),
            threshold=0.15,
        )
    )

    assert report["passed"] is True
    assert report["fragment_rows"] == 0
    assert report_path.exists()
