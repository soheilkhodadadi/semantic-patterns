# src/analysis/prepare_panel_for_regression.py
import os
import pandas as pd
import numpy as np

INP = "data/processed/panel/panel_ai_patents_controls.csv"
OUT = "data/processed/panel/panel_reg_ready.csv"
QC  = "reports/panel_clean_qc.md"

NUM_COLS_LIKELY = [
    "n_total","n_A","n_S","n_I","ai_total","share_A","share_S","share_I","doc_count",
    "patents_ai","patents_total",
    "ln_assets","leverage","cash","rd_intensity","capx_at","roa","sales_growth","emp",
    "sic"
]

def norm_cik(x):
    s = "".join(c for c in str(x) if c.isdigit())
    return s.zfill(10) if s else ""

def df_to_md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"]*len(cols)) + " |"]
    for _,r in df.iterrows():
        out.append("| " + " | ".join("" if pd.isna(r[c]) else str(r[c]) for c in cols) + " |")
    return "\n".join(out)

def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    os.makedirs(os.path.dirname(QC), exist_ok=True)

    df = pd.read_csv(INP)

    # keys
    if "cik" not in df or "year" not in df:
        raise ValueError("panel must include cik and year")
    df["cik"]  = df["cik"].apply(norm_cik)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

    # numeric coercions
    for c in [c for c in NUM_COLS_LIKELY if c in df.columns]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # nonnegative checks
    for c in ["n_total","n_A","n_S","n_I","ai_total","patents_ai","patents_total","doc_count"]:
        if c in df.columns:
            df.loc[df[c] < 0, c] = np.nan

    # recompute shares if counts present and shares missing/invalid
    has_counts = all(c in df.columns for c in ["n_A","n_S","n_I"])
    if has_counts:
        total_counts = df[["n_A","n_S","n_I"]].sum(axis=1)
        need_shares = any(col not in df.columns for col in ["share_A","share_S","share_I"])
        if need_shares:
            df["share_A"] = df["n_A"] / total_counts.replace(0, np.nan)
            df["share_S"] = df["n_S"] / total_counts.replace(0, np.nan)
            df["share_I"] = df["n_I"] / total_counts.replace(0, np.nan)

    # industry buckets from SIC (temporary FE proxy)
    if "sic" in df.columns:
        df["sic2"] = (pd.to_numeric(df["sic"], errors="coerce") // 100).astype("Int64")

    # transforms
    if "patents_ai" in df.columns:
        df["patents_ai_log"] = np.log1p(df["patents_ai"])
    if "patents_total" in df.columns:
        df["patents_total_log"] = np.log1p(df["patents_total"])

    # Minimal set for baseline model
    needed = ["cik","year","n_A","n_S","n_I","ln_assets"]
    dep    = ["patents_ai","patents_ai_log"]
    fe     = ["sic2"]  # change to ff12 later
    required = [c for c in needed + dep + fe if c in df.columns]

    before = len(df)
    reg_df = df.dropna(subset=required, how="any").copy()
    after = len(reg_df)

    # basic sanity
    dup = reg_df.duplicated(subset=["cik","year"]).sum()

    # save
    reg_df.to_csv(OUT, index=False)

    # QC
    miss = df[required].isna().mean().sort_values(ascending=False).round(3).to_frame("missing_share").reset_index().rename(columns={"index":"column"})
    kept_rate = round(after/max(1,before), 3)
    with open(QC, "w") as f:
        f.write("# Panel Cleaning QC\n\n")
        f.write(f"- Input rows: **{before}**\n")
        f.write(f"- Kept rows (complete for baseline): **{after}** (rate={kept_rate})\n")
        f.write(f"- Duplicate (cik,year) in kept: **{int(dup)}**\n\n")
        f.write("## Missingness (required fields)\n\n")
        f.write(df_to_md(miss))

    print(f"[✓] Wrote {OUT} ({after} rows) and {QC}")

if __name__ == "__main__":
    main()