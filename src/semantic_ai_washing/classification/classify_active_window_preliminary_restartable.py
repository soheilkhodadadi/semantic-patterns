"""Restartable chunked preliminary classification over sentence tables."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from semantic_ai_washing.classification.classify_active_window_preliminary import _resolve_runtime
from ai_washing_member.classification.model_runtime import predict_sentences, warm_runtime
from ai_washing_member.classification.preliminary_pipeline import sha256_file
from ai_washing_member.labeling.common import ALLOWED_LABELS, load_table


def _now_utc() -> str:
    return pd.Timestamp.utcnow().isoformat()


def _dump_json(path: str | Path, payload: dict[str, Any]) -> None:
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _build_progress_payload(
    *,
    years_requested: list[int],
    years_completed: list[int],
    current_year: int | None,
    current_chunk_index: int | None,
    year_state: dict[str, Any],
    status: str,
    output_root: str | Path,
    output_report: str | Path,
    chunk_size: int,
) -> dict[str, Any]:
    return {
        "status": status,
        "generated_at_utc": _now_utc(),
        "summary": {
            "status": status,
            "years_requested": years_requested,
            "years_completed": years_completed,
            "completed_year_count": len(years_completed),
            "current_year": current_year,
            "current_chunk_index": current_chunk_index,
            "chunk_size": int(chunk_size),
            "output_root": str(output_root),
            "output_report": str(output_report),
        },
        "years": year_state,
    }


def _write_progress(
    *,
    progress_path: str | Path,
    years_requested: list[int],
    years_completed: list[int],
    current_year: int | None,
    current_chunk_index: int | None,
    year_state: dict[str, Any],
    status: str,
    output_root: str | Path,
    output_report: str | Path,
    chunk_size: int,
) -> None:
    _dump_json(
        progress_path,
        _build_progress_payload(
            years_requested=years_requested,
            years_completed=years_completed,
            current_year=current_year,
            current_chunk_index=current_chunk_index,
            year_state=year_state,
            status=status,
            output_root=output_root,
            output_report=output_report,
            chunk_size=chunk_size,
        ),
    )


def _write_warming_progress(
    *,
    progress_path: str | Path,
    years_requested: list[int],
    years_completed: list[int],
    year_state: dict[str, Any],
    output_root: str | Path,
    output_report: str | Path,
    chunk_size: int,
    stage: str,
) -> None:
    warming_state = dict(year_state)
    warming_state["_runtime_warmup"] = {"stage": stage}
    _write_progress(
        progress_path=progress_path,
        years_requested=years_requested,
        years_completed=years_completed,
        current_year=None,
        current_chunk_index=None,
        year_state=warming_state,
        status="warming_runtime",
        output_root=output_root,
        output_report=output_report,
        chunk_size=chunk_size,
    )


def _classified_output_path(output_root: str | Path, *, year: int, model_id: str) -> Path:
    return (
        Path(output_root) / f"year={year}" / f"model={model_id}" / "classified_sentences.parquet"
    )


def _chunk_dir(output_root: str | Path, *, year: int, model_id: str) -> Path:
    return Path(output_root) / f"year={year}" / f"model={model_id}" / "_chunks"


def _write_chunk(
    *,
    frame: pd.DataFrame,
    runtime_manifest: dict[str, Any],
    output_model_id: str,
    source_window_id: str,
    chunk_path: Path,
) -> int:
    predicted, score_rows = predict_sentences(
        frame["sentence"].fillna("").astype(str).tolist(),
        runtime_manifest,
    )
    classified = frame.copy()
    classified["predicted_label"] = predicted
    classified["model_id"] = output_model_id
    classified["selected_model_id"] = str(runtime_manifest.get("model_id", output_model_id))
    classified["source_window_id"] = source_window_id
    classified["classified_at_utc"] = _now_utc()
    for label in ALLOWED_LABELS:
        classified[f"score_{label.lower()}"] = [float(row.get(label, 0.0)) for row in score_rows]

    chunk_path.parent.mkdir(parents=True, exist_ok=True)
    classified.to_parquet(chunk_path, index=False)
    return int(len(classified))


def _finalize_year(
    *,
    output_root: str | Path,
    year: int,
    model_id: str,
) -> dict[str, Any]:
    chunk_dir = _chunk_dir(output_root, year=year, model_id=model_id)
    chunk_paths = sorted(chunk_dir.glob("chunk_*.parquet"))
    if not chunk_paths:
        raise ValueError(f"No chunk files available to finalize year={year}.")
    frames = [pd.read_parquet(path) for path in chunk_paths]
    classified = pd.concat(frames, ignore_index=True)
    output_path = _classified_output_path(output_root, year=year, model_id=model_id)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    classified.to_parquet(output_path, index=False)
    return {
        "output_path": str(output_path),
        "output_sha256": sha256_file(output_path),
        "rows": int(len(classified)),
        "chunk_count": len(chunk_paths),
    }


def run_classification_restartable(args: argparse.Namespace) -> dict[str, Any]:
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    report_path = Path(args.output_report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    progress_path = Path(args.progress_report)
    progress_path.parent.mkdir(parents=True, exist_ok=True)

    runtime_manifest, metadata_source, output_model_id, source_window_id = _resolve_runtime(args)
    years = [int(year) for year in args.years]
    chunk_size = int(args.chunk_size)

    rows_by_year: dict[str, int] = {}
    outputs: dict[str, dict[str, Any]] = {}
    completed_years: list[int] = []
    year_state: dict[str, Any] = {}

    _write_progress(
        progress_path=progress_path,
        years_requested=years,
        years_completed=completed_years,
        current_year=None,
        current_chunk_index=None,
        year_state=year_state,
        status="starting",
        output_root=output_root,
        output_report=report_path,
        chunk_size=chunk_size,
    )

    try:
        _write_warming_progress(
            progress_path=progress_path,
            years_requested=years,
            years_completed=completed_years,
            year_state=year_state,
            output_root=output_root,
            output_report=report_path,
            chunk_size=chunk_size,
            stage="starting",
        )
        runtime_payload = (
            runtime_manifest.get("runtime", {})
            if isinstance(runtime_manifest.get("runtime", {}), dict)
            else {}
        )
        if runtime_payload:
            warm_runtime(
                runtime_manifest,
                on_stage=lambda stage: _write_warming_progress(
                    progress_path=progress_path,
                    years_requested=years,
                    years_completed=completed_years,
                    year_state=year_state,
                    output_root=output_root,
                    output_report=report_path,
                    chunk_size=chunk_size,
                    stage=stage,
                ),
            )
        else:
            _write_warming_progress(
                progress_path=progress_path,
                years_requested=years,
                years_completed=completed_years,
                year_state=year_state,
                output_root=output_root,
                output_report=report_path,
                chunk_size=chunk_size,
                stage="skipped",
            )
        _write_progress(
            progress_path=progress_path,
            years_requested=years,
            years_completed=completed_years,
            current_year=None,
            current_chunk_index=None,
            year_state=year_state,
            status="running",
            output_root=output_root,
            output_report=report_path,
            chunk_size=chunk_size,
        )
        for year in years:
            input_path = Path(args.input_root) / f"year={year}" / "ai_sentences.parquet"
            if not input_path.exists():
                raise SystemExit(f"Sentence table missing for year={year}: {input_path}")

            output_path = _classified_output_path(output_root, year=year, model_id=output_model_id)
            chunk_dir = _chunk_dir(output_root, year=year, model_id=output_model_id)
            chunk_dir.mkdir(parents=True, exist_ok=True)

            if output_path.exists() and not bool(args.force_recompute):
                rows = int(len(pd.read_parquet(output_path, columns=["sentence_id"])))
                rows_by_year[str(year)] = rows
                completed_years.append(year)
                outputs[str(year)] = {
                    "input_path": str(input_path),
                    "input_sha256": sha256_file(input_path),
                    "output_path": str(output_path),
                    "output_sha256": sha256_file(output_path),
                    "rows": rows,
                    "reused": True,
                }
                year_state[str(year)] = {
                    "status": "reused",
                    "rows_total": rows,
                    "rows_processed": rows,
                    "chunk_count": len(list(chunk_dir.glob("chunk_*.parquet"))),
                }
                _write_progress(
                    progress_path=progress_path,
                    years_requested=years,
                    years_completed=completed_years,
                    current_year=None,
                    current_chunk_index=None,
                    year_state=year_state,
                    status="running",
                    output_root=output_root,
                    output_report=report_path,
                    chunk_size=chunk_size,
                )
                continue

            frame = load_table(input_path)
            required_columns = {"sentence_id", "sentence", "source_year", "source_cik"}
            missing = sorted(required_columns - set(frame.columns))
            if missing:
                raise ValueError(f"Sentence table for year={year} is missing columns: {missing}")

            total_rows = int(len(frame))
            year_state[str(year)] = {
                "status": "running",
                "rows_total": total_rows,
                "rows_processed": 0,
                "chunk_count": int((total_rows + chunk_size - 1) / max(chunk_size, 1)),
                "chunk_rows_completed": 0,
            }
            _write_progress(
                progress_path=progress_path,
                years_requested=years,
                years_completed=completed_years,
                current_year=year,
                current_chunk_index=0,
                year_state=year_state,
                status="running",
                output_root=output_root,
                output_report=report_path,
                chunk_size=chunk_size,
            )

            chunk_count = int((total_rows + chunk_size - 1) / max(chunk_size, 1))
            rows_processed = 0
            for chunk_index in range(chunk_count):
                start = chunk_index * chunk_size
                stop = min(start + chunk_size, total_rows)
                chunk_path = chunk_dir / f"chunk_{chunk_index:04d}.parquet"
                if chunk_path.exists() and not bool(args.force_recompute):
                    chunk_rows = int(len(pd.read_parquet(chunk_path, columns=["sentence_id"])))
                else:
                    chunk_rows = _write_chunk(
                        frame=frame.iloc[start:stop].copy(),
                        runtime_manifest=runtime_manifest,
                        output_model_id=output_model_id,
                        source_window_id=source_window_id,
                        chunk_path=chunk_path,
                    )
                rows_processed += chunk_rows
                year_state[str(year)] = {
                    "status": "running",
                    "rows_total": total_rows,
                    "rows_processed": rows_processed,
                    "chunk_count": chunk_count,
                    "chunk_rows_completed": chunk_index + 1,
                    "last_chunk_path": str(chunk_path),
                }
                _write_progress(
                    progress_path=progress_path,
                    years_requested=years,
                    years_completed=completed_years,
                    current_year=year,
                    current_chunk_index=chunk_index,
                    year_state=year_state,
                    status="running",
                    output_root=output_root,
                    output_report=report_path,
                    chunk_size=chunk_size,
                )

            finalized = _finalize_year(
                output_root=output_root, year=year, model_id=output_model_id
            )
            rows_by_year[str(year)] = int(finalized["rows"])
            completed_years.append(year)
            outputs[str(year)] = {
                "input_path": str(input_path),
                "input_sha256": sha256_file(input_path),
                **finalized,
            }
            year_state[str(year)] = {
                "status": "completed",
                "rows_total": total_rows,
                "rows_processed": total_rows,
                "chunk_count": int(finalized["chunk_count"]),
                "output_path": str(finalized["output_path"]),
            }
            _write_progress(
                progress_path=progress_path,
                years_requested=years,
                years_completed=completed_years,
                current_year=None,
                current_chunk_index=None,
                year_state=year_state,
                status="running",
                output_root=output_root,
                output_report=report_path,
                chunk_size=chunk_size,
            )

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
                "years_completed": completed_years,
                "completed_year_count": len(completed_years),
                "rows_by_year": rows_by_year,
                "total_rows": int(sum(rows_by_year.values())),
                "chunk_size": chunk_size,
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
            "selected_model": metadata_source
            if getattr(args, "selected_model_manifest", "")
            else {},
            "outputs": outputs,
            "progress_report": str(progress_path),
        }
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        _write_progress(
            progress_path=progress_path,
            years_requested=years,
            years_completed=completed_years,
            current_year=None,
            current_chunk_index=None,
            year_state=year_state,
            status="completed",
            output_root=output_root,
            output_report=report_path,
            chunk_size=chunk_size,
        )
        return report
    except Exception:
        _write_progress(
            progress_path=progress_path,
            years_requested=years,
            years_completed=completed_years,
            current_year=None,
            current_chunk_index=None,
            year_state=year_state,
            status="failed",
            output_root=output_root,
            output_report=report_path,
            chunk_size=chunk_size,
        )
        raise


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
        "--output-report",
        default="reports/classification/active_window_coverage_prelim_restartable_v1.json",
    )
    parser.add_argument(
        "--progress-report",
        default="reports/classification/active_window_coverage_prelim_restartable_progress_v1.json",
    )
    parser.add_argument("--model-id", default="mpnet_prelim_v1")
    parser.add_argument("--source-window-id", default="active_2021_2024")
    parser.add_argument("--chunk-size", type=int, default=512)
    parser.add_argument("--force-recompute", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_classification_restartable(args)
    print(
        "[prelim-classify-restartable] active window classified "
        f"years={report['summary']['years_completed']} total_rows={report['summary']['total_rows']}"
    )
    print(f"[prelim-classify-restartable] report -> {args.output_report}")
    print(f"[prelim-classify-restartable] progress -> {args.progress_report}")


if __name__ == "__main__":
    main()
