"""Build a retraining candidate tranche from the reviewed boundary pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from ai_washing_member.labeling.common import load_table, normalize_sentence


def build_retraining_candidate_tranche(
    *,
    labels_master_path: str | Path,
    split_registry_path: str | Path,
    reviewed_boundary_pack_csv: str | Path,
    output_tranche_csv: str | Path,
    output_labels_master_parquet: str | Path,
    output_labels_master_review_csv: str | Path,
    output_json: str | Path | None = None,
) -> dict[str, object]:
    labels_master = load_table(labels_master_path).copy()
    split_registry = pd.read_csv(split_registry_path).copy()
    reviewed = pd.read_csv(reviewed_boundary_pack_csv).copy()

    required_labels = {"sentence_id", "sentence", "label"}
    required_split = {"sentence_id", "split"}
    required_reviewed = {
        "row_id",
        "sentence",
        "reviewed_label",
        "reviewed_rationale",
        "source",
        "case_kind",
    }
    missing_labels = sorted(required_labels - set(labels_master.columns))
    missing_split = sorted(required_split - set(split_registry.columns))
    missing_reviewed = sorted(required_reviewed - set(reviewed.columns))
    if missing_labels:
        raise ValueError(f"Labels master missing required columns: {missing_labels}")
    if missing_split:
        raise ValueError(f"Split registry missing required columns: {missing_split}")
    if missing_reviewed:
        raise ValueError(f"Reviewed boundary pack missing required columns: {missing_reviewed}")

    labels_master["sentence_norm_tranche"] = (
        labels_master["sentence"].fillna("").astype(str).map(normalize_sentence)
    )
    reviewed["sentence_norm_tranche"] = (
        reviewed["sentence"].fillna("").astype(str).map(normalize_sentence)
    )

    dup_norms = (
        labels_master.groupby("sentence_norm_tranche")["sentence_id"].nunique().reset_index()
    )
    ambiguous_norms = set(
        dup_norms.loc[dup_norms["sentence_id"] > 1, "sentence_norm_tranche"].tolist()
    )

    candidate = reviewed.merge(
        labels_master[
            [
                "sentence_id",
                "sentence_norm_tranche",
                "label",
                "batch_id",
                "batch_row_id",
                "source_cik",
                "source_year",
            ]
        ],
        on="sentence_norm_tranche",
        how="left",
        suffixes=("", "_labels_master"),
    )
    candidate = candidate.merge(
        split_registry[["sentence_id", "split"]],
        on="sentence_id",
        how="left",
    )
    candidate["ambiguous_overlap"] = candidate["sentence_norm_tranche"].isin(ambiguous_norms)
    candidate["training_eligible"] = candidate["sentence_id"].notna() & ~candidate["ambiguous_overlap"]
    candidate["label_changed"] = candidate["label"] != candidate["reviewed_label"]
    candidate["candidate_action"] = "benchmark_only"
    candidate.loc[candidate["ambiguous_overlap"], "candidate_action"] = "ambiguous_overlap_skip"
    candidate.loc[
        candidate["training_eligible"] & ~candidate["label_changed"],
        "candidate_action",
    ] = "retain_existing_label"
    candidate.loc[
        candidate["training_eligible"] & candidate["label_changed"],
        "candidate_action",
    ] = "update_existing_label"

    updated_labels_master = labels_master.copy()
    updates = candidate.loc[
        candidate["training_eligible"] & candidate["label_changed"],
        ["sentence_id", "reviewed_label"],
    ].drop_duplicates()
    update_map = dict(zip(updates["sentence_id"].astype(str), updates["reviewed_label"].astype(str)))
    if update_map:
        updated_labels_master["label"] = updated_labels_master["sentence_id"].astype(str).map(
            lambda sentence_id: update_map.get(sentence_id, updated_labels_master.loc[
                updated_labels_master["sentence_id"].astype(str) == sentence_id, "label"
            ].iloc[0])
        )

    updated_labels_master = updated_labels_master.drop(columns=["sentence_norm_tranche"])

    tranche = candidate[
        [
            "row_id",
            "source",
            "case_kind",
            "sentence",
            "reviewed_label",
            "reviewed_rationale",
            "sentence_id",
            "label",
            "split",
            "training_eligible",
            "label_changed",
            "candidate_action",
            "batch_id",
            "batch_row_id",
            "source_cik",
            "source_year",
        ]
    ].copy()

    output_tranche_path = Path(output_tranche_csv)
    output_tranche_path.parent.mkdir(parents=True, exist_ok=True)
    tranche.to_csv(output_tranche_path, index=False)

    output_labels_master_path = Path(output_labels_master_parquet)
    output_labels_master_path.parent.mkdir(parents=True, exist_ok=True)
    updated_labels_master.to_parquet(output_labels_master_path, index=False)

    output_labels_master_review_path = Path(output_labels_master_review_csv)
    output_labels_master_review_path.parent.mkdir(parents=True, exist_ok=True)
    updated_labels_master.to_csv(output_labels_master_review_path, index=False)

    summary = {
        "status": "passed",
        "reviewed_boundary_rows": int(len(reviewed)),
        "training_eligible_rows": int(candidate["training_eligible"].sum()),
        "benchmark_only_rows": int((candidate["candidate_action"] == "benchmark_only").sum()),
        "ambiguous_overlap_rows": int((candidate["candidate_action"] == "ambiguous_overlap_skip").sum()),
        "label_update_rows": int(
            (
                candidate["training_eligible"] & candidate["label_changed"]
            ).sum()
        ),
        "eligible_split_counts": {
            str(key): int(value)
            for key, value in candidate.loc[candidate["training_eligible"], "split"]
            .value_counts(dropna=False)
            .to_dict()
            .items()
        },
        "label_update_split_counts": {
            str(key): int(value)
            for key, value in candidate.loc[
                candidate["training_eligible"] & candidate["label_changed"], "split"
            ]
            .value_counts(dropna=False)
            .to_dict()
            .items()
        },
        "output_tranche_csv": str(output_tranche_path),
        "output_labels_master_parquet": str(output_labels_master_path),
        "output_labels_master_review_csv": str(output_labels_master_review_path),
    }
    if output_json is not None:
        output_json_path = Path(output_json)
        output_json_path.parent.mkdir(parents=True, exist_ok=True)
        output_json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        summary["output_json"] = str(output_json_path)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels-master", default="data/labels/v1/labels_master.parquet")
    parser.add_argument("--split-registry", default="data/metadata/splits/split_registry_v1.csv")
    parser.add_argument(
        "--reviewed-boundary-pack",
        default="reports/final/ai_washing_classifier_boundary_review_pack_v1.csv",
    )
    parser.add_argument(
        "--output-tranche-csv",
        default="reports/final/ai_washing_classifier_retraining_candidate_tranche_v1.csv",
    )
    parser.add_argument(
        "--output-labels-master-parquet",
        default="data/labels/v1/labels_master_boundary_revised_v1.parquet",
    )
    parser.add_argument(
        "--output-labels-master-review-csv",
        default="data/labels/v1/labels_master_boundary_revised_v1_review.csv",
    )
    parser.add_argument(
        "--output-json",
        default="reports/final/ai_washing_classifier_retraining_candidate_tranche_v1.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = build_retraining_candidate_tranche(
        labels_master_path=args.labels_master,
        split_registry_path=args.split_registry,
        reviewed_boundary_pack_csv=args.reviewed_boundary_pack,
        output_tranche_csv=args.output_tranche_csv,
        output_labels_master_parquet=args.output_labels_master_parquet,
        output_labels_master_review_csv=args.output_labels_master_review_csv,
        output_json=args.output_json,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
