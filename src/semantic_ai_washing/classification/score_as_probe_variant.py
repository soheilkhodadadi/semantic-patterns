"""Score a probe-variant label file against the fixed A/S benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def _load_variant_csv_tolerant(path: str | Path) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    with Path(path).open(encoding="utf-8") as handle:
        header = handle.readline().strip()
        expected = "row_id,predicted_label,variant_id,short_rationale"
        if header != expected:
            raise ValueError(
                "Variant CSV must start with "
                f"`{expected}`, got `{header}` instead."
            )
        for line in handle:
            text = line.rstrip("\n")
            if not text:
                continue
            parts = text.split(",", 3)
            if len(parts) != 4:
                raise ValueError(f"Malformed variant row: {text}")
            row_id, predicted_label, variant_id, short_rationale = parts
            rows.append(
                {
                    "row_id": row_id,
                    "predicted_label": predicted_label,
                    "variant_id": variant_id,
                    "short_rationale": short_rationale.strip().strip('"'),
                }
            )
    return pd.DataFrame(rows)


def score_as_probe_variant(
    *,
    benchmark_csv: str | Path,
    variant_csv: str | Path,
    output_json: str | Path | None = None,
) -> dict[str, object]:
    benchmark = pd.read_csv(benchmark_csv)
    variant = _load_variant_csv_tolerant(variant_csv)
    benchmark["row_id"] = benchmark["row_id"].astype(str)
    variant["row_id"] = variant["row_id"].astype(str)

    if "revised_label" in benchmark.columns:
        benchmark_label_col = "revised_label"
    elif "reviewed_label" in benchmark.columns:
        benchmark_label_col = "reviewed_label"
    else:
        raise ValueError(
            "Benchmark CSV must contain either `revised_label` or `reviewed_label`."
        )

    required_benchmark = {"row_id", "sentence", benchmark_label_col}
    required_variant = {"row_id", "predicted_label", "variant_id"}
    missing_benchmark = required_benchmark.difference(benchmark.columns)
    missing_variant = required_variant.difference(variant.columns)
    if missing_benchmark:
        missing_list = ", ".join(sorted(missing_benchmark))
        raise ValueError(f"Benchmark CSV missing required columns: {missing_list}")
    if missing_variant:
        missing_list = ", ".join(sorted(missing_variant))
        raise ValueError(f"Variant CSV missing required columns: {missing_list}")

    merged = benchmark.merge(variant, on="row_id", how="left", validate="one_to_one")
    if merged["predicted_label"].isna().any():
        missing_ids = merged.loc[merged["predicted_label"].isna(), "row_id"].tolist()
        raise ValueError(f"Variant CSV is missing predictions for row_id values: {missing_ids}")

    merged["is_match"] = merged[benchmark_label_col] == merged["predicted_label"]
    accuracy = float(merged["is_match"].mean())

    mismatch_rows = merged.loc[~merged["is_match"]].copy()
    mismatch_rows = mismatch_rows[
        [
            "row_id",
            "sentence",
            benchmark_label_col,
            "predicted_label",
            "variant_id",
            "short_rationale",
        ]
    ]

    summary = {
        "status": "passed",
        "variant_id": str(variant["variant_id"].dropna().iloc[0]),
        "row_count": int(len(merged)),
        "match_count": int(merged["is_match"].sum()),
        "mismatch_count": int((~merged["is_match"]).sum()),
        "accuracy": accuracy,
        "predicted_label_counts": {
            str(key): int(value)
            for key, value in merged["predicted_label"].value_counts().to_dict().items()
        },
        "benchmark_label_counts": {
            str(key): int(value)
            for key, value in merged[benchmark_label_col].value_counts().to_dict().items()
        },
        "transition_counts": {
            str(key): int(value)
            for key, value in (
                merged.assign(
                    transition=merged[benchmark_label_col].astype(str)
                    + "->"
                    + merged["predicted_label"].astype(str)
                )["transition"]
                .value_counts()
                .to_dict()
                .items()
            )
        },
        "mismatch_rows": mismatch_rows.to_dict(orient="records"),
    }

    if output_json is not None:
        output_path = Path(output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        summary["output_json"] = str(output_path)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--benchmark-csv",
        default="reports/final/ai_washing_classifier_as_probe_benchmark_v2.csv",
    )
    parser.add_argument("--variant-csv", required=True)
    parser.add_argument("--output-json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = score_as_probe_variant(
        benchmark_csv=args.benchmark_csv,
        variant_csv=args.variant_csv,
        output_json=args.output_json,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
