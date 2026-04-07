"""Classify the active-window sentence tables into the preliminary model namespace."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from ai_washing_member.classification.model_runtime import (
    build_centroid_runtime,
    load_manifest,
    predict_sentences,
)
from ai_washing_member.classification.preliminary_pipeline import sha256_file
from ai_washing_member.labeling.common import ALLOWED_LABELS, load_table


def _load_metadata(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if str(payload.get("status", "")).strip() != "trained":
        raise ValueError("Model metadata must report `status = trained`.")
    return payload


def _resolve_runtime(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any], str, str]:
    selected_model_manifest = getattr(args, "selected_model_manifest", "")
    if selected_model_manifest:
        selected = load_manifest(selected_model_manifest)
        if str(selected.get("status", "")).strip() != "selected" or not isinstance(
            selected.get("winner"), dict
        ):
            raise SystemExit(
                "Selected-model manifest is not ready; cannot classify the active window yet."
            )
        winner = dict(selected["winner"])
        output_model_id = str(args.model_id or "prelim_selected_model_v1")
        source_window_id = str(args.source_window_id or winner.get("source_window_id", ""))
        return winner, selected, output_model_id, source_window_id

    metadata = _load_metadata(args.model_metadata)
    runtime = build_centroid_runtime(
        metadata_path=args.model_metadata,
        centroids_path=args.centroids,
    )
    output_model_id = str(args.model_id)
    source_window_id = str(metadata.get("source_window_id", args.source_window_id))
    return runtime, metadata, output_model_id, source_window_id


def run_classification(args: argparse.Namespace) -> dict:
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    report_path = Path(args.output_report)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    selected_model_manifest = getattr(args, "selected_model_manifest", "")
    runtime_manifest, metadata_source, output_model_id, source_window_id = _resolve_runtime(args)
    years = [int(year) for year in args.years]

    rows_by_year: dict[str, int] = {}
    outputs: dict[str, dict] = {}
    completed_years: list[int] = []

    for year in years:
        input_path = Path(args.input_root) / f"year={year}" / "ai_sentences.parquet"
        if not input_path.exists():
            raise SystemExit(f"Sentence table missing for year={year}: {input_path}")
        frame = load_table(input_path)
        required_columns = {"sentence_id", "sentence", "source_year", "source_cik"}
        missing = sorted(required_columns - set(frame.columns))
        if missing:
            raise ValueError(f"Sentence table for year={year} is missing columns: {missing}")

        predicted, score_rows = predict_sentences(
            frame["sentence"].fillna("").astype(str).tolist(),
            runtime_manifest,
        )
        classified = frame.copy()
        classified["predicted_label"] = predicted
        classified["model_id"] = output_model_id
        classified["selected_model_id"] = str(runtime_manifest.get("model_id", output_model_id))
        classified["source_window_id"] = source_window_id
        classified["classified_at_utc"] = pd.Timestamp.utcnow().isoformat()
        for label in ALLOWED_LABELS:
            classified[f"score_{label.lower()}"] = [
                float(row.get(label, 0.0)) for row in score_rows
            ]

        output_path = (
            output_root
            / f"year={year}"
            / f"model={output_model_id}"
            / "classified_sentences.parquet"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        classified.to_parquet(output_path, index=False)

        row_count = int(len(classified))
        rows_by_year[str(year)] = row_count
        completed_years.append(year)
        outputs[str(year)] = {
            "input_path": str(input_path),
            "input_sha256": sha256_file(input_path),
            "output_path": str(output_path),
            "output_sha256": sha256_file(output_path),
            "rows": row_count,
        }

    report = {
        "status": "passed",
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "summary": {
            "status": "passed",
            "model_id": output_model_id,
            "selected_model_id": str(runtime_manifest.get("model_id", output_model_id)),
            "preliminary_only": True,
            "source_window_id": source_window_id,
            "years_requested": years,
            "years_completed": completed_years,
            "completed_year_count": len(completed_years),
            "rows_by_year": rows_by_year,
            "total_rows": int(sum(rows_by_year.values())),
        },
        "inputs": {
            "selected_model_manifest": str(selected_model_manifest),
            "selected_model_manifest_sha256": sha256_file(selected_model_manifest),
            "model_metadata": str(args.model_metadata),
            "model_metadata_sha256": sha256_file(args.model_metadata),
            "centroids": str(args.centroids),
            "centroids_sha256": sha256_file(args.centroids),
        },
        "selected_model": metadata_source if selected_model_manifest else {},
        "outputs": outputs,
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", default="data/processed/sentences")
    parser.add_argument("--years", nargs="+", default=["2021", "2022", "2023", "2024"])
    parser.add_argument("--centroids", default="artifacts/models/mpnet_prelim_v1/centroids.json")
    parser.add_argument(
        "--model-metadata", default="artifacts/models/mpnet_prelim_v1/metadata.json"
    )
    parser.add_argument("--selected-model-manifest", default="")
    parser.add_argument("--output-root", default="data/processed/classifications")
    parser.add_argument(
        "--output-report", default="reports/classification/active_window_coverage_prelim_v1.json"
    )
    parser.add_argument("--model-id", default="mpnet_prelim_v1")
    parser.add_argument("--source-window-id", default="active_2021_2024")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_classification(args)
    print(
        "[prelim-classify] active window classified "
        f"years={report['summary']['years_completed']} total_rows={report['summary']['total_rows']}"
    )
    print(f"[prelim-classify] report -> {args.output_report}")


if __name__ == "__main__":
    main()
