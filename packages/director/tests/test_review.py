from __future__ import annotations

import json

from semantic_director.review import load_approved_review_summaries


def test_load_approved_review_summaries_filters_to_approved_reviews(tmp_path) -> None:
    reviews_dir = tmp_path / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)

    (reviews_dir / "iteration_1_review.json").write_text(
        json.dumps(
            {
                "review_id": "review-1",
                "review_type": "iteration",
                "iteration_id": "1",
                "phase_id": "",
                "status": "completed",
                "findings": [{"finding_id": "f1"}],
            }
        ),
        encoding="utf-8",
    )
    (reviews_dir / "iteration_1_approval.json").write_text(
        json.dumps(
            {
                "review_id": "review-1",
                "decision": "approved",
                "accepted_change_ids": ["chg-1"],
                "deferred_change_ids": [],
                "authorized_track": "continue",
            }
        ),
        encoding="utf-8",
    )
    (reviews_dir / "iteration_2_review.json").write_text(
        json.dumps(
            {
                "review_id": "review-2",
                "review_type": "iteration",
                "iteration_id": "2",
                "phase_id": "",
                "status": "completed",
                "findings": [{"finding_id": "f2"}],
            }
        ),
        encoding="utf-8",
    )
    (reviews_dir / "iteration_2_approval.json").write_text(
        json.dumps(
            {
                "review_id": "review-2",
                "decision": "deferred",
                "accepted_change_ids": [],
                "deferred_change_ids": ["chg-2"],
                "authorized_track": "pause",
            }
        ),
        encoding="utf-8",
    )

    summaries = load_approved_review_summaries(reviews_dir)

    assert summaries == [
        {
            "review_id": "review-1",
            "review_type": "iteration",
            "iteration_id": "1",
            "phase_id": "",
            "status": "completed",
            "findings_count": 1,
            "accepted_change_ids": ["chg-1"],
            "deferred_change_ids": [],
            "authorized_track": "continue",
            "next_iteration": {},
            "stakeholder_alignment_summary": {},
            "methodology_alignment_summary": {},
            "unmet_stakeholder_requirements": [],
            "unmet_methodology_requirements": [],
            "rubric_calibration_status": "",
            "rubric_freeze_status": "",
            "predictive_validity_gate_status": "",
            "publication_readiness_blockers": [],
        }
    ]
