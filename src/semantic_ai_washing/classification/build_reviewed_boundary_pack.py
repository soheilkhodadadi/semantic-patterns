"""Build a larger reviewed boundary pack from audit rows and adjudicated labels."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


REVIEWED_COLUMNS = [
    "row_id",
    "source",
    "case_kind",
    "priority",
    "sentence",
    "failure_mode_primary",
    "failure_mode_note",
    "label_reference",
    "label_other",
    "reviewed_label",
    "reviewed_rationale",
    "benchmark_role",
]


def build_reviewed_boundary_pack(
    *,
    tagged_audit_csv: str | Path,
    existing_benchmark_csv: str | Path,
    remaining_labels_csv: str | Path,
    output_csv: str | Path,
    output_blinded_csv: str | Path,
    output_json: str | Path | None = None,
) -> dict[str, object]:
    audit = pd.read_csv(tagged_audit_csv)
    existing = pd.read_csv(existing_benchmark_csv)[["row_id", "revised_label"]].copy()
    existing["row_id"] = existing["row_id"].astype(str)
    existing = existing.rename(columns={"revised_label": "reviewed_label"})
    existing["reviewed_rationale"] = "Carried forward from fixed probe adjudication."

    remaining = pd.read_csv(remaining_labels_csv)
    required_remaining = {"row_id", "reviewed_label", "reviewed_rationale"}
    missing_remaining = required_remaining.difference(remaining.columns)
    if missing_remaining:
        missing_list = ", ".join(sorted(missing_remaining))
        raise ValueError(
            "Remaining-label CSV missing required columns: " f"{missing_list}"
        )
    remaining = remaining[["row_id", "reviewed_label", "reviewed_rationale"]].copy()
    remaining["row_id"] = remaining["row_id"].astype(str)

    labels = pd.concat([existing, remaining], ignore_index=True)
    if labels["row_id"].duplicated().any():
        dupes = labels.loc[labels["row_id"].duplicated(), "row_id"].tolist()
        raise ValueError(f"Duplicate reviewed labels for row_id values: {dupes}")

    audit["row_id"] = audit["row_id"].astype(str)
    reviewed = audit.merge(labels, on="row_id", how="left", validate="one_to_one")
    if reviewed["reviewed_label"].isna().any():
        missing_ids = reviewed.loc[reviewed["reviewed_label"].isna(), "row_id"].tolist()
        raise ValueError(f"Missing reviewed labels for row_id values: {missing_ids}")

    reviewed["benchmark_role"] = "boundary_review_pack_v1"
    reviewed = reviewed.sort_values(["priority", "row_id"]).reset_index(drop=True)
    reviewed = reviewed[REVIEWED_COLUMNS]

    blinded = reviewed[
        ["row_id", "source", "case_kind", "priority", "sentence", "failure_mode_primary"]
    ].copy()
    blinded["benchmark_role"] = "boundary_review_pack_v1_blinded"

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    reviewed.to_csv(output_path, index=False)

    blinded_path = Path(output_blinded_csv)
    blinded_path.parent.mkdir(parents=True, exist_ok=True)
    blinded.to_csv(blinded_path, index=False)

    summary = {
        "status": "passed",
        "row_count": int(len(reviewed)),
        "reviewed_label_counts": {
            str(key): int(value)
            for key, value in reviewed["reviewed_label"].value_counts().to_dict().items()
        },
        "failure_mode_counts": {
            str(key): int(value)
            for key, value in reviewed["failure_mode_primary"].value_counts().to_dict().items()
        },
        "output_csv": str(output_path),
        "output_blinded_csv": str(blinded_path),
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
        "--tagged-audit-csv",
        default="reports/final/ai_washing_classifier_as_boundary_audit_pack_tagged_v1.csv",
    )
    parser.add_argument(
        "--existing-benchmark-csv",
        default="reports/final/ai_washing_classifier_as_probe_benchmark_v2.csv",
    )
    parser.add_argument("--remaining-labels-csv", required=True)
    parser.add_argument(
        "--output-csv",
        default="reports/final/ai_washing_classifier_boundary_review_pack_v1.csv",
    )
    parser.add_argument(
        "--output-blinded-csv",
        default="reports/final/ai_washing_classifier_boundary_review_pack_blinded_v1.csv",
    )
    parser.add_argument(
        "--output-json",
        default="reports/final/ai_washing_classifier_boundary_review_pack_v1.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = build_reviewed_boundary_pack(
        tagged_audit_csv=args.tagged_audit_csv,
        existing_benchmark_csv=args.existing_benchmark_csv,
        remaining_labels_csv=args.remaining_labels_csv,
        output_csv=args.output_csv,
        output_blinded_csv=args.output_blinded_csv,
        output_json=args.output_json,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
