from __future__ import annotations

import pandas as pd

from ai_washing_member.labeling.initialize_review_sheet import initialize_review_sheet


def test_initialize_review_sheet_creates_blank_columns_and_slice(tmp_path) -> None:
    input_path = tmp_path / "prelabels.csv"
    output_path = tmp_path / "review.csv"
    slice_path = tmp_path / "slice.csv"
    pd.DataFrame(
        [
            {"sentence_id": "s1", "sentence": "Sentence one", "assistive_label": "Actionable"},
            {"sentence_id": "s2", "sentence": "Sentence two", "assistive_label": "Speculative"},
        ]
    ).to_csv(input_path, index=False)

    total_rows, slice_rows = initialize_review_sheet(
        input_csv=str(input_path),
        output_csv=str(output_path),
        slice_output_csv=str(slice_path),
        slice_size=1,
    )

    review = pd.read_csv(output_path)
    assert total_rows == 2
    assert slice_rows == 1
    assert review["label"].fillna("").tolist() == ["", ""]
    assert review["is_uncertain"].fillna("").tolist() == ["", ""]
    assert review["uncertainty_note"].fillna("").tolist() == ["", ""]


def test_initialize_review_sheet_carries_forward_existing_labels(tmp_path) -> None:
    input_path = tmp_path / "prelabels.csv"
    existing_path = tmp_path / "existing.csv"
    output_path = tmp_path / "review.csv"
    pd.DataFrame(
        [
            {"sentence_id": "s1", "sentence": "Sentence one"},
            {"sentence_id": "s2", "sentence": "Sentence two"},
        ]
    ).to_csv(input_path, index=False)
    pd.DataFrame(
        [
            {
                "sentence_id": "s2",
                "label": "Actionable",
                "is_uncertain": "false",
                "uncertainty_note": "kept",
            }
        ]
    ).to_csv(existing_path, index=False)

    total_rows, slice_rows = initialize_review_sheet(
        input_csv=str(input_path),
        output_csv=str(output_path),
        existing_review_csv=str(existing_path),
    )

    review = pd.read_csv(output_path)
    assert total_rows == 2
    assert slice_rows == 0
    carried = review.loc[review["sentence_id"] == "s2"].iloc[0]
    assert carried["label"] == "Actionable"
    assert str(carried["is_uncertain"]).lower() == "false"
    assert carried["uncertainty_note"] == "kept"
