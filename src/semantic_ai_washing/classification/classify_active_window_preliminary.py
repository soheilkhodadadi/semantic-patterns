"""Classify the active-window sentence tables into the preliminary model namespace."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from semantic_ai_washing.classification.preliminary_pipeline import (
    classify_embeddings,
    embed_sentences,
    load_centroids,
    sha256_file,
)
from semantic_ai_washing.labeling.common import load_table


def _load_metadata(path: str | Path) -> dict:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if str(payload.get("status", "")).strip() != "trained":
        raise ValueError("Model metadata must report `status = trained`.")
    return payload


def run_classification(args: argparse.Namespace) -> dict:
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    report_path = Path(args.output_report)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    metadata = _load_metadata(args.model_metadata)
    centroids = load_centroids(args.centroids)
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
        embeddings = embed_sentences(
            frame["sentence"].fillna("").astype(str).tolist(),
            backend=str(metadata.get("embedding_backend", args.embedding_backend)),
            model_name=str(metadata.get("model_name", args.model_name)),
            batch_size=int(args.batch_size),
            hash_dim=int(metadata.get("hash_dim", args.hash_dim)),
        )
        predicted, score_rows = classify_embeddings(embeddings, centroids)
        classified = frame.copy()
        classified["predicted_label"] = predicted
        classified["model_id"] = str(args.model_id)
        classified["source_window_id"] = metadata.get("source_window_id", args.source_window_id)
        classified["classified_at_utc"] = pd.Timestamp.utcnow().isoformat()
        for label in centroids:
            classified[f"score_{label.lower()}"] = [row[label] for row in score_rows]

        output_path = (
            output_root
            / f"year={year}"
            / f"model={args.model_id}"
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
            "model_id": str(args.model_id),
            "preliminary_only": True,
            "source_window_id": metadata.get("source_window_id", args.source_window_id),
            "years_requested": years,
            "years_completed": completed_years,
            "completed_year_count": len(completed_years),
            "rows_by_year": rows_by_year,
            "total_rows": int(sum(rows_by_year.values())),
        },
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
    parser.add_argument("--output-root", default="data/processed/classifications")
    parser.add_argument(
        "--output-report", default="reports/classification/active_window_coverage_prelim_v1.json"
    )
    parser.add_argument("--model-id", default="mpnet_prelim_v1")
    parser.add_argument("--source-window-id", default="active_2021_2024")
    parser.add_argument("--embedding-backend", default="sentence_transformers")
    parser.add_argument("--model-name", default="sentence-transformers/all-mpnet-base-v2")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--hash-dim", type=int, default=64)
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
