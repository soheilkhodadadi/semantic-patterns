# src/patents/build_company_lookup.py
"""
Builds a normalized company lookup table for patents work.

Inputs
------
data/metadata/company_list_50.csv
    Expected to contain at least a company name. Optionally CIK and/or ticker.
    Column names are inferred flexibly (e.g., 'company', 'Company Name',
    'issuer', 'name', 'cik', 'CIK', 'ticker', 'Ticker', etc.).

Outputs
-------
data/metadata/company_lookup.csv
    Columns: cik, name, name_clean, ticker (optional if present)

Optional
--------
data/metadata/company_aliases.csv (only if an 'alias' column exists)
    Columns: cik, name, alias, alias_clean

Run
---
python src/patents/build_company_lookup.py
"""

import os
import re
import sys
import pandas as pd

SRC = "data/metadata/company_list_50.csv"
OUT_MAIN = "data/metadata/company_lookup.csv"
OUT_ALIASES = "data/metadata/company_aliases.csv"


def clean_company_name(name: str) -> str:
    """Lowercase, strip suffixes, remove punctuation/extra whitespace."""
    if pd.isna(name):
        return ""
    s = str(name).lower()

    # Common corporate suffixes
    suffixes = [
        r"\s+inc\.?$",
        r"\s+corp\.?$",
        r"\s+corporation$",
        r"\s+ltd\.?$",
        r"\s+llc$",
        r"\s+plc$",
        r"\s+co\.?$",
        r"\s+company$",
        r"\s+holdings?$",
        r"\s+group$",
    ]
    for suf in suffixes:
        s = re.sub(suf, "", s)

    # Remove punctuation except spaces/word chars
    s = re.sub(r"[^\w\s]", "", s)
    # Collapse whitespace
    s = " ".join(s.split())
    return s.strip()


def normalize_cik(x) -> str:
    """Return zero-padded 10-digit CIK or empty string if missing/invalid."""
    if pd.isna(x) or str(x).strip() == "":
        return ""
    # keep digits only
    digits = re.sub(r"\D", "", str(x))
    if digits == "":
        return ""
    return digits.zfill(10)


def pick_first_nonempty(series: pd.Series) -> str:
    """Helper to pick the first non-empty string from a Series row-wise."""
    for v in series:
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def infer_columns(df: pd.DataFrame):
    """Find best-matching columns for name / cik / ticker / alias."""
    cols = {c.lower(): c for c in df.columns}

    def find(*cands):
        for c in cands:
            if c in cols:
                return cols[c]
        return None

    name_col = find("name", "company", "company_name", "issuer", "issuer_name", "conm")
    cik_col = find("cik", "cik_code", "sec_cik")
    ticker_col = find("ticker", "symbol", "tic")
    alias_col = find("alias", "alt_name", "aka")

    if not name_col:
        raise ValueError(
            "Could not find a company name column in company_list_50.csv. "
            "Expected one of: name, company, company_name, issuer, issuer_name, conm."
        )

    return name_col, cik_col, ticker_col, alias_col


def main():
    if not os.path.exists(SRC):
        print(f"[x] Missing input: {SRC}", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(SRC)

    name_col, cik_col, ticker_col, alias_col = infer_columns(df)

    # Build canonical columns
    out = pd.DataFrame()
    out["name"] = df[name_col].astype(str).str.strip()

    if cik_col:
        out["cik"] = df[cik_col].apply(normalize_cik)
    else:
        out["cik"] = ""  # allow blank; later we can fill via crosswalks

    if ticker_col:
        out["ticker"] = df[ticker_col].astype(str).str.upper().str.strip()
    else:
        out["ticker"] = ""

    out["name_clean"] = out["name"].apply(clean_company_name)

    # Drop rows with empty cleaned names
    out = out[out["name_clean"] != ""].copy()

    # De-dup logic:
    # 1) Prefer distinct CIKs when present.
    # 2) Otherwise de-dup on cleaned name.
    # If multiple rows share same non-empty cik, keep the first.
    if (out["cik"] != "").any():
        out = (
            out.sort_values(["cik", "name"])  # stable
            .drop_duplicates(subset=["cik"], keep="first")
        )

    # Now de-dup by cleaned name (for blanks or accidental repeats)
    out = out.sort_values(["name_clean", "name"]).drop_duplicates(
        subset=["name_clean"], keep="first"
    )

    # Reorder columns
    cols = ["cik", "name", "name_clean"]
    if "ticker" in out.columns:
        cols.append("ticker")
    out = out[cols].reset_index(drop=True)

    # Basic validations
    n_total = len(out)
    n_blank_cik = (out["cik"] == "").sum()
    print(f"[✓] Companies in lookup: {n_total}")
    if n_blank_cik > 0:
        print(f"[!] {n_blank_cik} companies missing CIK (will rely on crosswalks later).")

    # Ensure output dir
    os.makedirs(os.path.dirname(OUT_MAIN), exist_ok=True)
    out.to_csv(OUT_MAIN, index=False)
    print(f"[✓] Saved lookup to: {OUT_MAIN}")

    # Optional aliases file if provided
    if alias_col:
        ali = df[[name_col, alias_col]].copy()
        ali.columns = ["name", "alias"]
        ali["name_clean"] = ali["name"].apply(clean_company_name)
        ali["alias_clean"] = ali["alias"].apply(clean_company_name)
        # Join CIK back (if we had one for that name)
        ali = ali.merge(out[["name", "cik"]], on="name", how="left")
        ali = ali[(ali["alias_clean"] != "") & (ali["name_clean"] != "")]
        if len(ali):
            ali = ali[["cik", "name", "alias", "alias_clean"]]
            ali.to_csv(OUT_ALIASES, index=False)
            print(f"[✓] Saved aliases to: {OUT_ALIASES}")

    # Show head for sanity
    print("\nSample:")
    print(out.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
