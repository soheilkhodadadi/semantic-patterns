from __future__ import annotations

import argparse
import json

import pandas as pd

from ai_washing_member.labeling.build_irr_boundary_benchmark import (
    OUTPUT_COLUMNS,
    run_build,
)


def test_run_build_publishes_boundary_benchmark(tmp_path) -> None:
    adjudication_path = tmp_path / "adjudication.parquet"
    output_csv = tmp_path / "data" / "validation" / "irr_boundary_benchmark_v1.csv"
    output_report = tmp_path / "reports" / "validation" / "irr_boundary_benchmark_v1.json"

    pd.DataFrame(
        [
            {
                "irr_item_id": "irr_1",
                "sentence_id": "sent_1",
                "sentence": "We use AI systems in production today.",
                "resolved_label": "Actionable",
                "source_cik": "1001",
                "source_year": 2024,
                "disagreement_pair": "",
                "resolution_source": "agreement",
            },
            {
                "irr_item_id": "irr_2",
                "sentence_id": "sent_2",
                "sentence": "We may expand AI efforts later this year.",
                "resolved_label": "Speculative",
                "source_cik": "1002",
                "source_year": 2024,
                "disagreement_pair": "Actionable|Speculative",
                "transition": "A->S",
                "resolution_source": "third_adjudicator",
                "rater1_label": "Actionable",
                "rater2_label": "Speculative",
            },
            {
                "irr_item_id": "irr_3",
                "sentence_id": "sent_3",
                "sentence": "This sentence should be excluded from the benchmark.",
                "resolved_label": "Unknown",
                "source_cik": "1003",
                "source_year": 2024,
            },
        ]
    ).to_parquet(adjudication_path, index=False)

    summary = run_build(
        argparse.Namespace(
            adjudication=str(adjudication_path),
            output_csv=str(output_csv),
            output_report=str(output_report),
        )
    )

    benchmark = pd.read_csv(output_csv)
    saved = json.loads(output_report.read_text(encoding="utf-8"))

    assert benchmark.columns.tolist() == OUTPUT_COLUMNS
    assert benchmark["label"].tolist() == ["Actionable", "Speculative"]
    assert benchmark["is_disagreement_case"].tolist() == [False, True]
    assert benchmark["benchmark_role"].tolist() == [
        "boundary_benchmark_v1",
        "boundary_benchmark_v1",
    ]
    assert summary["summary"]["rows_total"] == 2
    assert summary["summary"]["rows_disagreement_case"] == 1
    assert saved["summary"]["label_counts"] == {"Actionable": 1, "Speculative": 1}
