# src/analysis/run_regressions.py
import os, argparse
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.iolib.summary2 import summary_col

def add_engineered_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Expect columns: cik, year, patents_ai, n_A, n_S, n_I, n_total, ln_assets, leverage, cash, rd_intensity, capx_at, roa, sales_growth, emp
    for y in ["patents_ai"]:
        df[f"log_{y}"] = np.log1p(df[y].fillna(0))
    # Shares (guard against zeros)
    df["ActShare"] = df["n_A"] / df["n_total"].replace(0, np.nan)
    df["SpecShare"] = df["n_S"] / df["n_total"].replace(0, np.nan)
    df["SpecMinusAct"] = df["SpecShare"] - df["ActShare"]
    df["log_docs"] = np.log1p(df["n_total"].fillna(0))
    return df

def make_lagged(df, k):
    # For outcome at t+k, create patents_{t+k} by grouping on firm and shifting backward
    df = df.sort_values(["cik","year"]).copy()
    df[f"patents_ai_lead{k}"] = df.groupby("cik")["patents_ai"].shift(-k)
    df[f"log_patents_ai_lead{k}"] = np.log1p(df[f"patents_ai_lead{k}"])
    return df

def fit_ols_fe(formula, df, cluster="cik"):
    # Firm & year FE via dummies: C(cik) + C(year)
    m = smf.ols(formula, data=df).fit(
        cov_type="cluster",
        cov_kwds={"groups": df[cluster]}
    )
    return m

def run_all_models(df, outdir):
    os.makedirs(outdir, exist_ok=True)
    results = {}

    # ---- Baseline OLS FE, k = 0,1,2 on log patents
    for k in [0,1,2]:
        d = make_lagged(df, k)
        keep = d[~d[f"log_patents_ai_lead{k}"].isna()].copy()

        # Levels (n_A, n_S) with FE + controls
        f1 = f"log_patents_ai_lead{k} ~ n_A + n_S + ln_assets + leverage + cash + rd_intensity + capx_at + roa + sales_growth + emp + C(cik) + C(year)"
        res1 = fit_ols_fe(f1, keep)
        results[f"OLS_k{k}_levels"] = res1

        # Shares with exposure control
        f2 = f"log_patents_ai_lead{k} ~ ActShare + SpecShare + log_docs + ln_assets + leverage + cash + rd_intensity + capx_at + roa + sales_growth + emp + C(cik) + C(year)"
        res2 = fit_ols_fe(f2, keep)
        results[f"OLS_k{k}_shares"] = res2

    # ---- Binary “any AI patent” (k=1 as example)
    d1 = make_lagged(df, 1)
    d1 = d1.assign(any_pat_1=(d1["patents_ai_lead1"] > 0).astype(int))
    f_bin = "any_pat_1 ~ n_A + n_S + ln_assets + leverage + cash + rd_intensity + capx_at + roa + sales_growth + emp + C(cik) + C(year)"
    res_bin = fit_ols_fe(f_bin, d1.dropna(subset=["any_pat_1"]))
    results["LPM_anypat_k1"] = res_bin

    # ---- Save stacked table (CSV + LaTeX)
    ordered = [results[k] for k in sorted(results.keys())]
    sc = summary_col(ordered, stars=True, float_format="%.3f",
                     model_names=list(sorted(results.keys())),
                     info_dict={"N":lambda x: f"{int(x.nobs)}"})
    with open(os.path.join(outdir, "baseline_table.txt"), "w") as f:
        f.write(sc.as_text())
    with open(os.path.join(outdir, "baseline_table.tex"), "w") as f:
        f.write(sc.as_latex())

    # Per-model CSV of coefficients
    rows = []
    for name, m in results.items():
        coefs = m.params.to_frame("coef")
        coefs["se"] = m.bse
        coefs["t"] = m.tvalues
        coefs["p"] = m.pvalues
        coefs["model"] = name
        coefs["N"] = m.nobs
        rows.append(coefs.reset_index().rename(columns={"index":"term"}))
    out = pd.concat(rows, ignore_index=True)
    out.to_csv(os.path.join(outdir, "baseline_coefficients.csv"), index=False)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", default="data/processed/panel/panel_reg_ready.csv")
    ap.add_argument("--outdir", default="results/01_baseline/tables")
    args = ap.parse_args()

    df = pd.read_csv(args.panel)
    df = add_engineered_cols(df)
    # Basic cleaning: drop rows missing key regressors (kept minimal)
    needed = ["cik","year","patents_ai","n_A","n_S","n_total","ln_assets","leverage","cash","rd_intensity","capx_at","roa","sales_growth","emp"]
    df = df.dropna(subset=[c for c in needed if c in df.columns])

    run_all_models(df, args.outdir)

if __name__ == "__main__":
    main()