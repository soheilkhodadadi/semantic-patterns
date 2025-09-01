# src/aggregation/merge_ai_with_patents.py
"""
Merge AI sentence frequencies (firm-year) with patents (firm-year).

Inputs (defaults can be overridden via CLI):
  --ai-freq   data/processed/ai_frequencies_by_firm_year.csv
  --patents   data/processed/patents/ai_patent_counts_filtered_2019plus.csv
  --lookup    data/metadata/company_lookup.csv

Output:
  data/final/ai_freq_patents_firm_year.csv

Notes
-----
- Left-join on (cik, year) to keep all AI frequency rows.
- Adds: patents_ai, patents_total (0 if missing), and ai_share_patents.
- Enriches with firm 'name' and 'ticker' from lookup (by cik).
"""

import argparse
import os
import re
import pandas as pd

def normalize_cik(x) -> str:
    if pd.isna(x) or str(x).strip() == "":
        return ""
    digits = re.sub(r"\D", "", str(x))
    return digits.zfill(10) if digits else ""

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ai-freq", default="data/processed/ai_frequencies_by_firm_year.csv")
    p.add_argument("--patents", default="data/processed/patents/ai_patent_counts_filtered_2019plus.csv")
    p.add_argument("--lookup", default="data/metadata/company_lookup.csv")
    p.add_argument("--out", default="data/final/ai_freq_patents_firm_year.csv")
    args = p.parse_args()

    # --- Load AI frequencies ---
    if not os.path.exists(args.ai_freq):
        raise FileNotFoundError(f"Missing AI frequency file: {args.ai_freq}")
    ai = pd.read_csv(args.ai_freq)

    # Expect keys and counts
    required_ai = {"cik", "year"}
    if not required_ai.issubset(set(ai.columns)):
        raise ValueError(f"{args.ai_freq} must contain at least columns: {required_ai}")

    # Normalize keys / dtypes
    ai["cik"] = ai["cik"].apply(normalize_cik)
    ai["year"] = ai["year"].astype(int)

    # If ai_total not present, derive from n_A + n_S when available
    if "ai_total" not in ai.columns:
        if {"n_A", "n_S"}.issubset(ai.columns):
            ai["ai_total"] = ai["n_A"].fillna(0) + ai["n_S"].fillna(0)
        else:
            ai["ai_total"] = pd.NA

    # --- Load patents counts ---
    if not os.path.exists(args.patents):
        raise FileNotFoundError(f"Missing patents file: {args.patents}")
    pt = pd.read_csv(args.patents)

    # Standardize expected fields from our extractor
    # (cik, name, year, patents_total, patents_ai, ai_share)
    required_pt = {"cik", "year"}
    if not required_pt.issubset(set(pt.columns)):
        raise ValueError(f"{args.patents} must contain keys: {required_pt}")

    pt["cik"] = pt["cik"].apply(normalize_cik)
    pt["year"] = pt["year"].astype(int)

    # Keep only the columns we need for merge; rename to avoid name collision
    keep_cols = ["cik", "year"]
    if "patents_ai" in pt.columns: keep_cols.append("patents_ai")
    if "patents_total" in pt.columns: keep_cols.append("patents_total")
    if "ai_share" in pt.columns: keep_cols.append("ai_share")

    pt = pt[keep_cols].copy()
    if "patents_ai" not in pt.columns:   pt["patents_ai"] = 0
    if "patents_total" not in pt.columns: pt["patents_total"] = 0
    # Guard against division by zero
    pt["ai_share"] = pt.get("ai_share", pd.Series([pd.NA]*len(pt)))
    pt["patents_ai"] = pd.to_numeric(pt["patents_ai"], errors="coerce").fillna(0).astype(int)
    pt["patents_total"] = pd.to_numeric(pt["patents_total"], errors="coerce").fillna(0).astype(int)

    # --- Load lookup for ticker/name enrichment ---
    if not os.path.exists(args.lookup):
        raise FileNotFoundError(f"Missing lookup: {args.lookup}")
    lk = pd.read_csv(args.lookup)
    # expected: cik, name, ticker (ticker optional)
    for col in ["cik", "name"]:
        if col not in lk.columns:
            raise ValueError(f"{args.lookup} must have at least columns 'cik' and 'name'")
    if "ticker" not in lk.columns:
        lk["ticker"] = ""

    lk["cik"] = lk["cik"].apply(normalize_cik)
    lk = lk[["cik", "name", "ticker"]].drop_duplicates("cik")

    # --- Merge ---
    base_rows = len(ai)
    # Avoid accidental dupes: ensure uniqueness on base keys
    if ai.duplicated(["cik","year"]).any():
        # If this happens, the Stage-5 aggregator must be fixed first
        raise ValueError("Duplicate (cik, year) in AI frequency file; please de-duplicate upstream.")

    merged = (ai
              .merge(pt, on=["cik","year"], how="left", validate="one_to_one")
              .merge(lk, on="cik", how="left"))

    # Fill patents fields that were missing
    for col, val in [("patents_ai", 0), ("patents_total", 0)]:
        if col in merged.columns:
            merged[col] = merged[col].fillna(val)
    if "ai_share" in merged.columns:
        # rename to clarify it’s patents-based share
        merged = merged.rename(columns={"ai_share": "ai_share_patents"})

    # Reorder for readability
    preferred = [
        "cik", "ticker", "name", "year",
        # AI sentence counts (if present)
        "n_total","n_A","n_S","n_I","ai_total","share_A","share_S","share_I","doc_count",
        # Patents
        "patents_total","patents_ai","ai_share_patents"
    ]
    cols_present = [c for c in preferred if c in merged.columns]
    other_cols = [c for c in merged.columns if c not in cols_present]
    merged = merged[cols_present + other_cols]

    # --- Output ---
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    merged.to_csv(args.out, index=False)

    # --- Console QA ---
    with_patents = (merged["patents_total"] > 0).sum() if "patents_total" in merged.columns else 0
    with_ai_patents = (merged["patents_ai"] > 0).sum() if "patents_ai" in merged.columns else 0
    print(f"[✓] Wrote merged panel: {args.out}")
    print(f"Rows (firm-year) in AI base: {base_rows}")
    print(f"Rows with any patents:      {with_patents}")
    print(f"Rows with AI patents:       {with_ai_patents}")

    if "patents_ai" in merged.columns and merged["patents_ai"].max() > 0:
        tops = (merged.sort_values("patents_ai", ascending=False)
                      .head(10)[["cik","ticker","name","year","patents_ai","patents_total"]])
        print("\nTop firm-years by AI patents:")
        for _, r in tops.iterrows():
            print(f" - {r['name']} ({r['ticker']}) {r['year']}: AI {int(r['patents_ai'])} / Total {int(r['patents_total'])}")

if __name__ == "__main__":
    main()