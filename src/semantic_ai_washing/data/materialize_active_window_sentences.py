"""Materialize canonical AI sentence tables for the active 2021-2024 source window."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd

from semantic_ai_washing.data.extract_sentence_table import extract_sentence_table
from semantic_ai_washing.data.index_sec_filings import (
    OUTPUT_SOURCE_WINDOWS,
    OUTPUT_SUMMARY,
    build_index_rows,
    build_source_windows,
    build_summary_report,
    dump_json,
    resolve_sec_source,
    write_index_csv,
)
from semantic_ai_washing.labeling.common import row_sha256

DEFAULT_YEARS = (2021, 2022, 2023, 2024)


def _load_prior_inventory(path: str | Path) -> dict[str, Any]:
    resolved = Path(path)
    if not resolved.exists():
        return {}
    return json.loads(resolved.read_text(encoding="utf-8"))


def _manifest_hash(frame: pd.DataFrame) -> str:
    ordered = frame.sort_values(["year", "quarter", "form", "cik", "filename"]).reset_index(
        drop=True
    )
    rows = ordered.astype(str).agg("|".join, axis=1).tolist()
    return row_sha256(rows)


def _load_or_refresh_index(args: argparse.Namespace) -> tuple[pd.DataFrame, bool, dict[str, Any]]:
    index_path = Path(args.index_csv)
    index_refresh_performed = False
    metadata: dict[str, Any] = {}

    if index_path.exists() and index_path.stat().st_size > 0:
        frame = pd.read_csv(index_path, dtype={"cik": str, "form": str, "path": str})
        if not frame.empty:
            metadata["index_row_count"] = int(len(frame))
            return frame, index_refresh_performed, metadata

    if not args.refresh_index_if_missing_or_empty:
        raise ValueError(
            "Filings index is missing or empty and refresh is disabled. Run the SEC indexer first."
        )

    source_root = resolve_sec_source(source_root=args.source_root, hint_file=args.source_root_hint)
    rows, scan_meta = build_index_rows(source_root)
    source_windows = build_source_windows(rows, source_root_name=source_root.name)
    summary = build_summary_report(
        rows,
        scan_meta=scan_meta,
        source_windows=source_windows,
        source_root_name=source_root.name,
        output_csv=args.index_csv,
    )
    write_index_csv(rows, args.index_csv)
    dump_json(args.source_windows_json, source_windows)
    dump_json(args.index_summary_json, summary)
    index_refresh_performed = True
    metadata.update(
        {
            "index_row_count": int(len(rows)),
            "source_root": str(source_root),
            "source_root_name": source_root.name,
        }
    )
    return pd.DataFrame(rows), index_refresh_performed, metadata


def _build_year_manifest(
    index_frame: pd.DataFrame, year: int, source_window_id: str
) -> pd.DataFrame:
    scoped = index_frame.loc[
        (index_frame["source_window_id"].astype(str) == str(source_window_id))
        & (index_frame["year"].astype(int) == int(year))
    ].copy()
    if scoped.empty:
        return scoped
    scoped["manifest_id"] = f"active_window_{year}_v1"
    scoped["source_window_id"] = str(source_window_id)
    return scoped[
        ["cik", "year", "quarter", "form", "filename", "path", "manifest_id", "source_window_id"]
    ]


def run_materialization(args: argparse.Namespace) -> dict[str, Any]:
    years = [int(year) for year in args.years]
    output_root = Path(args.output_root)
    inventory_path = Path(args.output_report)
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    output_root.mkdir(parents=True, exist_ok=True)

    index_frame, index_refresh_performed, index_meta = _load_or_refresh_index(args)
    prior_inventory = _load_prior_inventory(inventory_path)
    prior_years = (prior_inventory.get("years") or {}) if isinstance(prior_inventory, dict) else {}

    years_payload: dict[str, Any] = {}
    rows_by_year: dict[str, int] = {}
    years_completed: list[int] = []
    years_reused: list[int] = []
    years_materialized: list[int] = []
    missing_years: list[int] = []

    for year in years:
        manifest = _build_year_manifest(index_frame, year, args.source_window_id)
        manifest_hash = _manifest_hash(manifest) if not manifest.empty else ""
        output_path = output_root / f"year={year}" / "ai_sentences.parquet"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        prior_entry = prior_years.get(str(year), {}) if isinstance(prior_years, dict) else {}
        can_reuse = bool(
            output_path.exists()
            and prior_entry
            and prior_entry.get("manifest_hash", "") == manifest_hash
            and prior_entry.get("output_sha256", "")
        )

        if manifest.empty:
            missing_years.append(year)
            years_payload[str(year)] = {
                "status": "missing_index_rows",
                "manifest_hash": manifest_hash,
                "output_path": str(output_path),
                "reused": False,
                "row_count": 0,
            }
            continue

        if can_reuse:
            row_count = int(len(pd.read_parquet(output_path)))
            years_completed.append(year)
            years_reused.append(year)
            rows_by_year[str(year)] = row_count
            years_payload[str(year)] = {
                "status": "reused",
                "manifest_hash": manifest_hash,
                "output_path": str(output_path),
                "output_sha256": prior_entry.get("output_sha256", ""),
                "reused": True,
                "row_count": row_count,
            }
            continue

        with tempfile.TemporaryDirectory(prefix=f"active_window_{year}_") as tmp_dir:
            tmp_path = Path(tmp_dir)
            manifest_path = tmp_path / f"manifest_{year}.csv"
            sample_path = tmp_path / f"sample_{year}.csv"
            report_path = tmp_path / f"report_{year}.json"
            manifest.to_csv(manifest_path, index=False)
            extract_sentence_table(
                manifest_path=str(manifest_path),
                output_path=str(output_path),
                sample_output_path=str(sample_path),
                report_path=str(report_path),
                source_root=args.source_root,
                keywords_path=args.keywords_path,
                min_tokens=int(args.min_tokens),
                max_tokens=int(args.max_tokens),
                segmentation_mode=str(getattr(args, "segmentation_mode", "default")),
                sample_size=int(args.sample_size),
            )

        row_count = int(len(pd.read_parquet(output_path)))
        years_completed.append(year)
        years_materialized.append(year)
        rows_by_year[str(year)] = row_count
        years_payload[str(year)] = {
            "status": "materialized",
            "manifest_hash": manifest_hash,
            "output_path": str(output_path),
            "output_sha256": _sha256_file(output_path),
            "reused": False,
            "row_count": row_count,
        }

    status = "passed" if not missing_years and len(years_completed) == len(years) else "failed"
    report = {
        "status": status,
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "summary": {
            "status": status,
            "source_window_id": str(args.source_window_id),
            "years_requested": years,
            "years_completed": years_completed,
            "years_reused": years_reused,
            "years_materialized": years_materialized,
            "completed_year_count": len(years_completed),
            "missing_years": missing_years,
            "missing_year_count": len(missing_years),
            "rows_by_year": rows_by_year,
            "index_refresh_performed": index_refresh_performed,
            "index_row_count": int(index_meta.get("index_row_count", len(index_frame))),
            "source_root": index_meta.get("source_root", args.source_root or ""),
            "source_root_name": index_meta.get("source_root_name", ""),
            "output_root": str(output_root),
        },
        "years": years_payload,
        "inputs": {
            "index_csv": args.index_csv,
            "source_root_hint": args.source_root_hint,
            "keywords_path": args.keywords_path,
            "max_tokens": int(args.max_tokens),
            "segmentation_mode": str(getattr(args, "segmentation_mode", "default")),
        },
    }
    inventory_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if status != "passed":
        raise SystemExit(
            "Active-window sentence materialization did not cover every requested year."
        )
    return report


def _sha256_file(path: str | Path) -> str:
    resolved = Path(path)
    import hashlib

    hasher = hashlib.sha256()
    with resolved.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index-csv", default="data/metadata/available_filings_index.csv")
    parser.add_argument("--source-root", default="")
    parser.add_argument("--source-root-hint", default="data/metadata/sec_source_dir.txt")
    parser.add_argument("--source-windows-json", default=OUTPUT_SOURCE_WINDOWS)
    parser.add_argument("--index-summary-json", default=OUTPUT_SUMMARY)
    parser.add_argument("--source-window-id", default="active_2021_2024")
    parser.add_argument("--years", nargs="+", default=[str(year) for year in DEFAULT_YEARS])
    parser.add_argument("--output-root", default="data/processed/sentences")
    parser.add_argument(
        "--output-report", default="reports/data/active_window_sentence_inventory_v1.json"
    )
    parser.add_argument("--keywords-path", default="data/metadata/ai_keywords.txt")
    parser.add_argument("--min-tokens", type=int, default=6)
    parser.add_argument("--max-tokens", type=int, default=120)
    parser.add_argument(
        "--segmentation-mode",
        choices=["default", "fast"],
        default="default",
    )
    parser.add_argument("--sample-size", type=int, default=200)
    parser.add_argument(
        "--refresh-index-if-missing-or-empty",
        dest="refresh_index_if_missing_or_empty",
        action="store_true",
    )
    parser.add_argument(
        "--no-refresh-index-if-missing-or-empty",
        dest="refresh_index_if_missing_or_empty",
        action="store_false",
    )
    parser.set_defaults(refresh_index_if_missing_or_empty=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_materialization(args)
    print(
        "[sentences] active window materialized "
        f"years={report['summary']['years_completed']} "
        f"reused={report['summary']['years_reused']}"
    )
    print(f"[sentences] inventory -> {args.output_report}")


if __name__ == "__main__":
    main()
