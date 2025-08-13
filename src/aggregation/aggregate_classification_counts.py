import os
import math
from collections import Counter
import pandas as pd

# Path to classified sentence files
classified_dir = "data/processed/sec"

# Store aggregated results
rows = []

for filename in os.listdir(classified_dir):
    if not filename.endswith("_classified.txt"):
        continue

    path = os.path.join(classified_dir, filename)
    with open(path, "r", encoding="utf-8") as f:
        labels = [
            line.split(" | Label: ")[1].split(" |")[0]
            for line in f if " | Label: " in line
        ]
        if not labels:
            continue
        counts = Counter(labels)

    # Extract CIK and year from filename
    parts = filename.split("_")
    year = parts[0][:4]
    cik = parts[4] if len(parts) > 4 else "unknown"

    # Compute log-transformed counts
    actionable = counts.get("Actionable", 0)
    speculative = counts.get("Speculative", 0)
    irrelevant = counts.get("Irrelevant", 0)
    total = actionable + speculative + irrelevant

    row = {
        "cik": cik,
        "year": int(year),
        "AI_frequencyA": math.log(actionable + 1),
        "AI_frequencyS": math.log(speculative + 1),
        "AI_frequencyI": math.log(irrelevant + 1),
        "AI_frequency_total": math.log(total + 1)
    }
    rows.append(row)

# Convert to DataFrame
df = pd.DataFrame(rows)
df.sort_values(by=["cik", "year"], inplace=True)

# Save
output_path = "data/final/ai_frequencies_by_firm_year.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df.to_csv(output_path, index=False)
print(f"[✓] Saved {len(df)} firm-year rows with total frequency to: {output_path}")

"""
Aggregate per-file classification outputs into firm-year features.

This script walks data/processed/sec (including year subfolders),
finds all *_classified.txt files, parses their predicted labels, and
aggregates raw counts at the (cik, year) level. It then writes both
raw counts and log-transformed features to:

  data/final/ai_frequencies_by_firm_year.csv

Notes:
- We aggregate RAW counts first, then apply log(1 + x).
- Robust to nested directories and minor format glitches.
"""

import os
import re
import math
from collections import defaultdict
import pandas as pd

# Root containing *_classified.txt files (may include year subfolders)
CLASSIFIED_ROOT = "data/processed/sec"

# Output
OUTPUT_PATH = "data/final/ai_frequencies_by_firm_year.csv"


def extract_year_and_cik(filename: str) -> tuple[int, str]:
    """
    Extract year and CIK from a classified filename like:
    20240208_10-K_edgar_data_1571949_0001571949-24-000007_classified.txt

    Year: first 4 digits of filename.
    CIK : digits between 'edgar_data_' and the next underscore.
    """
    # Year = first 4 digits
    m_year = re.match(r"(?P<year>\d{4})", filename)
    year = int(m_year.group("year")) if m_year else -1

    # CIK via 'edgar_data_XXXX_' pattern
    m_cik = re.search(r"edgar_data_(\d+)_", filename)
    cik = m_cik.group(1) if m_cik else "unknown"

    return year, cik


def parse_labels_from_file(path: str) -> list[str]:
    """
    Read a *_classified.txt file and return list of labels found.
    Expects lines that contain: " | Label: <Label> |"
    """
    labels: list[str] = []
    # Use errors="ignore" in case of odd encoding artifacts
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if " | Label: " not in line:
                continue
            try:
                # Split only once on the known marker and then up to next ' |'
                after = line.split(" | Label: ", 1)[1]
                label = after.split(" |", 1)[0].strip()
                if label:
                    labels.append(label)
            except Exception:
                # Skip malformed line
                continue
    return labels


def main() -> None:
    # Aggregate raw counts first
    agg = defaultdict(lambda: {"Actionable": 0, "Speculative": 0, "Irrelevant": 0})

    files_seen = 0
    classified_files = 0

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

            labels = parse_labels_from_file(path)
            if not labels:
                continue

            files_seen += 1
            for lbl in labels:
                if lbl in ("Actionable", "Speculative", "Irrelevant"):
                    agg[(cik, year)][lbl] += 1
                # else: ignore unexpected labels silently

    # Build rows
    rows = []
    for (cik, year), counts in sorted(agg.items(), key=lambda k: (k[0][0], k[0][1])):
        a = counts.get("Actionable", 0)
        s = counts.get("Speculative", 0)
        i = counts.get("Irrelevant", 0)
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
        f"[✓] Aggregated {len(df)} firm-year rows "
        f"(scanned {classified_files} classified files, used {files_seen})."
    )
    print(f"[→] Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()