"""
Aggregate per-file classification outputs into firm-year features.

This script walks data/processed/sec (including year subfolders),
finds all *_classified.txt files, parses their predicted labels, and
aggregates raw counts at the (cik, year) level. It then writes both
raw counts and log-transformed features to:

  data/final/ai_frequencies_by_firm_year.csv

Notes:
- We aggregate RAW counts first, then apply log1p(x) = log(1 + x).
- Robust to nested directories and minor format glitches.
- If a classified file has zero labeled lines, we still emit a row
  with 0 counts for that (cik, year).
"""

from __future__ import annotations

import os
import re
import math
from collections import defaultdict
from typing import Dict, List, Tuple
import pandas as pd

# Root containing *_classified.txt files (may include year subfolders)
CLASSIFIED_ROOT = "data/processed/sec"

# Output
OUTPUT_PATH = "data/final/ai_frequencies_by_firm_year.csv"


def extract_year_and_cik(filename: str) -> Tuple[int, str]:
    """Extract year and CIK from a classified filename.

    Expected pattern (examples):
      20240208_10-K_edgar_data_1571949_0001571949-24-000007_classified.txt
      20220207_10-K_edgar_data_1318605_0000950170-22-000796_classified.txt

    Year: first 4 digits of filename.
    CIK : digits between 'edgar_data_' and the next underscore.
    """
    # Year = first 4 digits at start
    m_year = re.match(r"(?P<year>\d{4})", filename)
    year = int(m_year.group("year")) if m_year else -1

    # CIK via 'edgar_data_XXXX_' pattern
    m_cik = re.search(r"edgar_data_(\d+)_", filename)
    cik = m_cik.group(1) if m_cik else "unknown"

    return year, cik


def parse_labels_from_file(path: str) -> List[str]:
    """Read a *_classified.txt file and return list of labels found.

    Expects lines that contain: " | Label: <Label> |"
    Safely ignores malformed lines and odd encodings.
    """
    labels: List[str] = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if " | Label: " not in line:
                continue
            try:
                after = line.split(" | Label: ", 1)[1]
                label = after.split(" |", 1)[0].strip()
                if label:
                    labels.append(label)
            except Exception:
                continue
    return labels


def main() -> None:
    # Aggregate raw counts first
    agg: Dict[Tuple[str, int], Dict[str, int]] = defaultdict(
        lambda: {"Actionable": 0, "Speculative": 0, "Irrelevant": 0}
    )

    # Track all firm-years for which a classified file exists (even if empty)
    firm_years_seen: set[Tuple[str, int]] = set()

    classified_files = 0
    used_files = 0

    for root, _, files in os.walk(CLASSIFIED_ROOT):
        for fn in files:
            if not fn.endswith("_classified.txt"):
                continue
            classified_files += 1
            path = os.path.join(root, fn)

            year, cik = extract_year_and_cik(fn)
            if year == -1 or cik == "unknown":
                # Skip files we can't parse reliably
                continue

            firm_years_seen.add((cik, year))

            labels = parse_labels_from_file(path)
            # If file has no labels, we still want a zero row; just continue
            if not labels:
                continue

            used_files += 1
            for lbl in labels:
                if lbl in ("Actionable", "Speculative", "Irrelevant"):
                    agg[(cik, year)][lbl] += 1
                # else: ignore unexpected labels silently

    # Build rows for union of (agg keys) U (firm_years_seen)
    all_keys = set(agg.keys()) | firm_years_seen

    rows = []
    for cik, year in sorted(all_keys, key=lambda k: (k[0], k[1])):
        counts = agg.get((cik, year), {"Actionable": 0, "Speculative": 0, "Irrelevant": 0})
        a = int(counts.get("Actionable", 0))
        s = int(counts.get("Speculative", 0))
        i = int(counts.get("Irrelevant", 0))
        total = a + s + i

        rows.append(
            {
                "cik": cik,
                "year": int(year),
                # raw counts
                "A_count": a,
                "S_count": s,
                "I_count": i,
                "total_count": total,
                # log(1+x) features
                "AI_frequencyA": math.log1p(a),
                "AI_frequencyS": math.log1p(s),
                "AI_frequencyI": math.log1p(i),
                "AI_frequency_total": math.log1p(total),
            }
        )

    df = pd.DataFrame(rows)

    # Sort for readability
    if not df.empty:
        df.sort_values(by=["cik", "year"], inplace=True)

    # Ensure output dir exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(
        f"[\u2713] Aggregated {len(df)} firm-year rows "
        f"(scanned {classified_files} classified files, with {len(all_keys)} firm-years seen; "
        f"non-empty: {used_files})."
    )
    print(f"[\u2192] Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
