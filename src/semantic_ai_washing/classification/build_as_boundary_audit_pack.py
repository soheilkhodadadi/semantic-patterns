"""Build a compact A/S-focused audit pack from held-out and IRR artifacts."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

import pandas as pd


def _load_scores_dict(value: object) -> dict[str, float]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return {}
    text = str(value).strip()
    if not text:
        return {}
    try:
        parsed = ast.literal_eval(text)
    except (SyntaxError, ValueError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def build_as_boundary_audit_pack(
    *,
    irr_rows_path: str | Path,
    heldout_details_path: str | Path,
    output_csv: str | Path,
    output_json: str | Path | None = None,
) -> dict[str, object]:
    irr = pd.read_csv(irr_rows_path)
    irr_as = irr.loc[irr["transition"].isin(["A->S", "S->A"])].copy()
    irr_as["source"] = "irr"
    irr_as["case_kind"] = "human_human_as_disagreement"
    irr_as["label_reference"] = irr_as["resolved_label"]
    irr_as["label_other"] = irr_as["rater2_label"]
    irr_as["priority"] = "highest"
    irr_as["fine_margin"] = pd.NA
    irr_as["notes"] = (
        "Human-human disagreement. Use for rubric clarity, not for model scoring."
    )
    irr_as = irr_as[
        [
            "source",
            "case_kind",
            "priority",
            "sentence",
            "source_cik",
            "source_year",
            "ff12_code",
            "ff12_name",
            "label_reference",
            "label_other",
            "resolved_label",
            "transition",
            "fine_margin",
            "notes",
        ]
    ]

    heldout = pd.read_csv(heldout_details_path)
    heldout = heldout.loc[
        heldout["true_label"].isin(["Actionable", "Speculative"])
        & heldout["predicted_label"].isin(["Actionable", "Speculative"])
        & (heldout["true_label"] != heldout["predicted_label"])
    ].copy()
    heldout["scores_dict"] = heldout["scores"].map(_load_scores_dict)
    heldout["fine_margin"] = heldout["scores_dict"].map(lambda value: value.get("fine_margin"))
    heldout["actionable_score"] = heldout["scores_dict"].map(lambda value: value.get("Actionable"))
    heldout["speculative_score"] = heldout["scores_dict"].map(lambda value: value.get("Speculative"))
    heldout["irrelevant_score"] = heldout["scores_dict"].map(lambda value: value.get("Irrelevant"))
    heldout["source"] = "heldout"
    heldout["case_kind"] = "heldout_model_as_error"
    heldout["priority"] = heldout["fine_margin"].map(
        lambda value: "high" if pd.notna(value) and float(value) <= 0.10 else "medium"
    )
    heldout["label_reference"] = heldout["true_label"]
    heldout["label_other"] = heldout["predicted_label"]
    heldout["resolved_label"] = pd.NA
    heldout["transition"] = heldout["true_label"].str[0] + "->" + heldout["predicted_label"].str[0]
    heldout["notes"] = (
        "Held-out model miss. Review wording and whether A/S split is rubric-stable."
    )
    heldout["source_cik"] = pd.NA
    heldout["source_year"] = pd.NA
    heldout["ff12_code"] = pd.NA
    heldout["ff12_name"] = pd.NA
    heldout = heldout[
        [
            "source",
            "case_kind",
            "priority",
            "sentence",
            "source_cik",
            "source_year",
            "ff12_code",
            "ff12_name",
            "label_reference",
            "label_other",
            "resolved_label",
            "transition",
            "fine_margin",
            "actionable_score",
            "speculative_score",
            "irrelevant_score",
            "notes",
        ]
    ]

    irr_as["actionable_score"] = pd.NA
    irr_as["speculative_score"] = pd.NA
    irr_as["irrelevant_score"] = pd.NA

    combined = pd.DataFrame(irr_as.to_dict("records") + heldout.to_dict("records"))
    combined["priority_order"] = combined["priority"].map(
        {"highest": 0, "high": 1, "medium": 2}
    ).fillna(9)
    combined = combined.sort_values(
        ["priority_order", "source", "fine_margin", "transition"],
        na_position="last",
    ).drop(columns=["priority_order"])

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(output_path, index=False)

    summary = {
        "status": "passed",
        "irr_rows_total": int(len(irr)),
        "irr_as_rows": int(len(irr_as)),
        "heldout_rows_total": int(len(heldout)),
        "heldout_high_priority_rows": int((heldout["priority"] == "high").sum()),
        "audit_pack_rows": int(len(combined)),
        "output_csv": str(output_path),
    }
    if output_json is not None:
        json_path = Path(output_json)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        summary["output_json"] = str(json_path)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--irr-rows",
        default="reports/labels/irr_disagreement_rows_v1.csv",
    )
    parser.add_argument(
        "--heldout-details",
        default="reports/evaluation/legacy_two_stage_eval_default/evaluation_details.csv",
    )
    parser.add_argument(
        "--output-csv",
        default="reports/final/ai_washing_classifier_as_boundary_audit_pack_v1.csv",
    )
    parser.add_argument(
        "--output-json",
        default="reports/final/ai_washing_classifier_as_boundary_audit_pack_v1.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = build_as_boundary_audit_pack(
        irr_rows_path=args.irr_rows,
        heldout_details_path=args.heldout_details,
        output_csv=args.output_csv,
        output_json=args.output_json,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
