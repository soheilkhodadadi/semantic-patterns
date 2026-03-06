"""Index the external SEC corpus and emit source-window metadata."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Optional

SEC_SOURCE_HINT_FILE = "data/metadata/sec_source_dir.txt"
OUTPUT_CSV = "data/metadata/available_filings_index.csv"
OUTPUT_SOURCE_WINDOWS = "data/metadata/source_windows.json"
OUTPUT_SUMMARY = "reports/data/source_index_summary.json"

ACTIVE_SOURCE_WINDOW_ID = "active_2021_2024"
HISTORICAL_SOURCE_WINDOW_ID = "historical_2000_2020"
SOURCE_ROOT_REF = "env:SEC_SOURCE_DIR"
ACTIVE_YEARS = ("2021", "2022", "2023", "2024")

YEAR_DIR_RE = re.compile(r"^\d{4}$")
QTR_DIR_RE = re.compile(r"^QTR(?P<quarter>[1-4])$", re.IGNORECASE)
FNAME_RE = re.compile(
    r"^(?P<date>\d{8})_(?P<form>10-[KQ](?:-A)?)_edgar_data_(?P<cik>\d+)_.*\.txt$",
    re.IGNORECASE,
)


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def dump_json(path: str | Path, payload: Any) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=False), encoding="utf-8")


def resolve_sec_source(source_root: str = "", hint_file: str = SEC_SOURCE_HINT_FILE) -> Path:
    if source_root:
        return Path(source_root).expanduser().resolve()

    env_value = os.environ.get("SEC_SOURCE_DIR", "").strip()
    if env_value:
        return Path(env_value).expanduser().resolve()

    hint_path = Path(hint_file)
    if hint_path.exists():
        hinted = hint_path.read_text(encoding="utf-8", errors="ignore").strip()
        if hinted:
            return Path(hinted).expanduser().resolve()

    raise ValueError(
        "SEC source path is not configured. Set SEC_SOURCE_DIR or write the source path to "
        f"{hint_file}."
    )


def iter_filing_paths(root: Path) -> Iterator[Path]:
    for year_dir in sorted(root.iterdir()):
        if not year_dir.is_dir() or not YEAR_DIR_RE.match(year_dir.name):
            continue
        for quarter_dir in sorted(year_dir.iterdir()):
            quarter_match = QTR_DIR_RE.match(quarter_dir.name)
            if not quarter_dir.is_dir() or quarter_match is None:
                continue
            yield from sorted(path for path in quarter_dir.glob("*.txt") if path.is_file())


def parse_filename(path: Path) -> Optional[dict[str, Any]]:
    match = FNAME_RE.match(path.name)
    if match is None:
        return None
    quarter_match = QTR_DIR_RE.match(path.parent.name)
    quarter = int(quarter_match.group("quarter")) if quarter_match else None
    year = int(match.group("date")[:4])
    return {
        "cik": match.group("cik"),
        "year": year,
        "quarter": quarter,
        "form": match.group("form").upper(),
        "filename": path.name,
    }


def source_window_id_for_year(year: int) -> str:
    return ACTIVE_SOURCE_WINDOW_ID if 2021 <= year <= 2024 else HISTORICAL_SOURCE_WINDOW_ID


def build_index_rows(
    root: Path, source_root_ref: str = SOURCE_ROOT_REF
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    indexed_at = now_utc_iso()
    rows: list[dict[str, Any]] = []
    scanned_count = 0
    unmatched_files: list[str] = []

    for filing_path in iter_filing_paths(root):
        scanned_count += 1
        parsed = parse_filename(filing_path)
        if parsed is None:
            unmatched_files.append(str(filing_path.relative_to(root)))
            continue
        rows.append(
            {
                "cik": parsed["cik"],
                "year": parsed["year"],
                "quarter": parsed["quarter"],
                "form": parsed["form"],
                "filename": parsed["filename"],
                "path": filing_path.relative_to(root).as_posix(),
                "source_root": source_root_ref,
                "index_timestamp": indexed_at,
                "source_window_id": source_window_id_for_year(parsed["year"]),
            }
        )

    rows.sort(
        key=lambda row: (
            row["year"],
            row["quarter"] or 0,
            row["form"],
            row["cik"],
            row["filename"],
        )
    )
    return rows, {
        "indexed_at": indexed_at,
        "scanned_count": scanned_count,
        "unmatched_count": len(unmatched_files),
        "unmatched_files": unmatched_files[:25],
    }


def build_source_windows(rows: list[dict[str, Any]], source_root_name: str) -> dict[str, Any]:
    year_counts = Counter(str(row["year"]) for row in rows)
    available_years = sorted(year_counts)
    active_indexed_years = [year for year in ACTIVE_YEARS if year in year_counts]
    active_missing_years = [year for year in ACTIVE_YEARS if year not in year_counts]
    historical_years = [year for year in available_years if int(year) < 2021]

    return {
        "generated_at": now_utc_iso(),
        "source_root_ref": SOURCE_ROOT_REF,
        "source_root_name": source_root_name,
        "all_indexed_years": available_years,
        "windows": [
            {
                "source_window_id": ACTIVE_SOURCE_WINDOW_ID,
                "roadmap_status": "active",
                "expected_years": list(ACTIVE_YEARS),
                "indexed_years": active_indexed_years,
                "missing_years": active_missing_years,
                "availability_status": "complete" if not active_missing_years else "incomplete",
                "filing_count": sum(year_counts.get(year, 0) for year in ACTIVE_YEARS),
            },
            {
                "source_window_id": HISTORICAL_SOURCE_WINDOW_ID,
                "roadmap_status": "deferred",
                "expected_years": ["2000-2020"],
                "indexed_years": historical_years,
                "missing_years": [],
                "availability_status": (
                    "available_for_activation" if historical_years else "not_available"
                ),
                "filing_count": sum(year_counts[year] for year in historical_years),
                "note": (
                    "Historical backfill remains deferred until older years are intentionally "
                    "made available under SEC_SOURCE_DIR."
                ),
            },
        ],
    }


def build_summary_report(
    rows: list[dict[str, Any]],
    scan_meta: dict[str, Any],
    source_windows: dict[str, Any],
    source_root_name: str,
    output_csv: str,
) -> dict[str, Any]:
    form_counts = Counter(row["form"] for row in rows)
    year_counts = Counter(str(row["year"]) for row in rows)
    quarter_counts = Counter(f"{row['year']}:Q{row['quarter']}" for row in rows)

    return {
        "generated_at": now_utc_iso(),
        "source_root_ref": SOURCE_ROOT_REF,
        "source_root_name": source_root_name,
        "output_csv": output_csv,
        "scanned_file_count": scan_meta["scanned_count"],
        "indexed_row_count": len(rows),
        "unmatched_file_count": scan_meta["unmatched_count"],
        "sample_unmatched_files": scan_meta["unmatched_files"],
        "year_counts": dict(sorted(year_counts.items())),
        "form_counts": dict(sorted(form_counts.items())),
        "quarter_counts": dict(sorted(quarter_counts.items())),
        "source_windows": source_windows["windows"],
    }


def write_index_csv(rows: list[dict[str, Any]], output_csv: str) -> None:
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
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
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", default="")
    parser.add_argument("--output-csv", default=OUTPUT_CSV)
    parser.add_argument("--output-source-windows", default=OUTPUT_SOURCE_WINDOWS)
    parser.add_argument("--output-summary", default=OUTPUT_SUMMARY)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = resolve_sec_source(source_root=args.source_root)
    if not root.exists():
        raise FileNotFoundError(f"Source directory not found: {root}")

    rows, scan_meta = build_index_rows(root)
    source_windows = build_source_windows(rows, source_root_name=root.name)
    summary = build_summary_report(
        rows,
        scan_meta=scan_meta,
        source_windows=source_windows,
        source_root_name=root.name,
        output_csv=args.output_csv,
    )

    write_index_csv(rows, args.output_csv)
    dump_json(args.output_source_windows, source_windows)
    dump_json(args.output_summary, summary)

    print(f"[i] Scanned SEC source root: {root.name}")
    print(f"[i] Files scanned: {scan_meta['scanned_count']:,}")
    print(f"[i] Indexed rows: {len(rows):,}")
    print(f"[i] Unmatched files: {scan_meta['unmatched_count']:,}")
    print(f"[i] Wrote filings index: {args.output_csv}")
    print(f"[i] Wrote source windows: {args.output_source_windows}")
    print(f"[✓] Wrote summary: {args.output_summary}")


if __name__ == "__main__":
    main()
