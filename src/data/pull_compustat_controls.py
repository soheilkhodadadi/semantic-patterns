# src/data/pull_compustat_controls.py
"""
Pull Compustat controls from WRDS, build a CIK↔GVKEY crosswalk for your 50 firms,
compute standard ratios, winsorize, and write controls_by_firm_year.csv.

Usage
-----
python src/data/pull_compustat_controls.py \
    --start-year 2018 --end-year 2025 --align fyear

Requires
--------
- .env with:
    WRDS_USER=your_wrds_username
    WRDS_PASS=your_wrds_password
    WRDS_DB_HOST=wrds-pgdata.wharton.upenn.edu
    WRDS_DB_PORT=9737
- data/metadata/company_list_50.csv  (CIK and/or Ticker and Name)

Outputs
-------
- data/externals/crosswalks/cik_gvkey.csv
    columns: cik, gvkey, ticker_comp, name_comp, sic
- data/interim/controls/controls_by_firm_year.csv
    keys: cik, year  (+ gvkey, sic)
    vars: ln_assets, leverage, cash, rd_intensity, capx_at, roa, sales_growth, emp
- reports/controls_qc.md  (coverage & sanity summary)
"""

import os
import re
import argparse
from textwrap import dedent

import numpy as np
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor  # noqa: F401
from dotenv import load_dotenv

# ---------------------------
# Helpers
# ---------------------------

def normalize_cik(x: str) -> str:
    if x is None:
        return ""
    s = re.sub(r"\D", "", str(x))
    return s.zfill(10) if s else ""

def normalize_ticker(x: str) -> str:
    if x is None:
        return ""
    return str(x).upper().strip()

def winsorize01_series(s: pd.Series) -> pd.Series:
    if s.dropna().empty:
        return s
    q1, q99 = s.quantile(0.01), s.quantile(0.99)
    return s.clip(q1, q99)

def ensure_dirs():
    os.makedirs("data/externals/crosswalks", exist_ok=True)
    os.makedirs("data/interim/controls", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

# ---------------------------
# Data loaders
# ---------------------------

def load_company_list(path="data/metadata/company_list_50.csv") -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing company list: {path}")
    df = pd.read_csv(path)
    # Flexible column inference
    cols = {c.lower(): c for c in df.columns}
    name_col = next((cols[k] for k in ["name","company","company_name","issuer","issuer_name","conm"] if k in cols), None)
    cik_col  = next((cols[k] for k in ["cik","sec_cik","cik_code"] if k in cols), None)
    tic_col  = next((cols[k] for k in ["ticker","tic","symbol"] if k in cols), None)

    if name_col is None:
        raise ValueError("company_list_50.csv must contain a company name column (e.g., name/company/company_name/issuer).")

    out = pd.DataFrame()
    out["name_src"] = df[name_col].astype(str).str.strip()
    out["cik"] = df[cik_col].apply(normalize_cik) if cik_col else ""
    out["ticker_src"] = df[tic_col].apply(normalize_ticker) if tic_col else ""
    return out

def connect_wrds():
    load_dotenv()
    user = os.getenv("WRDS_USER")
    pwd  = os.getenv("WRDS_PASS")
    host = os.getenv("WRDS_DB_HOST", "wrds-pgdata.wharton.upenn.edu")
    port = int(os.getenv("WRDS_DB_PORT", "9737"))
    if not user or not pwd:
        raise EnvironmentError("WRDS credentials not found in .env (WRDS_USER / WRDS_PASS).")
    conn = psycopg2.connect(
        dbname="wrds",
        user=user,
        password=pwd,
        host=host,
        port=port
    )
    return conn

# ---------------------------
# Crosswalk builder
# ---------------------------

def build_cik_gvkey_crosswalk(conn, companies: pd.DataFrame) -> pd.DataFrame:
    """
    Build a CIK↔GVKEY crosswalk using WRDS comp.company and your 50-firm list.
    Strategy:
      1) Pull gvkey, cik, ticker, name, sic from comp.company.
      2) Normalize CIK (10-digit) and Ticker.
      3) Keep only rows whose CIK or Ticker matches your 50-firm list.
      4) Deduplicate (prefer CIK matches over ticker-only).
    """
    # Try selecting ticker from comp.company; some WRDS setups don't expose `tic` in this table
    try:
        sql = dedent("""
            SELECT gvkey,
                   CASE WHEN cik IS NULL THEN NULL ELSE cik::text END AS cik,
                   UPPER(tic) AS ticker_comp,
                   conm      AS name_comp,
                   sic
            FROM comp.company
        """)
        comp = pd.read_sql(sql, conn)
    except Exception:
        print("[!] 'tic' not found in comp.company (or SELECT failed). Falling back to CIK/name only.")
        sql = dedent("""
            SELECT gvkey,
                   CASE WHEN cik IS NULL THEN NULL ELSE cik::text END AS cik,
                   conm      AS name_comp,
                   sic
            FROM comp.company
        """)
        comp = pd.read_sql(sql, conn)
        comp["ticker_comp"] = ""

    comp["cik"] = comp["cik"].apply(normalize_cik)
    comp["ticker_comp"] = comp["ticker_comp"].fillna("").astype(str).str.upper().str.strip()

    # Match universe
    ciks = set([c for c in companies["cik"].tolist() if c])
    tics = set([t for t in companies["ticker_src"].tolist() if t])

    # Keep rows with CIK or Ticker hit
    if "ticker_comp" in comp.columns and comp["ticker_comp"].notna().any():
        comp_keep = comp[(comp["cik"].isin(ciks)) | (comp["ticker_comp"].isin(tics))].copy()
    else:
        comp_keep = comp[(comp["cik"].isin(ciks))].copy()

    # If both empty (e.g., list lacks cik/ticker), fallback to fuzzy on name (very light)
    if comp_keep.empty:
        print("[!] No matches by CIK/Ticker. Falling back to lightweight name match.")
        names = set([n.lower() for n in companies["name_src"].tolist() if isinstance(n, str)])
        comp["name_lower"] = comp["name_comp"].str.lower()
        comp_keep = comp[comp["name_lower"].isin(names)].copy()
        comp_keep.drop(columns=["name_lower"], inplace=True, errors="ignore")

    # Deduplicate by preferring cik matches; then by ticker; keep first gvkey
    comp_keep["match_key"] = np.where(comp_keep["cik"].isin(ciks), "cik", np.where(comp_keep["ticker_comp"].isin(tics), "ticker", "name"))
    comp_keep.sort_values(["match_key","cik","ticker_comp","gvkey"], inplace=True)
    # One row per cik if cik exists, else per ticker, else per name
    # Build a consolidated mapping
    # First, if we have cik: one row per cik
    have_cik = comp_keep[comp_keep["match_key"]=="cik"]
    if "ticker_comp" in comp_keep.columns and comp_keep["ticker_comp"].notna().any():
        have_tic = comp_keep[(comp_keep["match_key"]=="ticker") & (~comp_keep["ticker_comp"].isin(have_cik["ticker_comp"]))]  # may be empty
    else:
        have_tic = comp_keep.iloc[0:0].copy()

    cross = pd.concat([have_cik.drop_duplicates(subset=["cik"]),
                       have_tic.drop_duplicates(subset=["ticker_comp"])], ignore_index=True)

    # Attach original company names where available (by cik or ticker)
    companies["cik_nz"] = companies["cik"].replace("", np.nan)
    companies["ticker_nz"] = companies["ticker_src"].replace("", np.nan)
    cross = cross.merge(companies[["cik_nz","ticker_nz","name_src"]],
                        left_on="cik", right_on="cik_nz", how="left")
    cross = cross.merge(companies[["cik_nz","ticker_nz","name_src"]],
                        left_on="ticker_comp", right_on="ticker_nz", how="left", suffixes=("","_by_tic"))

    # Prefer name from cik match then ticker match then comp name
    cross["name_src_final"] = cross["name_src"].fillna(cross["name_src_by_tic"]).fillna(cross["name_comp"])
    cross = cross.rename(columns={"name_src_final":"name"})
    cross = cross[["cik","gvkey","ticker_comp","name","sic"]].drop_duplicates()

    # Basic report
    print(f"[✓] Crosswalk rows: {len(cross)} (unique firms from your 50)")
    missing_cik = (cross["cik"]=="").sum()
    if missing_cik:
        print(f"[!] {missing_cik} rows missing CIK in crosswalk (ticker/name-matched).")
    return cross

# ---------------------------
# Compustat funda pull
# ---------------------------

def pull_funda(conn, gvkeys: list, start_year: int, end_year: int) -> pd.DataFrame:
    """
    Use an explicit IN (%s, %s, ...) list and pass a flat params sequence.
    This avoids 'can't adapt type list' from pandas/psycopg2 when using ANY(%s).
    """
    if not gvkeys:
        return pd.DataFrame()

    # Make sure we have clean string gvkeys (drop empties/NaN)
    gvkeys = [str(g).strip() for g in gvkeys if pd.notna(g) and str(g).strip() != ""]
    if not gvkeys:
        return pd.DataFrame()

    # Build placeholders for the IN clause
    placeholders = ", ".join(["%s"] * len(gvkeys))

    sql = dedent(f"""
        SELECT gvkey, datadate, fyear, fyr, indfmt, consol, datafmt, popsrc,
               at, dltt, che, xrd, capx, ib, ni, oibdp, sale, emp
        FROM comp.funda
        WHERE indfmt='INDL' AND consol='C' AND datafmt='STD' AND popsrc='D'
          AND gvkey IN ({placeholders})
          AND fyear BETWEEN %s AND %s;
    """)

    # Pass scalars only (flattened)
    params = gvkeys + [start_year, end_year]

    df = pd.read_sql(sql, conn, params=params)
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df["fyear"] = pd.to_numeric(df["fyear"], errors="coerce").astype("Int64")
    return df

# ---------------------------
# Controls computation
# ---------------------------

def compute_controls(funda: pd.DataFrame, align: str="fyear") -> pd.DataFrame:
    if funda.empty:
        return funda

    # Choose the year alignment
    if align == "calendar":
        funda["year"] = funda["datadate"].dt.year
    else:
        funda["year"] = funda["fyear"].astype("Int64")

    # For duplicates within (gvkey, year): keep the latest datadate
    funda = funda.sort_values(["gvkey","year","datadate"]).drop_duplicates(subset=["gvkey","year"], keep="last")

    # Controls
    safe_at = funda["at"].replace(0, np.nan)
    funda["ln_assets"]    = np.log(safe_at)
    funda["leverage"]     = funda["dltt"] / safe_at
    funda["cash"]         = funda["che"] / safe_at
    funda["rd_intensity"] = funda["xrd"] / safe_at
    funda["capx_at"]      = funda["capx"] / safe_at
    funda["roa"]          = funda["ni"] / safe_at

    # Sales growth
    funda = funda.sort_values(["gvkey","year"])
    funda["sale_lag"] = funda.groupby("gvkey")["sale"].shift(1)
    funda["sales_growth"] = (funda["sale"] - funda["sale_lag"]) / funda["sale_lag"].abs()

    # Winsorize within year
    for col in ["leverage","cash","rd_intensity","capx_at","roa","sales_growth"]:
        funda[col] = funda.groupby("year")[col].transform(winsorize01_series)

    # Keep relevant columns
    keep = ["gvkey","year","ln_assets","leverage","cash","rd_intensity","capx_at","roa","sales_growth","emp"]
    funda = funda[keep].copy()
    return funda

# ---------------------------
# QC report
# ---------------------------

def write_qc_report(path_md: str, cross: pd.DataFrame, controls: pd.DataFrame, start_year: int, end_year: int):
    lines = []
    lines.append("# Controls QC\n")
    lines.append(f"- Years: {start_year}–{end_year}")
    lines.append(f"- Firms in crosswalk: **{len(cross)}**")
    lines.append(f"- Firm-years in controls: **{len(controls)}**")
    if not controls.empty:
        yr_min = int(pd.to_numeric(controls['year'], errors='coerce').min())
        yr_max = int(pd.to_numeric(controls['year'], errors='coerce').max())
        lines.append(f"- Year span in controls: {yr_min}–{yr_max}")
        miss_rate = controls.isna().mean().round(3)
        miss_tbl = miss_rate.to_frame("missing_share").reset_index().rename(columns={"index":"column"})
        lines.append("\n## Missingness\n")
        lines.append(miss_tbl.to_markdown(index=False))
    with open(path_md, "w") as f:
        f.write("\n".join(lines))
    print(f"[✓] Wrote QC report: {path_md}")

# ---------------------------
# Main
# ---------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start-year", type=int, default=2018)
    ap.add_argument("--end-year", type=int, default=2025)
    ap.add_argument("--align", choices=["fyear","calendar"], default="fyear",
                    help="Year alignment for Compustat (default: fyear).")
    ap.add_argument("--company-list", default="data/metadata/company_list_50.csv")
    ap.add_argument("--out-crosswalk", default="data/externals/crosswalks/cik_gvkey.csv")
    ap.add_argument("--out-controls", default="data/interim/controls/controls_by_firm_year.csv")
    ap.add_argument("--out-qc", default="reports/controls_qc.md")
    args = ap.parse_args()

    ensure_dirs()

    # Load your 50 firms
    companies = load_company_list(args.company_list)
    print(f"[✓] Loaded {len(companies)} companies from {args.company_list}")

    # Connect and build crosswalk
    conn = connect_wrds()
    try:
        cross = build_cik_gvkey_crosswalk(conn, companies)
        cross.to_csv(args.out_crosswalk, index=False)
        print(f"[✓] Saved crosswalk to {args.out_crosswalk}")

        # Pull funda for the gvkeys we found
        gvkeys = cross["gvkey"].dropna().astype(str).unique().tolist()
        print(f"🔎 Pulling Compustat funda for {len(gvkeys)} gvkeys {args.start_year}–{args.end_year} ...")
        funda = pull_funda(conn, gvkeys, args.start_year, args.end_year)

    finally:
        conn.close()

    if funda.empty:
        print("[!] No funda rows returned. Check year window and gvkeys.")
        # still write empty outputs to avoid pipeline breaks
        pd.DataFrame(columns=["cik","year","gvkey","sic","ln_assets","leverage","cash","rd_intensity","capx_at","roa","sales_growth","emp"])\
          .to_csv(args.out_controls, index=False)
        write_qc_report(args.out_qc, cross, pd.DataFrame(), args.start_year, args.end_year)
        return

    # Compute controls and merge back to cik via crosswalk
    controls = compute_controls(funda, align=args.align)
    controls = controls.merge(cross[["cik","gvkey","sic"]].drop_duplicates(), on="gvkey", how="left")
    # Zero-pad CIK
    controls["cik"] = controls["cik"].apply(normalize_cik)

    # Order columns
    cols = ["cik","year","gvkey","sic","ln_assets","leverage","cash","rd_intensity","capx_at","roa","sales_growth","emp"]
    controls = controls[cols].sort_values(["cik","year","gvkey"])

    # Write outputs
    controls.to_csv(args.out_controls, index=False)
    print(f"[✓] Saved controls to {args.out_controls} (rows={len(controls)})")

    # QC report
    write_qc_report(args.out_qc, cross, controls, args.start_year, args.end_year)

if __name__ == "__main__":
    main()