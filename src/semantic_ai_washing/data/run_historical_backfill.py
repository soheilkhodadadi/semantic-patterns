"""Restartable historical SEC indexing with progress logging and optional materialization."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pandas as pd

from semantic_ai_washing.data.index_sec_filings import (
    HISTORICAL_SOURCE_WINDOW_ID,
    QTR_DIR_RE,
    build_source_windows,
    build_summary_report,
    dump_json,
    parse_filename,
    resolve_sec_source,
    write_index_csv,
)
from semantic_ai_washing.data.materialize_active_window_sentences import run_materialization

DEFAULT_YEARS = (2016, 2017, 2018, 2019, 2020)
DEFAULT_FORMS = ("10-K",)


def _now_utc() -> str:
    return pd.Timestamp.utcnow().isoformat()


def _write_progress(path: str | Path, payload: dict[str, Any]) -> None:
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _year_cache_metadata(*, root: Path, year: int, forms: set[str]) -> dict[str, Any]:
    year_dir = root / str(year)
    year_dir_exists = year_dir.exists()
    year_dir_mtime_ns = int(year_dir.stat().st_mtime_ns) if year_dir_exists else None
    return {
        "source_root": str(root.resolve()),
        "year": int(year),
        "forms": sorted(forms),
        "year_dir_exists": bool(year_dir_exists),
        "year_dir_mtime_ns": year_dir_mtime_ns,
    }


def _scan_year(
    *,
    root: Path,
    year: int,
    forms: set[str],
    progress_path: Path,
    years_requested: list[int],
    years_completed: list[int],
    year_state: dict[str, Any],
    current_quarter: str | None,
    output_csv: str,
) -> list[dict[str, Any]]:
    year_dir = root / str(year)
    if not year_dir.exists():
        year_state[str(year)] = {
            "status": "missing_year_directory",
            "rows_indexed": 0,
            "files_scanned": 0,
            "current_quarter": None,
        }
        return []

    rows: list[dict[str, Any]] = []
    files_scanned = 0
    unmatched = 0
    for quarter_dir in sorted(year_dir.iterdir()):
        quarter_match = QTR_DIR_RE.match(quarter_dir.name)
        if not quarter_dir.is_dir() or quarter_match is None:
            continue
        current_quarter = quarter_dir.name.upper()
        for filing_path in sorted(path for path in quarter_dir.glob("*.txt") if path.is_file()):
            files_scanned += 1
            parsed = parse_filename(filing_path)
            if parsed is None:
                unmatched += 1
                continue
            form = str(parsed["form"]).upper()
            if form not in forms:
                continue
            rows.append(
                {
                    "cik": parsed["cik"],
                    "year": parsed["year"],
                    "quarter": parsed["quarter"],
                    "form": form,
                    "filename": parsed["filename"],
                    "path": filing_path.relative_to(root).as_posix(),
                    "source_root": "env:SEC_SOURCE_DIR",
                    "index_timestamp": _now_utc(),
                    "source_window_id": HISTORICAL_SOURCE_WINDOW_ID,
                }
            )
        year_state[str(year)] = {
            "status": "running",
            "rows_indexed": len(rows),
            "files_scanned": files_scanned,
            "unmatched_files": unmatched,
            "current_quarter": current_quarter,
        }
        _write_progress(
            progress_path,
            {
                "status": "running",
                "generated_at_utc": _now_utc(),
                "summary": {
                    "status": "running",
                    "years_requested": years_requested,
                    "years_completed": years_completed,
                    "current_year": year,
                    "current_quarter": current_quarter,
                    "output_csv": output_csv,
                },
                "years": year_state,
            },
        )
    year_state[str(year)] = {
        "status": "completed",
        "rows_indexed": len(rows),
        "files_scanned": files_scanned,
        "unmatched_files": unmatched,
        "current_quarter": current_quarter,
    }
    return rows


def _write_year_cache(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "cik",
        "year",
        "quarter",
        "form",
        "filename",
        "path",
        "source_root",
        "index_timestamp",
        "source_window_id",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _load_rows_from_cache(path: Path) -> list[dict[str, Any]]:
    frame = pd.read_csv(path, dtype={"cik": str, "form": str, "path": str})
    return frame.to_dict(orient="records")


def _materialize_years(
    *,
    index_csv: str,
    source_root: str,
    source_windows_json: str,
    index_summary_json: str,
    output_root: str,
    keywords_path: str,
    min_tokens: int,
    max_tokens: int,
    sample_size: int,
    source_window_id: str,
    years: list[int],
    report_template: str,
    progress_path: Path,
    base_progress: dict[str, Any],
) -> None:
    for year in years:
        report_path = report_template.format(year=year)
        args = SimpleNamespace(
            index_csv=index_csv,
            source_root=source_root,
            source_root_hint="",
            source_windows_json=source_windows_json,
            index_summary_json=index_summary_json,
            source_window_id=source_window_id,
            years=[str(year)],
            output_root=output_root,
            output_report=report_path,
            keywords_path=keywords_path,
            min_tokens=min_tokens,
            max_tokens=max_tokens,
            sample_size=sample_size,
            refresh_index_if_missing_or_empty=False,
        )
        progress = dict(base_progress)
        progress["materialization"] = {
            "status": "running",
            "current_year": year,
            "report_path": report_path,
        }
        _write_progress(progress_path, progress)
        run_materialization(args)
        progress["materialization"] = {
            "status": "completed",
            "current_year": year,
            "report_path": report_path,
        }
        _write_progress(progress_path, progress)


def run_backfill(args: argparse.Namespace) -> dict[str, Any]:
    years = [int(value) for value in args.years]
    materialize_years = [int(value) for value in args.materialize_years]
    root = resolve_sec_source(source_root=args.source_root, hint_file=args.source_root_hint)
    if not root.exists():
        raise FileNotFoundError(f"Source directory not found: {root}")

    forms = {value.upper() for value in args.forms}
    cache_dir = Path(args.cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    progress_path = Path(args.progress_report)
    year_state: dict[str, Any] = {}
    years_completed: list[int] = []
    all_rows: list[dict[str, Any]] = []
    missing_years: list[int] = []

    _write_progress(
        progress_path,
        {
            "status": "starting",
            "generated_at_utc": _now_utc(),
            "summary": {
                "status": "starting",
                "years_requested": years,
                "years_completed": years_completed,
                "current_year": None,
                "current_quarter": None,
                "output_csv": args.output_csv,
            },
            "years": year_state,
        },
    )

    try:
        for year in years:
            cache_path = cache_dir / f"year={year}_index.csv"
            meta_path = cache_dir / f"year={year}_index.meta.json"
            cache_meta = _year_cache_metadata(root=root, year=year, forms=forms)
            if (
                cache_path.exists()
                and meta_path.exists()
                and not args.force_recompute
                and _load_json(meta_path) == cache_meta
            ):
                rows = _load_rows_from_cache(cache_path)
                all_rows.extend(rows)
                years_completed.append(year)
                year_state[str(year)] = {
                    "status": "reused",
                    "rows_indexed": len(rows),
                    "files_scanned": None,
                    "unmatched_files": None,
                    "cache_path": str(cache_path),
                    "cache_meta_path": str(meta_path),
                }
                _write_progress(
                    progress_path,
                    {
                        "status": "running",
                        "generated_at_utc": _now_utc(),
                        "summary": {
                            "status": "running",
                            "years_requested": years,
                            "years_completed": years_completed,
                            "current_year": None,
                            "current_quarter": None,
                            "output_csv": args.output_csv,
                        },
                        "years": year_state,
                    },
                )
                continue

            rows = _scan_year(
                root=root,
                year=year,
                forms=forms,
                progress_path=progress_path,
                years_requested=years,
                years_completed=years_completed,
                year_state=year_state,
                current_quarter=None,
                output_csv=args.output_csv,
            )
            if year_state.get(str(year), {}).get("status") == "missing_year_directory":
                missing_years.append(year)
                continue
            _write_year_cache(cache_path, rows)
            _write_progress(
                progress_path,
                {
                    "status": "running",
                    "generated_at_utc": _now_utc(),
                    "summary": {
                        "status": "running",
                        "years_requested": years,
                        "years_completed": years_completed,
                        "current_year": year,
                        "current_quarter": None,
                        "output_csv": args.output_csv,
                    },
                    "years": year_state,
                },
            )
            dump_json(meta_path, cache_meta)
            year_state[str(year)]["cache_path"] = str(cache_path)
            year_state[str(year)]["cache_meta_path"] = str(meta_path)
            all_rows.extend(rows)
            years_completed.append(year)
            _write_progress(
                progress_path,
                {
                    "status": "running",
                    "generated_at_utc": _now_utc(),
                    "summary": {
                        "status": "running",
                        "years_requested": years,
                        "years_completed": years_completed,
                        "current_year": None,
                        "current_quarter": None,
                        "output_csv": args.output_csv,
                    },
                    "years": year_state,
                },
            )

        all_rows.sort(
            key=lambda row: (
                int(row["year"]),
                int(row["quarter"]) if row.get("quarter") is not None else 0,
                str(row["form"]),
                str(row["cik"]),
                str(row["filename"]),
            )
        )
        write_index_csv(all_rows, args.output_csv)
        source_windows = build_source_windows(all_rows, source_root_name=root.name)
        summary = build_summary_report(
            all_rows,
            scan_meta={
                "scanned_count": sum(
                    int(state.get("files_scanned") or 0) for state in year_state.values()
                ),
                "unmatched_count": sum(
                    int(state.get("unmatched_files") or 0) for state in year_state.values()
                ),
                "unmatched_files": [],
            },
            source_windows=source_windows,
            source_root_name=root.name,
            output_csv=args.output_csv,
        )
        dump_json(args.output_source_windows, source_windows)
        dump_json(args.output_summary, summary)

        base_progress = {
            "status": "indexed" if not missing_years else "failed",
            "generated_at_utc": _now_utc(),
            "summary": {
                "status": "indexed" if not missing_years else "failed",
                "years_requested": years,
                "years_completed": years_completed,
                "missing_years": missing_years,
                "current_year": None,
                "current_quarter": None,
                "output_csv": args.output_csv,
                "indexed_row_count": len(all_rows),
            },
            "years": year_state,
        }
        _write_progress(progress_path, base_progress)

        if materialize_years:
            _materialize_years(
                index_csv=args.output_csv,
                source_root=str(root),
                source_windows_json=args.output_source_windows,
                index_summary_json=args.output_summary,
                output_root=args.output_root,
                keywords_path=args.keywords_path,
                min_tokens=int(args.min_tokens),
                max_tokens=int(args.max_tokens),
                sample_size=int(args.sample_size),
                source_window_id=HISTORICAL_SOURCE_WINDOW_ID,
                years=materialize_years,
                report_template=args.materialization_report_template,
                progress_path=progress_path,
                base_progress=base_progress,
            )

        final_report = {
            "status": "completed" if not missing_years else "failed",
            "generated_at_utc": _now_utc(),
            "summary": {
                "status": "completed" if not missing_years else "failed",
                "years_requested": years,
                "years_completed": years_completed,
                "missing_years": missing_years,
                "forms": sorted(forms),
                "indexed_row_count": len(all_rows),
                "materialize_years": materialize_years,
            },
            "outputs": {
                "index_csv": args.output_csv,
                "source_windows_json": args.output_source_windows,
                "summary_json": args.output_summary,
                "progress_json": str(progress_path),
            },
            "years": year_state,
        }
        _write_progress(progress_path, final_report)
        return final_report
    except Exception as exc:
        _write_progress(
            progress_path,
            {
                "status": "failed",
                "generated_at_utc": _now_utc(),
                "summary": {
                    "status": "failed",
                    "years_requested": years,
                    "years_completed": years_completed,
                    "current_year": None,
                    "current_quarter": None,
                    "output_csv": args.output_csv,
                },
                "years": year_state,
                "error": str(exc),
            },
        )
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--source-root-hint", default="")
    parser.add_argument("--years", nargs="+", default=[str(year) for year in DEFAULT_YEARS])
    parser.add_argument("--forms", nargs="+", default=list(DEFAULT_FORMS))
    parser.add_argument(
        "--output-csv", default="data/metadata/available_filings_index_2016_2020.csv"
    )
    parser.add_argument(
        "--output-source-windows", default="data/metadata/source_windows_2016_2020.json"
    )
    parser.add_argument(
        "--output-summary", default="reports/data/source_index_summary_2016_2020.json"
    )
    parser.add_argument(
        "--progress-report", default="reports/data/source_index_progress_2016_2020.json"
    )
    parser.add_argument(
        "--cache-dir", default="reports/data/source_index_cache_2016_2020"
    )
    parser.add_argument("--materialize-years", nargs="*", default=[])
    parser.add_argument("--output-root", default="data/processed/sentences")
    parser.add_argument("--keywords-path", default="data/metadata/ai_keywords.txt")
    parser.add_argument("--min-tokens", type=int, default=6)
    parser.add_argument("--max-tokens", type=int, default=120)
    parser.add_argument("--sample-size", type=int, default=200)
    parser.add_argument(
        "--materialization-report-template",
        default="reports/data/historical_backfill_sentence_inventory_{year}_v1.json",
    )
    parser.add_argument(
        "--force-recompute",
        action="store_true",
        help="Ignore any cached per-year index outputs and rebuild them.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_backfill(args)
    print(f"[historical-backfill] status={report['status']}")
    print(f"[historical-backfill] years={report['summary']['years_completed']}")
    print(f"[historical-backfill] progress -> {args.progress_report}")


if __name__ == "__main__":
    main()
