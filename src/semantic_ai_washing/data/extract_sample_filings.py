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
  - data/processed/sec/<YEAR>/<original_filename>.txt

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


# Build file patterns that include the CIK so we don't miss matches and so it runs faster
# Examples that should match:
#   20240125_10-K_edgar_data_10329_0001437749-24-002203.txt
#   20240125_10-K-A_edgar_data_10329_0001437749-24-002203.txt
#   20240125_10k_edgar_data_10329_... (case-insensitive safety)


def find_files_for_cik(src_root: str, cik: str, years: set[int]) -> list[str]:
    paths: list[str] = []
    for y in sorted(years):
        for q in (1, 2, 3, 4):
            # Allow *_10-K* and case variants; always require edgar_data_<cik>_
            # We search with two patterns to be robust to dashes/underscores around 10-K
            base = os.path.join(src_root, str(y), f"QTR{q}")
            patterns = [
                os.path.join(base, f"*_10-K*_edgar_data_{cik}_*.txt"),
                os.path.join(base, f"*10k*_edgar_data_{cik}_*.txt"),  # very rare, but cheap
            ]
            for pat in patterns:
                paths.extend(glob.glob(pat))
    # De-duplicate in case multiple patterns matched the same file
    return sorted(set(paths))


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

    print(f"[i] Scanning {len(YEARS)} years x 4 quarters for {len(ciks)} CIKs under: {src_root}")

    os.makedirs(DEST_DIR, exist_ok=True)

    copied, skipped_exists, skipped_filters = 0, 0, 0
    per_year = {y: 0 for y in YEARS}

    missing: list[tuple[str, int]] = []  # (cik, year) pairs with no 10-K found

    # Search per‑CIK to avoid missing matches due to filename idiosyncrasies
    for cik in sorted(ciks):
        found_any_for_cik = False
        for year in sorted(YEARS):
            hits = find_files_for_cik(src_root, cik, {year})
            if not hits:
                missing.append((cik, year))
                continue

            found_any_for_cik = True
            year_dir = os.path.join(DEST_DIR, str(year))
            os.makedirs(year_dir, exist_ok=True)

            for src in hits:
                fn = os.path.basename(src)
                dest = os.path.join(year_dir, fn)
                if os.path.exists(dest):
                    skipped_exists += 1
                    continue
                shutil.copy2(src, dest)
                copied += 1
                per_year[year] += 1
                if copied % 10 == 0:
                    print(f"[…] Copied {copied} so far…")

        if not found_any_for_cik:
            # small note so you can quickly diagnose completely missing firms
            print(f"[!] No 10‑K files found for CIK {cik} in {min(YEARS)}–{max(YEARS)}")

    # Write a CSV report of missing cik-year combos for quick debugging
    if missing:
        rep_path = os.path.join(DEST_DIR, "_missing_10K_report.csv")
        rep_df = (
            pd.DataFrame(missing, columns=["cik", "year"])
            .sort_values(["cik", "year"])
            .reset_index(drop=True)
        )
        rep_df.to_csv(rep_path, index=False)
        print(f"[!] Wrote missing report with {len(missing)} rows → {rep_path}")

    print("\n—— Summary ————————————————")
    print(f"Copied new files     : {copied}")
    print(f"Skipped (already there): {skipped_exists}")
    print(f"Skipped (not our targets): {skipped_filters}")
    print(f"Destination dir      : {os.path.abspath(DEST_DIR)}\n")

    print("Per-year copied counts:")
    for y in sorted(YEARS):
        print(f"  {y}: {per_year[y]}")

    # Sanity: list a few examples per year
    shown = 0
    for y in sorted(YEARS):
        year_glob = glob.glob(os.path.join(DEST_DIR, str(y), "*.txt"))
        print(f"Year {y}: {len(year_glob)} files")
        for s in sorted([p for p in year_glob if "_10-K_" in os.path.basename(p)])[:2]:
            print("  ✓", s)
            shown += 1
    if shown == 0:
        print("  (No 10-K files copied yet.)")


if __name__ == "__main__":
    main()
