"""Build a filing-level event-study spine from classified SEC filing outputs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_CLASSIFIED_DIR = "data/processed/sec"
DEFAULT_CROSSWALK = "data/externals/crosswalks/cik_gvkey_active_annual_allyears_2021_2024_v3.csv"
DEFAULT_OUTPUT = "data/interim/market/filing_event_spine_v1.csv"
DEFAULT_REPORT = "reports/analysis/filing_event_spine_v1.json"
DEFAULT_FORMS = ("10-K", "10-K-A")

FILENAME_PATTERN = re.compile(
    r"^(?P<filing_date>\d{8})_"
    r"(?P<form>[^_]+)_"
    r"edgar_data_"
    r"(?P<cik>\d+)_"
    r"(?P<accession>[^_]+)"
    r"(?:_scored)?_classified\.csv$"
)

OUTPUT_COLUMNS = [
    "filing_id",
    "source_filename",
    "source_path",
    "filing_date",
    "filing_year",
    "form_type",
    "cik",
    "accession_number",
    "gvkey",
    "ticker_comp",
    "issuer_name",
    "sic",
]


@dataclass(frozen=True)
class FilingMetadata:
    filing_date: str
    form_type: str
    cik: str
    accession_number: str


def normalize_cik(value: Any) -> str:
    text = str(value or "").strip()
    digits = "".join(character for character in text if character.isdigit())
    return digits.zfill(10) if digits else ""


def parse_classified_filename(filename: str) -> FilingMetadata:
    match = FILENAME_PATTERN.match(filename)
    if not match:
        raise ValueError(f"Unrecognized classified filing filename: {filename}")
    return FilingMetadata(
        filing_date=match.group("filing_date"),
        form_type=match.group("form"),
        cik=normalize_cik(match.group("cik")),
        accession_number=match.group("accession"),
    )


def compute_filing_id(source_filename: str) -> str:
    return hashlib.sha1(source_filename.encode("utf-8")).hexdigest()[:16]


def load_crosswalk(path: str | Path) -> dict[str, dict[str, str]]:
    resolved = Path(path)
    if not resolved.exists():
        return {}

    with resolved.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            return {}
        crosswalk: dict[str, dict[str, str]] = {}
        for row in reader:
            cik = normalize_cik(row.get("cik"))
            if not cik or cik in crosswalk:
                continue
            crosswalk[cik] = {
                "gvkey": str(row.get("gvkey", "") or "").strip(),
                "ticker_comp": str(row.get("ticker_comp", "") or "").strip(),
                "issuer_name": str(row.get("name", "") or "").strip(),
                "sic": str(row.get("sic", "") or "").strip(),
            }
    return crosswalk


def iter_classified_files(
    classified_dir: str | Path,
    *,
    allowed_forms: set[str],
    start_year: int | None,
    end_year: int | None,
) -> list[tuple[Path, FilingMetadata]]:
    resolved_dir = Path(classified_dir)
    records: list[tuple[Path, FilingMetadata]] = []
    for path in sorted(resolved_dir.glob("*_classified.csv")):
        try:
            metadata = parse_classified_filename(path.name)
        except ValueError:
            continue
        if allowed_forms and metadata.form_type.upper() not in allowed_forms:
            continue
        filing_year = int(metadata.filing_date[:4])
        if start_year is not None and filing_year < start_year:
            continue
        if end_year is not None and filing_year > end_year:
            continue
        records.append((path, metadata))
    return records


def build_event_spine(
    classified_dir: str = DEFAULT_CLASSIFIED_DIR,
    crosswalk_path: str = DEFAULT_CROSSWALK,
    *,
    forms: tuple[str, ...] = DEFAULT_FORMS,
    start_year: int | None = None,
    end_year: int | None = None,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    allowed_forms = {value.strip().upper() for value in forms if value.strip()}
    crosswalk = load_crosswalk(crosswalk_path)
    records = iter_classified_files(
        classified_dir,
        allowed_forms=allowed_forms,
        start_year=start_year,
        end_year=end_year,
    )

    rows: list[dict[str, str]] = []
    form_counts: dict[str, int] = {}
    year_counts: dict[str, int] = {}
    crosswalk_hits = 0

    for path, metadata in records:
        lookup = crosswalk.get(metadata.cik, {})
        if lookup:
            crosswalk_hits += 1
        row = {
            "filing_id": compute_filing_id(path.name),
            "source_filename": path.name,
            "source_path": str(path),
            "filing_date": metadata.filing_date,
            "filing_year": metadata.filing_date[:4],
            "form_type": metadata.form_type,
            "cik": metadata.cik,
            "accession_number": metadata.accession_number,
            "gvkey": lookup.get("gvkey", ""),
            "ticker_comp": lookup.get("ticker_comp", ""),
            "issuer_name": lookup.get("issuer_name", ""),
            "sic": lookup.get("sic", ""),
        }
        rows.append(row)
        form_counts[row["form_type"]] = form_counts.get(row["form_type"], 0) + 1
        year_counts[row["filing_year"]] = year_counts.get(row["filing_year"], 0) + 1

    summary = {
        "classified_dir": str(Path(classified_dir).resolve()),
        "crosswalk_path": str(Path(crosswalk_path).resolve()),
        "forms": sorted(allowed_forms),
        "row_count": len(rows),
        "year_counts": dict(sorted(year_counts.items())),
        "form_counts": dict(sorted(form_counts.items())),
        "crosswalk_match_count": crosswalk_hits,
        "crosswalk_match_rate": round(crosswalk_hits / len(rows), 4) if rows else 0.0,
        "date_min": min((row["filing_date"] for row in rows), default=""),
        "date_max": max((row["filing_date"] for row in rows), default=""),
        "unique_cik_count": len({row["cik"] for row in rows if row["cik"]}),
        "unique_gvkey_count": len({row["gvkey"] for row in rows if row["gvkey"]}),
    }
    return rows, summary


def write_event_spine(rows: list[dict[str, str]], output_path: str | Path) -> None:
    resolved = Path(output_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def write_report(report: dict[str, Any], path: str | Path) -> None:
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(report, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--classified-dir", default=DEFAULT_CLASSIFIED_DIR)
    parser.add_argument("--crosswalk", default=DEFAULT_CROSSWALK)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    parser.add_argument("--forms", default=",".join(DEFAULT_FORMS))
    parser.add_argument("--start-year", type=int, default=None)
    parser.add_argument("--end-year", type=int, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    forms = tuple(part.strip() for part in args.forms.split(",") if part.strip())
    rows, report = build_event_spine(
        classified_dir=args.classified_dir,
        crosswalk_path=args.crosswalk,
        forms=forms,
        start_year=args.start_year,
        end_year=args.end_year,
    )
    write_event_spine(rows, args.output)
    write_report(report, args.report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
