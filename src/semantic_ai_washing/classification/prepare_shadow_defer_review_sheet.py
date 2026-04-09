"""Prepare a deferred-slice review sheet from local shadow classification outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from semantic_ai_washing.classification.shadow_selective_defer import (
    build_deferred_mask,
    load_classified_rows,
    resolve_policy,
    summarize_deferred_rows,
)


ASSISTIVE_COLUMNS = [
    "assistive_label",
    "assistive_confidence",
    "assistive_rationale",
    "assistive_model",
    "assistive_generated_at",
    "assistive_prompt_hash",
]


def run_prepare(args: argparse.Namespace) -> dict[str, object]:
    years = [int(value) for value in args.years]
    policy = resolve_policy(args.policy)
    frame = load_classified_rows(input_root=args.input_root, years=years, model_id=args.model_id).copy()
    deferred_mask = build_deferred_mask(frame, policy)
    summary = summarize_deferred_rows(frame, deferred_mask)

    deferred = frame.loc[deferred_mask].copy()
    deferred["prelabel_eligible"] = True
    deferred["label"] = ""
    deferred["manual_label"] = ""
    deferred["shadow_policy"] = policy.name
    deferred["shadow_policy_description"] = policy.description
    deferred["shadow_deferred"] = True
    deferred["local_predicted_label"] = deferred["predicted_label"].astype(str)
    if "local_label" not in deferred.columns:
        deferred["local_label"] = deferred["local_predicted_label"]
    for column in ASSISTIVE_COLUMNS:
        if column not in deferred.columns:
            deferred[column] = ""

    preferred = [
        "sentence_id",
        "sentence",
        "source_file",
        "sentence_index",
        "source_section",
        "source_cik",
        "source_year",
        "label",
        "manual_label",
        "prelabel_eligible",
        "shadow_policy",
        "shadow_policy_description",
        "shadow_deferred",
        "local_predicted_label",
        "local_label",
        "predicted_label",
        "local_confidence",
        "conditional_as_margin",
        "binary_logreg_relevance_disagreement",
        *ASSISTIVE_COLUMNS,
    ]
    ordered = [column for column in preferred if column in deferred.columns] + [
        column for column in deferred.columns if column not in preferred
    ]
    deferred = deferred[ordered].sort_values(["source_year", "source_file", "sentence_index", "sentence_id"])

    output_csv = Path(args.output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    deferred.to_csv(output_csv, index=False)

    report = {
        "status": "passed",
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "policy": {
            "name": policy.name,
            "description": policy.description,
            "low_confidence_threshold": policy.low_confidence_threshold,
            "low_as_margin_threshold": policy.low_as_margin_threshold,
            "require_component_disagreement": policy.require_component_disagreement,
        },
        "inputs": {
            "input_root": str(Path(args.input_root).resolve()),
            "years": years,
            "model_id": str(args.model_id),
        },
        "outputs": {
            "review_sheet_csv": str(output_csv.resolve()),
        },
        "summary": {
            "rows_total": summary["rows_total"],
            "deferred_rows": summary["deferred_rows"],
            "deferred_rate": summary["deferred_rate"],
        },
        "by_year": summary["by_year"].to_dict(orient="records"),
        "by_label": summary["by_label"].to_dict(orient="records"),
    }

    report_path = Path(args.output_report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--years", nargs="+", required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--policy", default="conf_or_margin")
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--output-report", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_prepare(args)
    print(
        "[shadow-defer-prepare] prepared "
        f"policy={report['policy']['name']} deferred_rows={report['summary']['deferred_rows']} "
        f"rate={report['summary']['deferred_rate']:.4f}"
    )
    print(f"[shadow-defer-prepare] review sheet -> {args.output_csv}")


if __name__ == "__main__":
    main()
