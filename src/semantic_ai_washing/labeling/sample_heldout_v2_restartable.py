"""Restartable held_out_v2 candidate sampling with progress logging."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from semantic_ai_washing.classification.model_runtime import (
    build_legacy_two_stage_runtime,
    predict_sentences,
)
from semantic_ai_washing.labeling.sample_heldout_v2_candidates import (
    DEFAULT_YEARS,
    LABELS,
    load_exclusions,
    load_sentence_pool,
    select_candidate_review_rows,
    write_review_package,
)


def _now_utc() -> str:
    return pd.Timestamp.utcnow().isoformat()


def _dump_json(path: str | Path, payload: dict[str, Any]) -> None:
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _file_fingerprint(path: str | Path) -> dict[str, Any]:
    resolved = Path(path)
    stat = resolved.stat()
    return {
        "path": str(resolved.resolve()),
        "size": int(stat.st_size),
        "mtime_ns": int(stat.st_mtime_ns),
    }


def _sha256_file(path: str | Path) -> str:
    resolved = Path(path)
    hasher = hashlib.sha256()
    with resolved.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _cache_metadata(
    *,
    year: int,
    input_root: str | Path,
    labels_master: str | Path,
    historical_held_out: str | Path,
) -> dict[str, Any]:
    sentence_table = Path(input_root) / f"year={year}" / "ai_sentences.parquet"
    return {
        "year": int(year),
        "sentence_table": _file_fingerprint(sentence_table),
        "labels_master_sha256": _sha256_file(labels_master),
        "historical_held_out_sha256": _sha256_file(historical_held_out),
    }


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _build_progress_payload(
    *,
    years_requested: list[int],
    years_completed: list[int],
    current_year: int | None,
    year_state: dict[str, Any],
    cache_dir: Path,
    output_csv: str,
    output_xlsx: str,
    output_report: str,
    status: str,
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
            "cache_dir": str(cache_dir),
        },
        "years": year_state,
        "outputs": {
            "candidate_csv": str(output_csv),
            "review_xlsx": str(output_xlsx),
            "report_json": str(output_report),
        },
    }


def _write_progress(
    *,
    progress_path: Path,
    years_requested: list[int],
    years_completed: list[int],
    current_year: int | None,
    year_state: dict[str, Any],
    cache_dir: Path,
    output_csv: str,
    output_xlsx: str,
    output_report: str,
    status: str,
) -> None:
    payload = _build_progress_payload(
        years_requested=years_requested,
        years_completed=years_completed,
        current_year=current_year,
        year_state=year_state,
        cache_dir=cache_dir,
        output_csv=output_csv,
        output_xlsx=output_xlsx,
        output_report=output_report,
        status=status,
    )
    _dump_json(progress_path, payload)


def _predict_year(
    *,
    input_root: str | Path,
    year: int,
    exclusions: set[str],
    legacy_runtime: dict[str, Any],
    batch_size: int,
    progress_path: Path,
    years_requested: list[int],
    years_completed: list[int],
    year_state: dict[str, Any],
    cache_dir: Path,
    output_csv: str,
    output_xlsx: str,
    output_report: str,
) -> pd.DataFrame:
    frame = load_sentence_pool(input_root, [year])
    eligible = frame[~frame["sentence_norm"].isin(exclusions)].copy()
    eligible = eligible.sort_values(["source_year", "source_cik", "sentence_id"]).reset_index(
        drop=True
    )

    total_rows = int(len(eligible))
    year_state[str(year)] = {
        "status": "running",
        "rows_total": total_rows,
        "rows_processed": 0,
        "candidate_label_counts": {label: 0 for label in LABELS},
    }
    _write_progress(
        progress_path=progress_path,
        years_requested=years_requested,
        years_completed=years_completed,
        current_year=year,
        year_state=year_state,
        cache_dir=cache_dir,
        output_csv=output_csv,
        output_xlsx=output_xlsx,
        output_report=output_report,
        status="running",
    )

    if eligible.empty:
        year_state[str(year)] = {
            "status": "completed",
            "rows_total": 0,
            "rows_processed": 0,
            "candidate_label_counts": {label: 0 for label in LABELS},
        }
        return eligible

    predicted: list[str] = []
    for start in range(0, total_rows, batch_size):
        stop = min(start + batch_size, total_rows)
        labels, _scores = predict_sentences(
            eligible.iloc[start:stop]["sentence"].astype(str).tolist(),
            legacy_runtime,
        )
        predicted.extend(labels)
        partial = pd.Series(predicted).value_counts().to_dict()
        year_state[str(year)] = {
            "status": "running",
            "rows_total": total_rows,
            "rows_processed": stop,
            "candidate_label_counts": {label: int(partial.get(label, 0)) for label in LABELS},
        }
        _write_progress(
            progress_path=progress_path,
            years_requested=years_requested,
            years_completed=years_completed,
            current_year=year,
            year_state=year_state,
            cache_dir=cache_dir,
            output_csv=output_csv,
            output_xlsx=output_xlsx,
            output_report=output_report,
            status="running",
        )

    eligible["candidate_label"] = predicted
    counts = eligible["candidate_label"].value_counts().to_dict()
    year_state[str(year)] = {
        "status": "completed",
        "rows_total": total_rows,
        "rows_processed": total_rows,
        "candidate_label_counts": {label: int(counts.get(label, 0)) for label in LABELS},
    }
    return eligible


def run_sampling_restartable(args: argparse.Namespace) -> dict[str, Any]:
    years = [int(value) for value in args.years]
    exclusions = load_exclusions(args.labels_master, args.historical_held_out)
    cache_dir = Path(args.cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    progress_path = Path(args.progress_report)
    years_completed: list[int] = []
    year_state: dict[str, Any] = {}
    legacy_runtime = build_legacy_two_stage_runtime()

    cached_frames: list[pd.DataFrame] = []
    _write_progress(
        progress_path=progress_path,
        years_requested=years,
        years_completed=years_completed,
        current_year=None,
        year_state=year_state,
        cache_dir=cache_dir,
        output_csv=args.output_csv,
        output_xlsx=args.output_xlsx,
        output_report=args.output_report,
        status="starting",
    )

    try:
        for year in years:
            cache_path = cache_dir / f"year={year}_candidate_pool.parquet"
            meta_path = cache_dir / f"year={year}_candidate_pool.meta.json"
            cache_meta = _cache_metadata(
                year=year,
                input_root=args.input_root,
                labels_master=args.labels_master,
                historical_held_out=args.historical_held_out,
            )
            if (
                cache_path.exists()
                and meta_path.exists()
                and not args.force_recompute
                and _load_json(meta_path) == cache_meta
            ):
                cached = pd.read_parquet(cache_path)
                cached_frames.append(cached)
                years_completed.append(year)
                counts = (
                    cached["candidate_label"].value_counts().to_dict()
                    if not cached.empty
                    else {}
                )
                year_state[str(year)] = {
                    "status": "reused",
                    "rows_total": int(len(cached)),
                    "rows_processed": int(len(cached)),
                    "candidate_label_counts": {
                        label: int(counts.get(label, 0)) for label in LABELS
                    },
                    "cache_path": str(cache_path),
                }
                _write_progress(
                    progress_path=progress_path,
                    years_requested=years,
                    years_completed=years_completed,
                    current_year=None,
                    year_state=year_state,
                    cache_dir=cache_dir,
                    output_csv=args.output_csv,
                    output_xlsx=args.output_xlsx,
                    output_report=args.output_report,
                    status="running",
                )
                continue

            year_candidates = _predict_year(
                input_root=args.input_root,
                year=year,
                exclusions=exclusions,
                legacy_runtime=legacy_runtime,
                batch_size=int(args.batch_size),
                progress_path=progress_path,
                years_requested=years,
                years_completed=years_completed,
                year_state=year_state,
                cache_dir=cache_dir,
                output_csv=args.output_csv,
                output_xlsx=args.output_xlsx,
                output_report=args.output_report,
            )
            year_candidates.to_parquet(cache_path, index=False)
            _dump_json(meta_path, cache_meta)
            year_state[str(year)]["cache_path"] = str(cache_path)
            year_state[str(year)]["cache_meta_path"] = str(meta_path)
            cached_frames.append(year_candidates)
            years_completed.append(year)
            _write_progress(
                progress_path=progress_path,
                years_requested=years,
                years_completed=years_completed,
                current_year=None,
                year_state=year_state,
                cache_dir=cache_dir,
                output_csv=args.output_csv,
                output_xlsx=args.output_xlsx,
                output_report=args.output_report,
                status="running",
            )

        combined = pd.concat(cached_frames, ignore_index=True)
        selected = select_candidate_review_rows(combined)
        report = write_review_package(
            selected=selected,
            years=years,
            output_csv=args.output_csv,
            output_xlsx=args.output_xlsx,
            output_report=args.output_report,
        )
        final_progress = _build_progress_payload(
            years_requested=years,
            years_completed=years_completed,
            current_year=None,
            year_state=year_state,
            cache_dir=cache_dir,
            output_csv=args.output_csv,
            output_xlsx=args.output_xlsx,
            output_report=args.output_report,
            status="completed",
        )
        final_progress["final_report"] = report
        _dump_json(progress_path, final_progress)
        return report
    except Exception as exc:
        failed = _build_progress_payload(
            years_requested=years,
            years_completed=years_completed,
            current_year=None,
            year_state=year_state,
            cache_dir=cache_dir,
            output_csv=args.output_csv,
            output_xlsx=args.output_xlsx,
            output_report=args.output_report,
            status="failed",
        )
        failed["error"] = str(exc)
        _dump_json(progress_path, failed)
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", default="data/processed/sentences")
    parser.add_argument("--years", nargs="+", default=[str(year) for year in DEFAULT_YEARS])
    parser.add_argument("--labels-master", default="data/labels/v1/labels_master.parquet")
    parser.add_argument("--historical-held-out", default="data/validation/held_out_sentences.csv")
    parser.add_argument(
        "--output-csv", default="data/validation/held_out_sentences_v2_review_sheet.csv"
    )
    parser.add_argument(
        "--output-xlsx", default="data/validation/held_out_sentences_v2_review_sheet.xlsx"
    )
    parser.add_argument(
        "--output-report", default="reports/validation/held_out_v2_sampling_report.json"
    )
    parser.add_argument(
        "--progress-report",
        default="reports/validation/held_out_v2_sampling_progress.json",
    )
    parser.add_argument(
        "--cache-dir",
        default="reports/validation/held_out_v2_cache",
    )
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument(
        "--force-recompute",
        action="store_true",
        help="Ignore any cached per-year candidate pools and recompute them.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_sampling_restartable(args)
    print(
        "[heldout-v2-restartable] "
        f"status={report['status']} rows={report['summary']['rows_selected']}"
    )
    print(f"[heldout-v2-restartable] review sheet -> {args.output_xlsx}")
    print(f"[heldout-v2-restartable] progress -> {args.progress_report}")


if __name__ == "__main__":
    main()
