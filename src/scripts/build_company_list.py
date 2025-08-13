"""
Build a reproducible company list (~50 firms) from cik_ticker_list.csv.

Inputs:
  data/external/cik_ticker_list.csv  # your existing CIK–ticker–name table

Outputs:
  data/metadata/company_list_50.csv  # columns: cik, ticker, company_name
"""

import os
import random
import pandas as pd

IN  = "data/external/cik_ticker_list.csv"   # <- put your cik_ticker_list.csv here
OUT = "data/metadata/company_list_50.csv"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# Reproducibility
random.seed(42)

df = pd.read_csv(IN)
# Try to keep only US public names with both CIK & ticker
keep_cols = [c for c in df.columns if c.lower() in {"cik","ticker","name","company_name"}]
df = df[keep_cols].rename(columns={"name":"company_name"})
df = df.dropna(subset=["cik"]).drop_duplicates(subset=["cik"])
df["cik"] = df["cik"].astype(str).str.extract(r"(\d+)")  # strip weird formatting
df = df[df["cik"].str.len() > 0]

# Sample 50 (or fewer if source is short)
sample_n = min(50, len(df))
sample_idx = random.sample(range(len(df)), sample_n)
out = df.iloc[sample_idx].reset_index(drop=True)

out = out[["cik"] + [c for c in out.columns if c in {"ticker","company_name"}]]
out.to_csv(OUT, index=False)
print(f"[✓] Wrote {len(out)} firms → {OUT}")
