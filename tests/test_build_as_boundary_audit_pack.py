from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from semantic_ai_washing.classification.build_as_boundary_audit_pack import (
    build_as_boundary_audit_pack,
)


def test_build_as_boundary_audit_pack_filters_as_cases(tmp_path: Path) -> None:
    irr_path = tmp_path / "irr.csv"
    heldout_path = tmp_path / "heldout.csv"
    output_csv = tmp_path / "audit.csv"
    output_json = tmp_path / "audit.json"

    pd.DataFrame(
        [
            {
                "sentence": "We deploy AI features in production.",
                "source_cik": "0000000001",
                "source_year": 2024,
                "ff12_code": 12,
                "ff12_name": "Other",
                "rater1_label": "Actionable",
                "rater2_label": "Speculative",
                "resolved_label": "Actionable",
                "transition": "A->S",
            },
            {
                "sentence": "We may evaluate AI opportunities in the future.",
                "source_cik": "0000000002",
                "source_year": 2024,
                "ff12_code": 12,
                "ff12_name": "Other",
                "rater1_label": "Actionable",
                "rater2_label": "Irrelevant",
                "resolved_label": "Irrelevant",
                "transition": "A->I",
            },
        ]
    ).to_csv(irr_path, index=False)

    pd.DataFrame(
        [
            {
                "sentence": "We deploy AI features in production.",
                "true_label": "Actionable",
                "predicted_label": "Speculative",
                "match": False,
                "scores": "{'Actionable': 0.6, 'Speculative': 0.7, 'Irrelevant': 0.2, 'fine_margin': 0.1}",
            },
            {
                "sentence": "We may evaluate AI opportunities in the future.",
                "true_label": "Irrelevant",
                "predicted_label": "Actionable",
                "match": False,
                "scores": "{'Actionable': 0.7, 'Speculative': 0.2, 'Irrelevant': 0.1, 'fine_margin': 0.5}",
            },
        ]
    ).to_csv(heldout_path, index=False)

    summary = build_as_boundary_audit_pack(
        irr_rows_path=irr_path,
        heldout_details_path=heldout_path,
        output_csv=output_csv,
        output_json=output_json,
    )

    result = pd.read_csv(output_csv)
    assert summary["irr_as_rows"] == 1
    assert summary["heldout_rows_total"] == 1
    assert summary["audit_pack_rows"] == 2
    assert set(result["source"]) == {"irr", "heldout"}
    assert set(result["transition"]) == {"A->S"}

    payload = json.loads(output_json.read_text(encoding="utf-8"))
    assert payload["audit_pack_rows"] == 2
