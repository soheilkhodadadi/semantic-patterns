"""
Build a reproducible firm list (~50 CIKs) that **have a 10‑K in each year 2021–2024**
**and** have a valid mapping to both `ticker` and `company_name` in your CIK map.
Also write out the exact 200 filing rows (50 firms × 4 years) for downstream copying.

Inputs
------
- data/metadata/available_filings_index.csv   # columns: cik, year, form, filename, path
- data/external/cik_ticker_list.csv           # CIK↔ticker↔name mapping (your existing table)

Outputs
-------
- data/metadata/company_list_50.csv           # columns: cik, ticker, company_name  (no missing values)
- data/metadata/sample_filings_200.csv        # columns: cik, year, form, filename, path
- data/metadata/company_mapping_gaps.csv      # CIKs with missing ticker and/or name (for debugging)

Usage
-----
$ python src/scripts/build_company_list.py

Notes
-----
- Deterministic sampling with seed=42
- Only considers 10‑K forms and years in {2021, 2022, 2023, 2024}
- Skips CIKs that are missing any of the 4 required years
- **New:** Only samples from CIKs that have both ticker and company_name present.
"""
from __future__ import annotations
import os
import random
import pandas as pd
from typing import List

# ---- Config -----------------------------------------------------------------
INDEX_PATH = "data/metadata/available_filings_index.csv"
CIK_MAP    = "data/external/cik_ticker_list.csv"
OUT_FIRMS  = "data/metadata/company_list_50.csv"
OUT_FILES  = "data/metadata/sample_filings_200.csv"
OUT_GAPS  = "data/metadata/company_mapping_gaps.csv"

REQUIRED_YEARS: List[int] = [2021, 2022, 2023, 2024]
FORM = "10-K"
SAMPLE_N = 50
RNG_SEED = 42

os.makedirs(os.path.dirname(OUT_FIRMS), exist_ok=True)


def _clean_cik(series: pd.Series) -> pd.Series:
    """Normalize CIK values to zero-padded strings (no spaces or symbols)."""
    s = series.astype(str).str.extract(r"(\d+)", expand=False).fillna("")
    # keep numeric only, left-pad to typical CIK length (10), but don't enforce width
    return s.str.lstrip("0").replace("", pd.NA).fillna("0")


def main() -> None:
    # 1) Load the index of available filings
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(f"Missing index file: {INDEX_PATH}. Run index_sec_filings.py first.")
    idx = pd.read_csv(INDEX_PATH)
    idx.columns = idx.columns.str.strip().str.lower()

    # basic column check
    needed = {"cik", "year", "form", "filename", "path"}
    missing = needed - set(idx.columns)
    if missing:
        raise ValueError(f"Index is missing columns: {sorted(missing)}. Found: {sorted(idx.columns)}")

    # 2) Keep only required 10-Ks in required years
    idx["cik"] = _clean_cik(idx["cik"])
    idx = idx[(idx["form"].str.upper() == FORM) & (idx["year"].isin(REQUIRED_YEARS))].copy()

    # 3) Find CIKs that have all required years
    have_years = (idx.groupby("cik")["year"].nunique() == len(REQUIRED_YEARS))
    eligible_ciks = have_years[have_years].index.tolist()
    if not eligible_ciks:
        raise RuntimeError("No CIKs found with complete 2021–2024 10‑K coverage.")

    idx_eligible = idx[idx["cik"].isin(eligible_ciks)].copy()

    # 4) Load CIK↔ticker↔name mapping and filter to complete rows
    if not os.path.exists(CIK_MAP):
        raise FileNotFoundError(f"Missing CIK map: {CIK_MAP}")
    cm = pd.read_csv(CIK_MAP)
    cm.columns = cm.columns.str.strip().str.lower()
    if "company_name" not in cm.columns and "name" in cm.columns:
        cm = cm.rename(columns={"name": "company_name"})
    if "ticker" not in cm.columns and "symbol" in cm.columns:
        cm = cm.rename(columns={"symbol": "ticker"})
    if "cik" not in cm.columns:
        if "cik_str" in cm.columns:
            cm = cm.rename(columns={"cik_str": "cik"})
        else:
            raise ValueError(f"CIK map lacks a 'cik' column. Columns found: {list(cm.columns)}")
    cm["cik"] = _clean_cik(cm["cik"])

    # 5) Join eligible CIKs to the map and keep only those with BOTH fields present
    elig_map = (
        pd.DataFrame({"cik": eligible_ciks})
        .merge(cm[["cik", "ticker", "company_name"]], on="cik", how="left")
    )
    complete_mask = elig_map["ticker"].notna() & elig_map["ticker"].astype(str).str.strip().ne("") \
                    & elig_map["company_name"].notna() & elig_map["company_name"].astype(str).str.strip().ne("")
    complete = elig_map[complete_mask].copy()
    gaps = elig_map[~complete_mask].copy()
    # write gaps for visibility
    gaps.to_csv(OUT_GAPS, index=False)

    if complete.empty:
        raise RuntimeError("No eligible CIKs have both ticker and company_name in the CIK map.")

    # 6) Deterministic sample from complete CIKs only
    random.seed(RNG_SEED)
    sample_ciks = sorted(random.sample(complete["cik"].tolist(), k=min(SAMPLE_N, len(complete))))

    # 7) Subset the 200 files (CIK × 4 years), ensuring one 10-K per year per CIK
    idx_sample = (
        idx_eligible[idx_eligible["cik"].isin(sample_ciks)]
        .sort_values(["cik", "year", "filename"])
        .groupby(["cik", "year"], as_index=False)
        .head(1)
    )
    coverage = idx_sample.groupby("cik")["year"].nunique()
    bad = coverage[coverage != len(REQUIRED_YEARS)]
    if not bad.empty:
        raise RuntimeError(
            "Some sampled CIKs lost coverage after tie‑breaking. Offenders: "
            + ", ".join(bad.index.tolist())
        )

    # 8) Final firm table (no null ticker/company_name)
    firms = (
        complete[complete["cik"].isin(sample_ciks)]
        .sort_values("cik")[["cik", "ticker", "company_name"]]
    )

    # 9) Write outputs
    firms.to_csv(OUT_FIRMS, index=False)
    idx_sample[["cik", "year", "form", "filename", "path"]].to_csv(OUT_FILES, index=False)

    # 10) Print summary
    print(f"[✓] Eligible CIKs with full 2021–2024 10‑K coverage: {len(eligible_ciks):,}")
    print(f"[✓] With ticker & name available            : {len(complete):,}")
    print(f"[✓] Sampled CIKs                             : {len(sample_ciks)} → {OUT_FIRMS}")
    print(f"[✓] Wrote file list                          : {len(idx_sample):,} rows → {OUT_FILES}")
    print(f"[i] Mapping gaps written to                  : {OUT_GAPS}")
    print("    Years: ", REQUIRED_YEARS)


if __name__ == "__main__":
    main()
