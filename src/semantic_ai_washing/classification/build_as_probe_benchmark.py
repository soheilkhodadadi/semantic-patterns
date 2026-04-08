"""Build a clean fixed A/S probe benchmark from revised adjudication rows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


BENCHMARK_COLUMNS = [
    "row_id",
    "sentence_id",
    "sentence",
    "revised_label",
    "relevance_precondition",
    "currentness_gate",
    "business_claim_gate",
    "benchmark_role",
]


def build_as_probe_benchmark(
    *,
    revised_labels_csv: str | Path,
    output_csv: str | Path,
    output_blinded_csv: str | Path,
    output_json: str | Path | None = None,
) -> dict[str, object]:
    revised = pd.read_csv(revised_labels_csv)

    required = {
        "row_id",
        "sentence",
        "revised_label",
        "relevance_precondition",
        "currentness_gate",
        "business_claim_gate",
    }
    missing = required.difference(revised.columns)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Revised-label input is missing required columns: {missing_list}")

    benchmark = revised[
        [
            "row_id",
            "sentence",
            "revised_label",
            "relevance_precondition",
            "currentness_gate",
            "business_claim_gate",
        ]
    ].copy()
    benchmark.insert(1, "sentence_id", pd.NA)
    benchmark["benchmark_role"] = "fixed_as_probe_v2"
    benchmark = benchmark.sort_values("row_id").reset_index(drop=True)
    benchmark = benchmark[BENCHMARK_COLUMNS]

    blinded = benchmark[["row_id", "sentence"]].copy()
    blinded["benchmark_role"] = "fixed_as_probe_v2_blinded"

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    benchmark.to_csv(output_path, index=False)

    blinded_path = Path(output_blinded_csv)
    blinded_path.parent.mkdir(parents=True, exist_ok=True)
    blinded.to_csv(blinded_path, index=False)

    transition_counts = (
        revised[["label_reference", "revised_label"]]
        .dropna(subset=["label_reference", "revised_label"])
        .assign(
            transition=lambda df: df["label_reference"].astype(str)
            + "->"
            + df["revised_label"].astype(str)
        )["transition"]
        .value_counts()
        .to_dict()
    )

    summary = {
        "status": "passed",
        "row_count": int(len(benchmark)),
        "revised_label_counts": {
            str(key): int(value)
            for key, value in benchmark["revised_label"].value_counts().to_dict().items()
        },
        "reference_to_revised": {
            str(key): int(value) for key, value in transition_counts.items()
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
        "--revised-labels-csv",
        default="reports/final/ai_washing_classifier_rubric_probe_slice_revised_labels_v1.csv",
    )
    parser.add_argument(
        "--output-csv",
        default="reports/final/ai_washing_classifier_as_probe_benchmark_v2.csv",
    )
    parser.add_argument(
        "--output-blinded-csv",
        default="reports/final/ai_washing_classifier_as_probe_benchmark_blinded_v1.csv",
    )
    parser.add_argument(
        "--output-json",
        default="reports/final/ai_washing_classifier_as_probe_benchmark_v2.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = build_as_probe_benchmark(
        revised_labels_csv=args.revised_labels_csv,
        output_csv=args.output_csv,
        output_blinded_csv=args.output_blinded_csv,
        output_json=args.output_json,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
