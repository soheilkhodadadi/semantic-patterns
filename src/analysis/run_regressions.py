# src/analysis/run_regressions.py
import os
import argparse
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.iolib.summary2 import summary_col

# ---------- Helpers to make column names robust ----------
ALT_NAMES = {
    "n_A": ["n_A", "n_actionable", "actionable", "nA", "count_actionable", "act_count"],
    "n_S": ["n_S", "n_speculative", "speculative", "nS", "count_speculative", "spec_count"],
    "n_I": ["n_I", "n_irrelevant", "irrelevant", "nI", "count_irrelevant", "irr_count"],
    "n_total": ["n_total", "total_sentences", "doc_count", "sent_count", "total_count"],
    "share_A": ["share_A", "ActShare", "actionable_share", "share_actionable"],
    "share_S": ["share_S", "SpecShare", "speculative_share", "share_speculative"],
    "patents_ai": ["patents_ai", "ai_patents", "patent_ai", "patentsAI"],
    "ln_assets": ["ln_assets", "log_assets", "size", "ln_at"],
    "leverage": ["leverage", "lev", "dltt_at", "debt_ratio"],
    "cash": ["cash", "cash_at", "cash_ratio"],
    "rd_intensity": ["rd_intensity", "xrd_at", "rd_at"],
    "capx_at": ["capx_at", "capx_ratio", "capx_over_at"],
    "roa": ["roa", "return_on_assets"],
    "sales_growth": ["sales_growth", "sales_g", "g_sales"],
    "emp": ["emp", "employees", "employment"],
}


def _resolve(df: pd.DataFrame, key: str):
    for nm in ALT_NAMES[key]:
        if nm in df.columns:
            return nm
    return None


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # counts (if present)
    for k in ["n_A", "n_S", "n_I", "n_total", "patents_ai"]:
        nm = _resolve(df, k)
        if nm and nm != k:
            df[k] = df[nm]
    # controls
    for k in ["ln_assets","leverage","cash","rd_intensity","capx_at","roa","sales_growth","emp"]:
        nm = _resolve(df, k)
        if nm and nm != k:
            df[k] = df[nm]
    # shares (if provided already)
    for k in ["share_A","share_S"]:
        nm = _resolve(df, k)
        if nm and nm != k:
            df[k] = df[nm]
    return df


# ---------- Feature engineering ----------

def add_engineered_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df)
    # Expect at least cik, year, patents_ai
    for y in ["patents_ai"]:
        if y in df.columns:
            df[f"log_{y}"] = np.log1p(df[y].fillna(0))

    # Build shares if we have counts
    if "n_A" in df.columns and "n_S" in df.columns and "n_total" in df.columns:
        denom = df["n_total"].replace(0, np.nan)
        df["ActShare"] = df["n_A"] / denom
        df["SpecShare"] = df["n_S"] / denom
        df["log_docs"] = np.log1p(df["n_total"].fillna(0))
    else:
        # Fall back to any provided share columns
        if "share_A" in df.columns and "share_S" in df.columns:
            df["ActShare"] = df["share_A"]
            df["SpecShare"] = df["share_S"]
        # log_docs only if n_total exists
        if "n_total" in df.columns:
            df["log_docs"] = np.log1p(df["n_total"].fillna(0))

    if "SpecShare" in df.columns and "ActShare" in df.columns:
        df["SpecMinusAct"] = df["SpecShare"] - df["ActShare"]
    else:
        df["SpecMinusAct"] = np.nan
    return df


def make_lagged(df, k):
    df = df.sort_values(["cik","year"]).copy()
    if "patents_ai" in df.columns:
        df[f"patents_ai_lead{k}"] = df.groupby("cik")["patents_ai"].shift(-k)
        df[f"log_patents_ai_lead{k}"] = np.log1p(df[f"patents_ai_lead{k}"])
    return df


def fit_ols_fe(formula, df, cluster="cik"):
    m = smf.ols(formula, data=df).fit(cov_type="cluster", cov_kwds={"groups": df[cluster]})
    return m


def _available_controls(df: pd.DataFrame):
    cand = ["ln_assets","leverage","cash","rd_intensity","capx_at","roa","sales_growth","emp"]
    return [c for c in cand if c in df.columns]


def run_all_models(df, outdir):
    os.makedirs(outdir, exist_ok=True)
    results = {}

    have_counts = all(c in df.columns for c in ["n_A","n_S"])  # n_total optional
    have_shares = all(c in df.columns for c in ["ActShare","SpecShare"])
    controls = _available_controls(df)
    print(f"[info] Using counts? {have_counts}; Using shares? {have_shares}; Controls: {controls}")

    # ---- Baseline OLS FE, k = 0,1,2 on log patents
    for k in [0,1,2]:
        d = make_lagged(df, k)
        dep = f"log_patents_ai_lead{k}"
        if dep not in d.columns:
            continue
        keep = d[~d[dep].isna()].copy()
        fe = "+ C(cik) + C(year)"
        ctrl = (" + " + " + ".join(controls)) if controls else ""

        # Levels (if counts available)
        if have_counts:
            rhs = f"n_A + n_S{ctrl}"
            if "log_docs" in keep.columns:
                # exposure control can be added optionally
                rhs = f"{rhs} + log_docs"
            f1 = f"{dep} ~ {rhs}{fe}"
            try:
                res1 = fit_ols_fe(f1, keep)
                results[f"OLS_k{k}_levels"] = res1
            except Exception as e:
                print(f"[warn] Levels model k={k} failed: {e}")

        # Shares model if shares available
        if have_shares:
            rhs = f"ActShare + SpecShare{ctrl}"
            if "log_docs" in keep.columns:
                rhs = f"{rhs} + log_docs"
            f2 = f"{dep} ~ {rhs}{fe}"
            try:
                res2 = fit_ols_fe(f2, keep)
                results[f"OLS_k{k}_shares"] = res2
            except Exception as e:
                print(f"[warn] Shares model k={k} failed: {e}")

    # ---- Binary any AI patent (k=1), if patents present
    d1 = make_lagged(df, 1)
    if "patents_ai_lead1" in d1.columns:
        d1 = d1.assign(any_pat_1=(d1["patents_ai_lead1"] > 0).astype(int))
        rhs_terms = []
        if have_counts:
            rhs_terms += ["n_A","n_S"]
        elif have_shares:
            rhs_terms += ["ActShare","SpecShare"]
        rhs_terms += controls
        if "log_docs" in d1.columns:
            rhs_terms += ["log_docs"]
        if rhs_terms:
            f_bin = f"any_pat_1 ~ {' + '.join(rhs_terms)} + C(cik) + C(year)"
            try:
                res_bin = fit_ols_fe(f_bin, d1.dropna(subset=["any_pat_1"]))
                results["LPM_anypat_k1"] = res_bin
            except Exception as e:
                print(f"[warn] LPM anypat failed: {e}")

    if not results:
        raise RuntimeError("No models were estimated. Check that required columns exist.")

    # ---- Save stacked table (TXT + LaTeX) and CSV of coefficients
    ordered_keys = sorted(results.keys())
    ordered = [results[k] for k in ordered_keys]
    sc = summary_col(ordered, stars=True, float_format="%.3f",
                     model_names=ordered_keys,
                     info_dict={"N": lambda x: f"{int(x.nobs)}"})
    with open(os.path.join(outdir, "baseline_table.txt"), "w") as f:
        f.write(sc.as_text())
    with open(os.path.join(outdir, "baseline_table.tex"), "w") as f:
        f.write(sc.as_latex())

    rows = []
    for name, m in results.items():
        coefs = m.params.to_frame("coef")
        coefs["se"] = m.bse
        coefs["t"] = m.tvalues
        coefs["p"] = m.pvalues
        coefs["model"] = name
        coefs["N"] = m.nobs
        rows.append(coefs.reset_index().rename(columns={"index": "term"}))
    out = pd.concat(rows, ignore_index=True)
    out.to_csv(os.path.join(outdir, "baseline_coefficients.csv"), index=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", default="data/processed/panel/panel_reg_ready.csv")
    ap.add_argument("--outdir", default="results/01_baseline/tables")
    args = ap.parse_args()

    df = pd.read_csv(args.panel)
    # Minimal required keys
    for k in ["cik","year"]:
        if k not in df.columns:
            raise KeyError(f"Required key '{k}' not in panel.")

    df = add_engineered_cols(df)

    # Drop rows missing the dependent variable or key regressors if present
    base_needed = [c for c in ["patents_ai","n_A","n_S","ActShare","SpecShare","n_total","ln_assets","leverage","cash","rd_intensity","capx_at","roa","sales_growth","emp"] if c in df.columns]
    if base_needed:
        df = df.dropna(subset=base_needed, how="any")

    run_all_models(df, args.outdir)


if __name__ == "__main__":
    main()