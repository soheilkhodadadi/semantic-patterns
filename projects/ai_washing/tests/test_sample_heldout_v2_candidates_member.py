from __future__ import annotations

import pandas as pd

from ai_washing_member.labeling.sample_heldout_v2_candidates import (
    LABELS,
    TARGET_PER_LABEL,
    predict_candidate_labels,
    select_candidate_review_rows,
)


def test_predict_candidate_labels_supports_heuristic_mode() -> None:
    predicted = predict_candidate_labels(
        [
            "We deployed AI systems into production.",
            "We plan to focus on AI capabilities next year.",
            "Our AI infrastructure and laws and regulations discussion continues.",
        ],
        prelabeler="heuristic",
    )

    assert predicted == ["Actionable", "Speculative", "Irrelevant"]


def test_select_candidate_review_rows_builds_balanced_pack() -> None:
    records: list[dict[str, object]] = []
    for label_idx, label in enumerate(LABELS):
        for year in (2021, 2024):
            for idx in range(TARGET_PER_LABEL):
                records.append(
                    {
                        "sentence_id": f"{label}-{year}-{idx}",
                        "sentence": f"{label} sentence {year} {idx}",
                        "source_cik": f"{year}{label_idx:02d}{idx:04d}",
                        "source_year": year,
                        "source_form": "10-K",
                        "source_file": f"{year}_{label}_{idx}.txt",
                        "sentence_index": idx,
                        "candidate_label": label,
                    }
                )
    eligible = pd.DataFrame.from_records(records)

    selected = select_candidate_review_rows(eligible)

    assert len(selected) == 180
    assert selected["candidate_label"].value_counts().to_dict() == {
        label: TARGET_PER_LABEL for label in LABELS
    }
