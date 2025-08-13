"""
Collect 10-K filing text for a firm list & year range, without overwriting.

Inputs:
  - data/metadata/company_list.csv  OR  data/metadata/company_list_50.csv
    (must contain a 'cik' column; optional 'ticker' / 'company_name')

Source:
  - SEC_SOURCE_DIR env var OR the default DataWork path below
    (expects files named like: 20210128_10-K_edgar_data_1326801_0001326801-21-000014.txt
     or ..._text.txt – we copy the file as-is)

Outputs:
  - data/processed/sec/<original_filename>.txt

Notes:
  - Skips non-10-K files.
  - Skips years outside 2021–2024.
  - Skips files that already exist at the destination (no overwrite).
"""

import os
import re
import glob
import shutil
import pandas as pd

# ---- config -----------------------------------------------------------------

# Which firm list to use (pick the one you actually have):
FIRMS_CSV_CANDIDATES = [
    "data/metadata/company_list_50.csv",
    "data/metadata/company_list.csv",
]

# Default source folder (can be overridden by env var SEC_SOURCE_DIR)
DEFAULT_SEC_SOURCE = "/Users/soheilkhodadadi/DataWork/10-X_C_2021-2124"

DEST_DIR = "data/processed/sec"
YEARS = {2021, 2022, 2023, 2024}

# filename pattern (captures date and cik):
# e.g. 20210128_10-K_edgar_data_1326801_0001326801-21-000014.txt
F_PAT = re.compile(r"(?P<date>\d{8})_10-K.*?_edgar_data_(?P<cik>\d+)_", re.IGNORECASE)

# ---- helpers ----------------------------------------------------------------

def pick_firm_list() -> str:
    for p in FIRMS_CSV_CANDIDATES:
        if os.path.exists(p):
            return p
    raise FileNotFoundError(
        "No firm list found. Expected one of:\n  - " + "\n  - ".join(FIRMS_CSV_CANDIDATES)
    )

def load_ciks(csv_path: str) -> set:
    df = pd.read_csv(csv_path)
    if "cik" not in df.columns:
        raise ValueError(f"'cik' column not found in {csv_path}")
    ciks = set(df["cik"].astype(str).str.extract(r"(\d+)")[0].dropna().tolist())
    return ciks

# ---- main -------------------------------------------------------------------

def main():
    firms_csv = pick_firm_list()
    ciks = load_ciks(firms_csv)
    print(f"[i] Using firm list: {firms_csv} ({len(ciks)} CIKs)")

    src_root = os.environ.get("SEC_SOURCE_DIR", DEFAULT_SEC_SOURCE)
    if not os.path.isdir(src_root):
        raise FileNotFoundError(
            f"Source directory not found: {src_root}\n"
            "Set SEC_SOURCE_DIR env var or update DEFAULT_SEC_SOURCE.\n"
            "Expected structure: <SRC_ROOT>/<YEAR>/QTR#/....txt  (e.g., 2024/QTR1/20240102_10-K_...txt)"
        )

    os.makedirs(DEST_DIR, exist_ok=True)

    # Find candidate files in /<YEAR>/QTR*/ subfolders (both .txt and *_text.txt are fine)
    candidates = []
    for y in sorted(YEARS):
        for q in (1, 2, 3, 4):
            pattern = os.path.join(src_root, str(y), f"QTR{q}", "*.txt")
            candidates.extend(glob.glob(pattern))
    print(f"[i] Found {len(candidates)} .txt files under {src_root} (scanned {len(YEARS)} years x 4 quarters)")

    copied, skipped_exists, skipped_filters = 0, 0, 0

    for src in candidates:
        fn = os.path.basename(src)
        m = F_PAT.search(fn)
        if not m:
            skipped_filters += 1
            continue

        year = int(m.group("date")[:4])
        cik = m.group("cik")

        # Only 10-Ks for our firms & years
        if year not in YEARS or cik not in ciks or "_10-K" not in fn.upper():
            skipped_filters += 1
            continue

        dest = os.path.join(DEST_DIR, fn)

        if os.path.exists(dest):
            skipped_exists += 1
            continue  # do NOT overwrite

        # Copy as-is (preserve timestamps)
        shutil.copy2(src, dest)
        copied += 1
        if copied % 10 == 0:
            print(f"[…] Copied {copied} so far…")

    print("\n—— Summary ————————————————")
    print(f"Copied new files     : {copied}")
    print(f"Skipped (already there): {skipped_exists}")
    print(f"Skipped (not our targets): {skipped_filters}")
    print(f"Destination dir      : {os.path.abspath(DEST_DIR)}\n")

    # Sanity: list a few examples
    sample = sorted(
        [p for p in glob.glob(os.path.join(DEST_DIR, "*.txt")) if "_10-K_" in p]
    )[:5]
    for s in sample:
        print("✓", s)

if __name__ == "__main__":
    main()