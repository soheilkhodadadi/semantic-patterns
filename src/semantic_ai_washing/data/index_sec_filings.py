import os
import re
import csv
from pathlib import Path
from typing import Iterator, Dict, Any, Tuple, Optional

"""
Index SEC filings on disk by parsing file names.

Outputs: data/metadata/available_filings_index.csv with columns:
  cik,year,form,filename,path

Assumptions:
- Files are stored under a root with subfolders by year and quarter, e.g.:
    /Users/soheilkhodadadi/DataWork/10-X_C_2021-2124/{2021..2024}/QTR{1..4}/*.txt
- File names include the fragment "edgar_data_{CIK}_" and start with YYYYMMDD,
  e.g., 20220401_10-K_edgar_data_862861_0000950170-22-005290.txt
- Forms of interest include 10-K / 10-K/A / 10-Q / 10-Q/A; we index all.
- The root directory can be set via the SEC_SOURCE_DIR env var.
"""

DEFAULT_SEC_SOURCE = os.environ.get(
    "SEC_SOURCE_DIR",
    "/Users/soheilkhodadadi/DataWork/10-X_C_2021-2124",
)

OUTPUT_CSV = "data/metadata/available_filings_index.csv"

# Example: 20220401_10-K_edgar_data_862861_0000950170-22-005290.txt
FNAME_RE = re.compile(
    r"^(?P<date>\d{8})_(?P<form>10-[KQ](?:-A)?)_edgar_data_(?P<cik>\d+)_.*\.txt$",
    re.IGNORECASE,
)


def iter_filing_paths(root: Path) -> Iterator[Path]:
    for year_dir in sorted(root.glob("20[12][1-4]")):  # 2021..2024
        if not year_dir.is_dir():
            continue
        for qdir in sorted(year_dir.glob("QTR[1-4]")):
            if not qdir.is_dir():
                continue
            yield from (p for p in qdir.glob("*.txt") if p.is_file())


def parse_filename(path: Path) -> Optional[Tuple[str, int, str]]:
    m = FNAME_RE.match(path.name)
    if not m:
        return None
    cik = m.group("cik")
    year = int(m.group("date")[:4])
    form = m.group("form").upper()
    return cik, year, form


def main() -> None:
    root = Path(DEFAULT_SEC_SOURCE)
    if not root.exists():
        raise FileNotFoundError(f"Source directory not found: {root}")

    out_path = Path(OUTPUT_CSV)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    total = 0
    matched = 0
    rows: list[Dict[str, Any]] = []

    for p in iter_filing_paths(root):
        total += 1
        parsed = parse_filename(p)
        if not parsed:
            continue
        cik, year, form = parsed
        rows.append({"cik": cik, "year": year, "form": form, "filename": p.name, "path": str(p)})
        matched += 1

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["cik", "year", "form", "filename", "path"])
        writer.writeheader()
        writer.writerows(rows)

    by_year: Dict[int, int] = {}
    for r in rows:
        by_year[r["year"]] = by_year.get(r["year"], 0) + 1

    print(f"[i] Scanned: {root}")
    print(f"[i] Files found: {total:,}  |  Indexed: {matched:,}")
    print("[i] Per-year counts:")
    for y in sorted(by_year):
        print(f"   {y}: {by_year[y]:,}")
    print(f"[✓] Wrote index: {out_path}  ({len(rows):,} rows)")


if __name__ == "__main__":
    main()
