from __future__ import annotations

import pandas as pd

from ai_washing_member.labeling.merge_labeling_batches import merge_labeling_batches


def test_merge_labeling_batches_member_keeps_nonempty_labels(tmp_path) -> None:
    tranche_path = tmp_path / "tranche.csv"
    held_out_path = tmp_path / "held_out.csv"
    output_parquet = tmp_path / "labels_master.parquet"
    output_review_csv = tmp_path / "labels_master_review.csv"
    report_path = tmp_path / "summary.json"

    pd.DataFrame(
        [
            {
                "batch_id": "labeling_batch_v1",
                "sentence_id": "s1",
                "sentence_text_id": "t1",
                "sentence": "We use artificial intelligence in operations.",
                "sentence_norm": "we use artificial intelligence in operations",
                "label": "Actionable",
                "is_uncertain": "",
                "uncertainty_note": "",
                "source_file": "2024/QTR1/f1.txt",
                "source_year": 2024,
                "source_quarter": 1,
                "source_form": "10-K",
                "source_cik": "1001",
                "sentence_index": 1,
                "assistive_label": "Actionable",
            }
        ]
    ).to_csv(tranche_path, index=False)
    pd.DataFrame([{"sentence": "unrelated held out sentence"}]).to_csv(held_out_path, index=False)

    summary, exit_code = merge_labeling_batches(
        input_csvs=[str(tranche_path)],
        held_out_path=str(held_out_path),
        output_parquet_path=str(output_parquet),
        output_review_csv_path=str(output_review_csv),
        report_path=str(report_path),
    )

    assert exit_code == 0
    assert output_parquet.exists()
    assert output_review_csv.exists()
    assert summary["summary"]["total_canonical_labeled_rows"] == 1
