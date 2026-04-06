from __future__ import annotations

import pandas as pd

from ai_washing_member.data.reextract_tranche_slice import reextract_tranche_slice


def _write_text(path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_member_reextract_tranche_slice_rebuilds_rows_and_marks_unmatched(tmp_path):
    source_root = tmp_path / "sec_root"
    filing_path = source_root / "2024" / "QTR1" / "sample_10k.txt"
    _write_text(
        filing_path,
        (
            "Table of Contents\n"
            "Item 1. Business\n"
            "Business Overview Artificial intelligence supports workflows today.\n"
            "Item 1A. Risk Factors\n"
            "Artificial intelligence could expose us to cyber risks.\n"
        ),
    )

    keywords_path = tmp_path / "keywords.txt"
    _write_text(keywords_path, "artificial intelligence\nmachine learning\n")

    slice_path = tmp_path / "slice40.csv"
    pd.DataFrame(
        [
            {
                "source_file": "2024/QTR1/sample_10k.txt",
                "sentence_id": "s1",
                "sentence_index": 1,
                "sentence": "Business Overview Artificial intelligence supports workflows today.",
                "assistive_label": "Actionable",
                "label": "",
                "is_uncertain": "",
                "uncertainty_note": "",
            },
            {
                "source_file": "2024/QTR1/sample_10k.txt",
                "sentence_id": "s2",
                "sentence_index": 2,
                "sentence": "N AI/ML - Artificial Intelligence/Machine Learning.",
                "assistive_label": "Speculative",
                "label": "",
                "is_uncertain": "",
                "uncertainty_note": "",
            },
        ]
    ).to_csv(slice_path, index=False)

    report = reextract_tranche_slice(
        input_csv=str(slice_path),
        output_csv=str(tmp_path / "reextracted.csv"),
        report_path=str(tmp_path / "report.json"),
        source_root=str(source_root),
        keywords_path=str(keywords_path),
    )

    rebuilt = pd.read_csv(tmp_path / "reextracted.csv", keep_default_na=False)
    assert rebuilt.loc[0, "sentence"] == "Artificial intelligence supports workflows today."
    assert rebuilt.loc[0, "match_status"] == "exact"
    assert rebuilt.loc[1, "match_status"] == "unmatched"
    assert report["counts"]["slice_rows"] == 2
    assert report["counts"]["unmatched_rows"] == 1
