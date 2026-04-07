"""Extract company names and aliases from SEC filing headers.

This utility is designed for patent lookup repair work. It scans SEC raw filing
text files, extracts the CIK, the company conformed name, and any former
conformed names from the header, and writes a CSV that can be used as input to
``build_company_lookup``.
"""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass, field
from itertools import islice
from pathlib import Path


HEADER_LINE_LIMIT = 300
DEFAULT_FORM_PREFIXES = ("10-K",)

PATTERNS = {
    "cik": re.compile(r"^\s*CENTRAL INDEX KEY:\s*(\d+)\s*$", re.IGNORECASE),
    "name": re.compile(r"^\s*COMPANY CONFORMED NAME:\s*(.+?)\s*$", re.IGNORECASE),
    "former": re.compile(r"^\s*FORMER CONFORMED NAME:\s*(.+?)\s*$", re.IGNORECASE),
    "submission": re.compile(r"^\s*CONFORMED SUBMISSION TYPE:\s*(.+?)\s*$", re.IGNORECASE),
    "filed": re.compile(r"^\s*FILED AS OF DATE:\s*(\d{8})\s*$", re.IGNORECASE),
}


@dataclass(slots=True)
class SecHeaderCompanyEntity:
    """One company block extracted from a filing header."""

    cik: str = ""
    name: str = ""
    former_names: list[str] = field(default_factory=list)

    def normalized_former_names(self) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for item in self.former_names:
            cleaned = normalize_whitespace(item)
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                out.append(cleaned)
        return out


@dataclass(slots=True)
class SecHeaderFilingRecord:
    """Structured filing-level metadata plus extracted company blocks."""

    source_file: str
    filing_date: str = ""
    submission_type: str = ""
    companies: list[SecHeaderCompanyEntity] = field(default_factory=list)


def normalize_cik(value: str) -> str:
    digits = re.sub(r"\D", "", str(value))
    return digits.zfill(10) if digits else ""


def normalize_whitespace(value: str) -> str:
    return " ".join(str(value).split()).strip()


def parse_header_lines(lines: list[str], *, source_file: str) -> SecHeaderFilingRecord:
    record = SecHeaderFilingRecord(source_file=source_file)
    pending_name = ""
    current_company: SecHeaderCompanyEntity | None = None
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        match = PATTERNS["cik"].match(line)
        if match:
            cik = normalize_cik(match.group(1))
            if pending_name:
                current_company = SecHeaderCompanyEntity(cik=cik, name=pending_name)
                record.companies.append(current_company)
                pending_name = ""
            elif current_company is not None and not current_company.cik:
                current_company.cik = cik
            continue

        match = PATTERNS["name"].match(line)
        if match:
            pending_name = normalize_whitespace(match.group(1))
            continue

        match = PATTERNS["former"].match(line)
        if match:
            if current_company is not None:
                current_company.former_names.append(normalize_whitespace(match.group(1)))
            continue

        match = PATTERNS["submission"].match(line)
        if match:
            record.submission_type = normalize_whitespace(match.group(1)).upper()
            continue

        match = PATTERNS["filed"].match(line)
        if match:
            record.filing_date = match.group(1)

    return record


def read_header_record(path: Path, *, source_file: str, header_line_limit: int) -> SecHeaderFilingRecord:
    with path.open(encoding="utf-8", errors="ignore") as handle:
        lines = list(islice(handle, header_line_limit))
    return parse_header_lines(lines, source_file=source_file)


def resolve_input_paths(
    root: Path | None,
    source_files: list[str],
    *,
    recursive_scan: bool,
) -> list[tuple[Path, str]]:
    if source_files:
        resolved: list[tuple[Path, str]] = []
        for source in source_files:
            source_path = Path(source)
            candidate = source_path
            if not candidate.is_absolute():
                candidate = (root or Path.cwd()) / candidate
            if not candidate.exists():
                raise FileNotFoundError(f"Missing SEC filing: {candidate}")
            if root is not None:
                try:
                    rel = candidate.relative_to(root)
                    source_label = rel.as_posix()
                except ValueError:
                    source_label = source_path.as_posix()
            else:
                source_label = source_path.as_posix()
            resolved.append((candidate, source_label))
        return resolved

    if root is None:
        raise ValueError("Either --root or at least one --source-file must be provided.")

    if not root.exists():
        raise FileNotFoundError(f"Missing SEC root: {root}")

    if recursive_scan:
        candidates = sorted(p for p in root.rglob("*.txt") if p.is_file())
    else:
        candidates = sorted(p for p in root.glob("*.txt") if p.is_file())
    return [(path, path.relative_to(root).as_posix()) for path in candidates]


def form_is_selected(submission_type: str, form_prefixes: tuple[str, ...]) -> bool:
    if not submission_type:
        return False
    upper = submission_type.upper()
    return any(upper.startswith(prefix.upper()) for prefix in form_prefixes)


def build_output_rows(record: SecHeaderFilingRecord) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for company in record.companies:
        if not company.cik or not company.name:
            continue
        former_names = company.normalized_former_names()
        rows.append(
            {
                "cik": company.cik,
                "name": company.name,
                "alias": "",
                "former_names": "|".join(former_names),
                "source_file": record.source_file,
                "filing_date": record.filing_date,
                "submission_type": record.submission_type,
                "record_type": "current_name",
            }
        )
        for former_name in former_names:
            rows.append(
                {
                    "cik": company.cik,
                    "name": company.name,
                    "alias": former_name,
                    "former_names": "",
                    "source_file": record.source_file,
                    "filing_date": record.filing_date,
                    "submission_type": record.submission_type,
                    "record_type": "former_name",
                }
            )
    return rows


def extract_sec_header_company_names(
    paths: list[tuple[Path, str]],
    *,
    header_line_limit: int = HEADER_LINE_LIMIT,
    form_prefixes: tuple[str, ...] = DEFAULT_FORM_PREFIXES,
) -> tuple[list[dict[str, str]], list[SecHeaderFilingRecord], list[dict[str, str]]]:
    rows: list[dict[str, str]] = []
    records: list[SecHeaderFilingRecord] = []
    skipped: list[dict[str, str]] = []

    for path, source_label in paths:
        record = read_header_record(path, source_file=source_label, header_line_limit=header_line_limit)
        if not form_is_selected(record.submission_type, form_prefixes):
            skipped.append(
                {
                    "source_file": source_label,
                    "submission_type": record.submission_type,
                    "reason": "form_filtered",
                }
            )
            continue
        records.append(record)
        rows.extend(build_output_rows(record))

    return rows, records, skipped


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "cik",
        "name",
        "alias",
        "former_names",
        "source_file",
        "filing_date",
        "submission_type",
        "record_type",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract company names and former names from SEC filing headers."
    )
    parser.add_argument(
        "--root",
        default="",
        help="SEC filing root directory. If --source-file is omitted, the root is scanned recursively for *.txt files.",
    )
    parser.add_argument(
        "--source-file",
        action="append",
        default=[],
        help="Relative or absolute SEC filing path. May be repeated.",
    )
    parser.add_argument(
        "--recursive-scan",
        action="store_true",
        help="When scanning --root, recurse through nested quarter directories. Enabled by default for the repair workflow.",
    )
    parser.add_argument(
        "--form-prefix",
        action="append",
        default=list(DEFAULT_FORM_PREFIXES),
        help="Allowed filing form prefix. May be repeated. Defaults to 10-K, which includes 10-K/A.",
    )
    parser.add_argument(
        "--header-line-limit",
        type=int,
        default=HEADER_LINE_LIMIT,
        help="Number of header lines to inspect per filing.",
    )
    parser.add_argument(
        "--out-csv",
        required=True,
        help="Output CSV path compatible with build_company_lookup input columns.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    root = Path(args.root) if args.root else None
    paths = resolve_input_paths(root, args.source_file, recursive_scan=args.recursive_scan or not args.source_file)
    rows, records, skipped = extract_sec_header_company_names(
        paths,
        header_line_limit=args.header_line_limit,
        form_prefixes=tuple(args.form_prefix),
    )

    out_path = Path(args.out_csv)
    write_csv(out_path, rows)

    print(f"[✓] Read filings: {len(paths)}")
    print(f"[✓] Extracted records: {len(records)}")
    print(f"[✓] Output rows: {len(rows)}")
    print(f"[✓] Saved CSV to: {out_path}")
    if skipped:
        print(f"[!] Skipped filings: {len(skipped)} (filtered by form prefix)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
