"""Build preliminary firm-year AI metrics and proposal-defined narrative measures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from semantic_ai_washing.classification.model_runtime import load_manifest
from semantic_ai_washing.classification.preliminary_pipeline import sha256_file
from ai_washing_member.labeling.common import load_table


LABEL_TO_COUNT = {
    "Actionable": "n_A",
    "Speculative": "n_S",
    "Irrelevant": "n_I",
}
REQUIRED_MEASURES = ["AI_Focus", "log_1p_A", "log_1p_S", "SpecShare", "CredAI", "A_S"]


def _zscore(series: pd.Series) -> pd.Series:
    std = float(series.std(ddof=0))
    if std == 0.0:
        return pd.Series(np.zeros(len(series)), index=series.index, dtype=float)
    return (series - float(series.mean())) / std


def _load_classified_rows(input_root: str | Path, years: list[int], model_id: str) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for year in years:
        path = (
            Path(input_root)
            / f"year={year}"
            / f"model={model_id}"
            / "classified_sentences.parquet"
        )
        if not path.exists():
            raise FileNotFoundError(f"Missing classified sentences for year={year}: {path}")
        frame = load_table(path)
        required_columns = {"source_cik", "source_year", "source_file", "predicted_label"}
        missing = sorted(required_columns - set(frame.columns))
        if missing:
            raise ValueError(f"Classified sentences for year={year} missing columns: {missing}")
        frames.append(frame)
    if not frames:
        raise ValueError("No classified sentence tables were loaded.")
    return pd.concat(frames, ignore_index=True)


def _selected_model_context(selected_manifest_path: str | Path) -> dict[str, Any]:
    if not selected_manifest_path:
        return {}
    path = Path(selected_manifest_path)
    if not path.exists():
        return {}
    payload = load_manifest(path)
    winner = payload.get("winner") if isinstance(payload.get("winner"), dict) else {}
    benchmark_path = Path(str(payload.get("benchmark_matrix", "")))
    held_out_v2_sha256 = ""
    benchmark_name = ""
    if benchmark_path.exists():
        benchmark_payload = json.loads(benchmark_path.read_text(encoding="utf-8"))
        benchmark_name = str(
            benchmark_payload.get("summary", {}).get("primary_benchmark_name", "")
        )
        benchmarks = benchmark_payload.get("benchmarks", {})
        if benchmark_name in benchmarks:
            held_out_v2_sha256 = str(benchmarks[benchmark_name].get("sha256", ""))
    return {
        "selected_model_manifest": str(path),
        "selected_model_manifest_sha256": sha256_file(path),
        "selected_model_status": str(payload.get("status", "")),
        "selected_model_id": str(winner.get("model_id", "")),
        "benchmark_matrix": str(benchmark_path)
        if benchmark_path.exists()
        else str(benchmark_path),
        "benchmark_matrix_sha256": sha256_file(benchmark_path),
        "primary_benchmark_name": benchmark_name,
        "primary_benchmark_sha256": held_out_v2_sha256,
    }


def run_measure_build(args: argparse.Namespace) -> dict:
    ai_metrics_path = Path(args.output_ai_metrics)
    measures_path = Path(args.output_measures)
    report_path = Path(args.output_report)
    ai_metrics_path.parent.mkdir(parents=True, exist_ok=True)
    measures_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    years = [int(year) for year in args.years]
    classified = _load_classified_rows(args.input_root, years, args.model_id).copy()
    classified["source_cik"] = classified["source_cik"].astype(str)
    classified["source_year"] = classified["source_year"].astype(int)

    grouped = (
        classified.groupby(["source_cik", "source_year"], dropna=False)
        .agg(
            ai_total=("sentence_id", "count"),
            doc_count=("source_file", pd.Series.nunique),
        )
        .reset_index()
    )
    for label, column in LABEL_TO_COUNT.items():
        counts = (
            classified.loc[classified["predicted_label"] == label]
            .groupby(["source_cik", "source_year"])["sentence_id"]
            .count()
            .rename(column)
            .reset_index()
        )
        grouped = grouped.merge(counts, on=["source_cik", "source_year"], how="left")
    for column in LABEL_TO_COUNT.values():
        grouped[column] = grouped[column].fillna(0).astype(int)
    grouped["n_total"] = grouped["ai_total"].astype(int)
    grouped["source_window_id"] = str(args.source_window_id)
    grouped["model_id"] = str(args.model_id)
    grouped.to_parquet(ai_metrics_path, index=False)

    measures = grouped.copy()
    measures["AI_Focus"] = np.log1p(measures["ai_total"])
    measures["log_1p_A"] = np.log1p(measures["n_A"])
    measures["log_1p_S"] = np.log1p(measures["n_S"])
    denom = (measures["n_A"] + measures["n_S"]).replace(0, np.nan)
    measures["SpecShare"] = (measures["n_S"] / denom).fillna(0.0)
    measures["CredAI"] = _zscore(measures["n_A"].astype(float)) - _zscore(
        measures["n_S"].astype(float)
    )
    measures["A_S"] = np.log1p(measures["n_A"] / (1.0 + measures["n_S"]))
    measures.to_parquet(measures_path, index=False)

    selected_context = _selected_model_context(getattr(args, "selected_model_manifest", ""))
    report = {
        "status": "passed",
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "summary": {
            "status": "passed",
            "preliminary_only": True,
            "source_window_id": str(args.source_window_id),
            "model_id": str(args.model_id),
            "selected_model_id": selected_context.get("selected_model_id", ""),
            "rows_total": int(len(measures)),
            "years_covered": sorted({int(value) for value in measures["source_year"].unique()}),
            "firm_count": int(measures["source_cik"].nunique()),
            "named_measures": REQUIRED_MEASURES,
            "named_measures_complete": all(
                column in measures.columns for column in REQUIRED_MEASURES
            ),
            "primary_benchmark_name": selected_context.get("primary_benchmark_name", ""),
            "primary_benchmark_sha256": selected_context.get("primary_benchmark_sha256", ""),
        },
        "inputs": {
            "selected_model_manifest": selected_context.get("selected_model_manifest", ""),
            "selected_model_manifest_sha256": selected_context.get(
                "selected_model_manifest_sha256", ""
            ),
            "benchmark_matrix": selected_context.get("benchmark_matrix", ""),
            "benchmark_matrix_sha256": selected_context.get("benchmark_matrix_sha256", ""),
        },
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", default="data/processed/classifications")
    parser.add_argument("--years", nargs="+", default=["2021", "2022", "2023", "2024"])
    parser.add_argument("--model-id", default="mpnet_prelim_v1")
    parser.add_argument("--source-window-id", default="active_2021_2024")
    parser.add_argument("--selected-model-manifest", default="")
    parser.add_argument(
        "--output-ai-metrics",
        default="data/processed/aggregates/firm_year_ai_metrics_prelim_v1.parquet",
    )
    parser.add_argument(
        "--output-measures",
        default="data/processed/aggregates/firm_year_narrative_measures_prelim_v1.parquet",
    )
    parser.add_argument(
        "--output-report",
        default="reports/classification/firm_year_narrative_measures_prelim_v1.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_measure_build(args)
    print(
        "[prelim-measures] measures built "
        f"rows={report['summary']['rows_total']} firms={report['summary']['firm_count']}"
    )
    print(f"[prelim-measures] report -> {args.output_report}")


if __name__ == "__main__":
    main()
