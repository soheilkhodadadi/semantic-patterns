"""
Aggregate per-file classification outputs into firm-year features.

This script walks ``data/processed/sec`` (including year subfolders), finds
``*_classified.csv`` (current output) and ``*_classified.txt`` (legacy output),
parses predicted labels, and aggregates raw counts at the ``(cik, year)`` level.
It then writes both raw counts and log-transformed features to:

  data/final/ai_frequencies_by_firm_year.csv

Notes:
- We aggregate RAW counts first, then apply ``log1p(x) = log(1 + x)``.
- Robust to nested directories and minor format glitches.
- If a classified file has zero labeled lines, we still emit a row with
  ``0`` counts for that ``(cik, year)``.
"""

from __future__ import annotations

import csv
import logging
import math
import os
import re
from collections import defaultdict
from typing import Dict, Iterator, List, Tuple

import pandas as pd

logger = logging.getLogger(__name__)

# Root containing classified outputs (may include year subfolders)
CLASSIFIED_ROOT = "data/processed/sec"
CLASSIFIED_SUFFIXES = ("_classified.csv", "_classified.txt")
VALID_LABELS = ("Actionable", "Speculative", "Irrelevant")

# Output
OUTPUT_PATH = "data/final/ai_frequencies_by_firm_year.csv"


def extract_year_and_cik(filename: str) -> Tuple[int, str]:
    """Extract year and CIK from a classified filename.

    Expected patterns (examples):
      20240208_10-K_edgar_data_1571949_0001571949-24-000007_classified.csv
      20220207_10-K_edgar_data_1318605_0000950170-22-000796_classified.txt

    Year: first 4 digits of filename.
    CIK : digits between ``edgar_data_`` and the next underscore.
    """
    m_year = re.match(r"(?P<year>\d{4})", filename)
    year = int(m_year.group("year")) if m_year else -1

    m_cik = re.search(r"edgar_data_(\d+)_", filename)
    cik = m_cik.group(1) if m_cik else "unknown"

    return year, cik


def parse_labels_from_txt_file(path: str) -> List[str]:
    """Read a legacy ``*_classified.txt`` file and return parsed labels."""
    labels: List[str] = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if " | Label: " not in line:
                    continue
                after = line.split(" | Label: ", 1)[1]
                label = after.split(" |", 1)[0].strip()
                if label:
                    labels.append(label)
    except OSError as exc:
        logger.warning("Failed to read classified TXT file %s: %s", path, exc)
    return labels


def parse_labels_from_csv_file(path: str) -> List[str]:
    """Read a ``*_classified.csv`` file and return parsed labels.

    The parser prefers ``label_pred`` and falls back to ``label`` if needed.
    """
    labels: List[str] = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                return labels

            fields = {
                field.strip().lower(): field
                for field in reader.fieldnames
                if isinstance(field, str) and field.strip()
            }
            label_field = fields.get("label_pred") or fields.get("label")
            if not label_field:
                logger.warning("No label column found in classified CSV: %s", path)
                return labels

            for row in reader:
                if not isinstance(row, dict):
                    continue
                value = row.get(label_field)
                if value is None:
                    continue
                label = value.strip() if isinstance(value, str) else str(value).strip()
                if label:
                    labels.append(label)
    except OSError as exc:
        logger.warning("Failed to read classified CSV file %s: %s", path, exc)
    return labels


def parse_labels_from_file(path: str) -> List[str]:
    """Dispatch parsing for either legacy TXT or current CSV classified files."""
    if path.endswith("_classified.csv"):
        return parse_labels_from_csv_file(path)
    if path.endswith("_classified.txt"):
        return parse_labels_from_txt_file(path)
    return []


def iter_classified_files(classified_root: str) -> Iterator[str]:
    """Yield absolute paths to supported classified files under ``classified_root``."""
    discovered: list[str] = []
    for root, _, files in os.walk(classified_root):
        for name in files:
            if name.endswith(CLASSIFIED_SUFFIXES):
                discovered.append(os.path.join(root, name))
    for path in sorted(discovered):
        yield path


def build_aggregated_rows(classified_root: str) -> Tuple[List[dict], int, int, int]:
    """Return aggregated firm-year rows plus scan stats.

    Returns
    -------
    Tuple[List[dict], int, int, int]
        ``(rows, classified_files, used_files, firm_years_seen_count)``
    """
    agg: Dict[Tuple[str, int], Dict[str, int]] = defaultdict(
        lambda: {"Actionable": 0, "Speculative": 0, "Irrelevant": 0}
    )
    firm_years_seen: set[Tuple[str, int]] = set()

    classified_files = 0
    used_files = 0

    for path in iter_classified_files(classified_root):
        classified_files += 1
        filename = os.path.basename(path)

        year, cik = extract_year_and_cik(filename)
        if year == -1 or cik == "unknown":
            continue

        firm_years_seen.add((cik, year))
        labels = parse_labels_from_file(path)
        if not labels:
            continue

        used_files += 1
        for label in labels:
            if label in VALID_LABELS:
                agg[(cik, year)][label] += 1

    all_keys = set(agg.keys()) | firm_years_seen

    rows: list[dict] = []
    for cik, year in sorted(all_keys, key=lambda key: (key[0], key[1])):
        counts = agg.get((cik, year), {"Actionable": 0, "Speculative": 0, "Irrelevant": 0})
        actionable_count = int(counts.get("Actionable", 0))
        speculative_count = int(counts.get("Speculative", 0))
        irrelevant_count = int(counts.get("Irrelevant", 0))
        total_count = actionable_count + speculative_count + irrelevant_count

        rows.append(
            {
                "cik": cik,
                "year": int(year),
                "A_count": actionable_count,
                "S_count": speculative_count,
                "I_count": irrelevant_count,
                "total_count": total_count,
                "AI_frequencyA": math.log1p(actionable_count),
                "AI_frequencyS": math.log1p(speculative_count),
                "AI_frequencyI": math.log1p(irrelevant_count),
                "AI_frequency_total": math.log1p(total_count),
            }
        )

    return rows, classified_files, used_files, len(all_keys)


def main() -> None:
    rows, classified_files, used_files, firm_years_seen_count = build_aggregated_rows(
        CLASSIFIED_ROOT
    )

    df = pd.DataFrame(rows)
    if not df.empty:
        df.sort_values(by=["cik", "year"], inplace=True)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(
        f"[✓] Aggregated {len(df)} firm-year rows "
        f"(scanned {classified_files} classified files, with {firm_years_seen_count} "
        f"firm-years seen; non-empty: {used_files})."
    )
    print(f"[→] Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
