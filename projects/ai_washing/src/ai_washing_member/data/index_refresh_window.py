"""Index a bounded annual refresh source window without touching legacy contracts."""

from __future__ import annotations

import argparse
from typing import Any

from ai_washing_member.data.index_sec_filings import (
    SOURCE_ROOT_REF,
    build_index_rows,
    dump_json,
    resolve_sec_source,
    write_index_csv,
)

DEFAULT_SOURCE_WINDOW_ID = "annual_10k_2025_refresh_v1"
DEFAULT_YEARS = (2025,)
DEFAULT_FORMS = ("10-K", "10-K-A")
DEFAULT_OUTPUT_CSV = "data/metadata/available_filings_index_2025_refresh_v1.csv"
DEFAULT_OUTPUT_SOURCE_WINDOWS = "data/metadata/source_windows_2025_refresh_v1.json"
DEFAULT_OUTPUT_SUMMARY = "reports/data/source_index_summary_2025_refresh_v1.json"


def _build_refresh_source_windows(
    *,
    source_root_name: str,
    source_window_id: str,
    years: list[int],
    indexed_years: list[int],
    filing_count: int,
) -> dict[str, Any]:
    missing_years = [year for year in years if year not in indexed_years]
    return {
        "generated_at": _now_utc(),
        "source_root_ref": SOURCE_ROOT_REF,
        "source_root_name": source_root_name,
        "all_indexed_years": indexed_years,
        "windows": [
            {
                "source_window_id": str(source_window_id),
                "roadmap_status": "active_refresh",
                "expected_years": years,
                "indexed_years": indexed_years,
                "missing_years": missing_years,
                "availability_status": "complete" if not missing_years else "incomplete",
                "filing_count": int(filing_count),
                "form_policy": list(DEFAULT_FORMS),
            }
        ],
    }


def _now_utc() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def _build_summary(
    *,
    rows: list[dict[str, Any]],
    source_root_name: str,
    output_csv: str,
    source_window_id: str,
    form_filter: list[str],
    scan_meta: dict[str, Any],
) -> dict[str, Any]:
    form_counts: dict[str, int] = {}
    quarter_counts: dict[str, int] = {}
    year_counts: dict[str, int] = {}
    for row in rows:
        form = str(row["form"])
        year = int(row["year"])
        quarter = int(row["quarter"])
        form_counts[form] = form_counts.get(form, 0) + 1
        year_counts[str(year)] = year_counts.get(str(year), 0) + 1
        quarter_key = f"{year}:Q{quarter}"
        quarter_counts[quarter_key] = quarter_counts.get(quarter_key, 0) + 1

    return {
        "generated_at": _now_utc(),
        "source_root_ref": SOURCE_ROOT_REF,
        "source_root_name": source_root_name,
        "output_csv": output_csv,
        "source_window_id": str(source_window_id),
        "form_filter": list(form_filter),
        "scanned_file_count": int(scan_meta.get("scanned_count", 0)),
        "indexed_row_count": int(len(rows)),
        "unmatched_file_count": int(scan_meta.get("unmatched_count", 0)),
        "sample_unmatched_files": list(scan_meta.get("unmatched_files", [])),
        "year_counts": dict(sorted(year_counts.items())),
        "form_counts": dict(sorted(form_counts.items())),
        "quarter_counts": dict(sorted(quarter_counts.items())),
    }


def run_refresh_index(args: argparse.Namespace) -> dict[str, Any]:
    source_root = resolve_sec_source(source_root=args.source_root, hint_file=args.source_root_hint)
    rows, scan_meta = build_index_rows(source_root)

    allowed_years = {int(year) for year in args.years}
    allowed_forms = {str(form).upper() for form in args.forms}

    filtered_rows = [
        {
            **row,
            "source_window_id": str(args.source_window_id),
        }
        for row in rows
        if int(row["year"]) in allowed_years and str(row["form"]).upper() in allowed_forms
    ]

    filtered_rows.sort(
        key=lambda row: (
            int(row["year"]),
            int(row["quarter"]),
            str(row["form"]),
            str(row["cik"]),
            str(row["filename"]),
        )
    )

    indexed_years = sorted({int(row["year"]) for row in filtered_rows})
    source_windows = _build_refresh_source_windows(
        source_root_name=source_root.name,
        source_window_id=args.source_window_id,
        years=[int(year) for year in args.years],
        indexed_years=indexed_years,
        filing_count=len(filtered_rows),
    )
    summary = _build_summary(
        rows=filtered_rows,
        source_root_name=source_root.name,
        output_csv=args.output_csv,
        source_window_id=args.source_window_id,
        form_filter=sorted(allowed_forms),
        scan_meta=scan_meta,
    )

    write_index_csv(filtered_rows, args.output_csv)
    dump_json(args.output_source_windows, source_windows)
    dump_json(args.output_summary, summary)

    return {
        "status": "indexed",
        "source_root": str(source_root),
        "source_root_name": source_root.name,
        "source_window_id": str(args.source_window_id),
        "years": [int(year) for year in args.years],
        "forms": sorted(allowed_forms),
        "indexed_row_count": len(filtered_rows),
        "output_csv": str(args.output_csv),
        "output_source_windows": str(args.output_source_windows),
        "output_summary": str(args.output_summary),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", default="")
    parser.add_argument("--source-root-hint", default="")
    parser.add_argument("--source-window-id", default=DEFAULT_SOURCE_WINDOW_ID)
    parser.add_argument("--years", nargs="+", type=int, default=list(DEFAULT_YEARS))
    parser.add_argument("--forms", nargs="+", default=list(DEFAULT_FORMS))
    parser.add_argument("--output-csv", default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-source-windows", default=DEFAULT_OUTPUT_SOURCE_WINDOWS)
    parser.add_argument("--output-summary", default=DEFAULT_OUTPUT_SUMMARY)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_refresh_index(args)
    print(
        "[refresh-index] indexed "
        f"rows={report['indexed_row_count']} window={report['source_window_id']}"
    )
    print(f"[refresh-index] output_csv -> {report['output_csv']}")


if __name__ == "__main__":
    main()
