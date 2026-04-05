"""Reconcile final report/progress artifacts from existing preliminary classification outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq

from semantic_ai_washing.classification.classify_active_window_preliminary import _resolve_runtime
from ai_washing_member.classification.preliminary_pipeline import sha256_file


def _now_utc() -> str:
    return pd.Timestamp.utcnow().isoformat()


def _row_count(path: str | Path) -> int:
    resolved = Path(path)
    try:
        return int(pq.ParquetFile(resolved).metadata.num_rows)
    except Exception:
        return int(len(pd.read_parquet(resolved, columns=["sentence_id"])))


def _chunk_count(output_root: str | Path, *, year: int, model_id: str) -> int:
    chunk_dir = Path(output_root) / f"year={year}" / f"model={model_id}" / "_chunks"
    if not chunk_dir.exists():
        return 0
    return len(list(chunk_dir.glob("chunk_*.parquet")))


def reconcile_outputs(args: argparse.Namespace) -> dict[str, Any]:
    runtime_manifest, metadata_source, output_model_id, source_window_id = _resolve_runtime(args)
    years = [int(year) for year in args.years]

    outputs: dict[str, dict[str, Any]] = {}
    rows_by_year: dict[str, int] = {}
    progress_years: dict[str, Any] = {}

    for year in years:
        output_path = (
            Path(args.output_root)
            / f"year={year}"
            / f"model={output_model_id}"
            / "classified_sentences.parquet"
        )
        if not output_path.exists():
            raise SystemExit(f"Missing classified output for year={year}: {output_path}")
        input_path = Path(args.input_root) / f"year={year}" / "ai_sentences.parquet"
        rows = _row_count(output_path)
        chunk_count = _chunk_count(args.output_root, year=year, model_id=output_model_id)
        rows_by_year[str(year)] = rows
        outputs[str(year)] = {
            "input_path": str(input_path),
            "input_sha256": sha256_file(input_path),
            "output_path": str(output_path),
            "output_sha256": sha256_file(output_path),
            "rows": rows,
            "reused": True,
        }
        progress_years[str(year)] = {
            "status": "completed",
            "rows_total": rows,
            "rows_processed": rows,
            "chunk_count": chunk_count,
            "output_path": str(output_path),
        }

    report = {
        "status": "passed",
        "generated_at_utc": _now_utc(),
        "summary": {
            "status": "passed",
            "model_id": output_model_id,
            "selected_model_id": str(runtime_manifest.get("model_id", output_model_id)),
            "preliminary_only": True,
            "source_window_id": source_window_id,
            "years_requested": years,
            "years_completed": years,
            "completed_year_count": len(years),
            "rows_by_year": rows_by_year,
            "total_rows": int(sum(rows_by_year.values())),
        },
        "inputs": {
            "selected_model_manifest": str(getattr(args, "selected_model_manifest", "")),
            "selected_model_manifest_sha256": sha256_file(
                getattr(args, "selected_model_manifest", "")
            ),
            "model_metadata": str(args.model_metadata),
            "model_metadata_sha256": sha256_file(args.model_metadata),
            "centroids": str(args.centroids),
            "centroids_sha256": sha256_file(args.centroids),
        },
        "selected_model": metadata_source if getattr(args, "selected_model_manifest", "") else {},
        "outputs": outputs,
        "progress_report": str(args.progress_report),
    }

    progress = {
        "status": "completed",
        "generated_at_utc": _now_utc(),
        "summary": {
            "status": "completed",
            "years_requested": years,
            "years_completed": years,
            "completed_year_count": len(years),
            "current_year": None,
            "current_chunk_index": None,
            "chunk_size": int(args.chunk_size),
            "output_root": str(args.output_root),
            "output_report": str(args.output_report),
        },
        "years": progress_years,
    }

    report_path = Path(args.output_report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    progress_path = Path(args.progress_report)
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    progress_path.write_text(json.dumps(progress, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", default="data/processed/sentences_clean")
    parser.add_argument(
        "--years",
        nargs="+",
        default=["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"],
    )
    parser.add_argument("--centroids", default="artifacts/models/mpnet_prelim_v1/centroids.json")
    parser.add_argument(
        "--model-metadata", default="artifacts/models/mpnet_prelim_v1/metadata.json"
    )
    parser.add_argument("--selected-model-manifest", default="")
    parser.add_argument("--output-root", default="data/processed/classifications_clean")
    parser.add_argument(
        "--output-report",
        default="reports/classification/active_window_coverage_prelim_clean_restartable_v1.json",
    )
    parser.add_argument(
        "--progress-report",
        default="reports/classification/active_window_coverage_prelim_clean_restartable_progress_v1.json",
    )
    parser.add_argument("--model-id", default="binary_relevance_then_as_v1")
    parser.add_argument("--source-window-id", default="annual_10k_2016_2024_clean")
    parser.add_argument("--chunk-size", type=int, default=256)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = reconcile_outputs(args)
    print(
        "[prelim-classify-reconcile] classification outputs reconciled "
        f"years={report['summary']['years_completed']} total_rows={report['summary']['total_rows']}"
    )
    print(f"[prelim-classify-reconcile] report -> {args.output_report}")


if __name__ == "__main__":
    main()
