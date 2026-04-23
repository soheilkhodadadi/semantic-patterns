"""Shared payload builders for standalone delivery tables."""

from __future__ import annotations

import csv
import math
import statistics
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.regression.linear_model import OLS
from statsmodels.tools.tools import add_constant

from semantic_ai_washing.analysis.run_regressions import add_engineered_cols, make_leads

TABLE1_VARS: list[tuple[str, str]] = [
    ("n_A", "Actionable AI sentences"),
    ("n_S", "Speculative AI sentences"),
    ("n_I", "Irrelevant AI sentences"),
    ("AI_Focus", "AI focus"),
    ("share_A", "Actionable share"),
    ("share_S", "Speculative share"),
    ("CredAI", "CredAI"),
    ("A_S", "Actionable/speculative ratio"),
    ("patents_ai", "AI patents"),
    ("patents_total", "Total patents"),
    ("ln_assets", "Log assets"),
    ("leverage", "Leverage"),
    ("cash", "Cash/assets"),
    ("rd_intensity", "R&D/assets"),
    ("capx_at", "CAPX/assets"),
    ("roa", "ROA"),
    ("sales_growth", "Sales growth"),
    ("emp", "Employees"),
]

CONTROL_CANDIDATES = [
    "ln_assets",
    "leverage",
    "cash",
    "rd_intensity",
    "capx_at",
    "roa",
    "sales_growth",
    "emp",
]

TIMING_LOG_AI_OUTCOMES: list[tuple[str, str]] = [
    ("t-2", "log_patents_ai_lag2"),
    ("t-1", "log_patents_ai_lag1"),
    ("t", "log_patents_ai_lead0"),
    ("t+1", "log_patents_ai_lead1"),
    ("t+2", "log_patents_ai_lead2"),
]

TIMING_COUNT_AI_OUTCOMES: list[tuple[str, str]] = [
    ("t-2", "patents_ai_lag2"),
    ("t-1", "patents_ai_lag1"),
    ("t", "patents_ai_lead0"),
    ("t+1", "patents_ai_lead1"),
    ("t+2", "patents_ai_lead2"),
]

CREDIBILITY_METRICS: list[tuple[str, str]] = [
    ("AI_Focus", "AI_Focus"),
    ("Speculative share", "SpecShare"),
    ("CredAI", "CredAI"),
    ("A/S ratio", "A_S"),
    ("SpecShare - ActShare", "SpecMinusAct"),
]

MISMATCH_METRICS: list[tuple[str, str]] = [
    ("A/S ratio", "A_S"),
    ("A/S ratio × PatentMismatch", "AS_x_PatentMismatch"),
]

DETERMINANT_METRICS: list[tuple[str, str]] = [
    ("Log assets", "ln_assets"),
    ("Cash/assets", "cash"),
    ("Leverage", "leverage"),
    ("R&D/assets", "rd_intensity"),
    ("CAPX/assets", "capx_at"),
    ("ROA", "roa"),
    ("Employees (k)", "emp"),
]

DETERMINANT_METRICS_REDUCED: list[tuple[str, str]] = [
    ("Log assets", "ln_assets"),
    ("Cash/assets", "cash"),
    ("Leverage", "leverage"),
    ("CAPX/assets", "capx_at"),
    ("ROA", "roa"),
]


def fmt_num(value: float | None, digits: int = 3) -> str:
    if value is None or math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def sig_stars(pvalue: float | None) -> str:
    if pvalue is None or math.isnan(pvalue):
        return ""
    if pvalue < 0.01:
        return "***"
    if pvalue < 0.05:
        return "**"
    if pvalue < 0.10:
        return "*"
    return ""


def quantile(values: list[float], p: float) -> float:
    if not values:
        return float("nan")
    n = len(values)
    k = (n - 1) * p
    floor_i = math.floor(k)
    ceil_i = math.ceil(k)
    if floor_i == ceil_i:
        return values[int(k)]
    return values[floor_i] * (ceil_i - k) + values[ceil_i] * (k - floor_i)


def to_markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


def _drop_infs(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    if not cols:
        return df
    mask = np.isfinite(df[cols].astype(float)).all(axis=1)
    return df.loc[mask].copy()


def _demean_by_codes(matrix: np.ndarray, codes: np.ndarray) -> np.ndarray:
    n_groups = int(codes.max()) + 1
    sums = np.zeros((n_groups, matrix.shape[1]), dtype=float)
    counts = np.bincount(codes, minlength=n_groups).astype(float)
    np.add.at(sums, codes, matrix)
    means = sums[codes] / counts[codes, None]
    return matrix - means


def _two_way_demean(
    matrix: np.ndarray,
    entity_codes: np.ndarray,
    time_codes: np.ndarray,
    *,
    max_iter: int = 100,
    tol: float = 1e-10,
) -> np.ndarray:
    transformed = matrix.astype(float, copy=True)
    for _ in range(max_iter):
        previous = transformed.copy()
        transformed = _demean_by_codes(transformed, entity_codes)
        transformed = _demean_by_codes(transformed, time_codes)
        if np.max(np.abs(transformed - previous)) < tol:
            break
    return transformed


def _compute_absorbed_adj_r2(
    y: np.ndarray,
    fitted: np.ndarray,
    *,
    nobs: int,
    n_slopes: int,
    n_entities: int,
    n_periods: int,
) -> float | None:
    tss = float(np.square(y).sum())
    if not np.isfinite(tss) or tss <= 0:
        return None
    ssr = float(np.square(y - fitted).sum())
    absorbed_rank = n_entities + n_periods - 1
    df_resid = nobs - n_slopes - absorbed_rank
    if df_resid <= 0 or nobs <= 1:
        return None
    mse_resid = ssr / df_resid
    mse_total = tss / (nobs - 1)
    return 1.0 - (mse_resid / mse_total)


def load_panel(panel_path: str | Path) -> pd.DataFrame:
    resolved = Path(panel_path)
    if resolved.suffix == ".parquet":
        df = pd.read_parquet(resolved)
    else:
        df = pd.read_csv(resolved, low_memory=False)
    if "sic2" not in df.columns and "sic" in df.columns:
        sic = pd.to_numeric(df["sic"], errors="coerce")
        df["sic2"] = (sic // 100).astype("Int64")
    df = add_engineered_cols(df)
    df = make_leads(df, k_list=(0, 1, 2))
    return df


def _non_financial_mask(df: pd.DataFrame) -> pd.Series:
    if "sic2" not in df.columns:
        return pd.Series(True, index=df.index)
    sic2 = pd.to_numeric(df["sic2"], errors="coerce")
    return ~sic2.between(60, 69, inclusive="both")


def _non_utility_mask(df: pd.DataFrame) -> pd.Series:
    if "sic2" not in df.columns:
        return pd.Series(True, index=df.index)
    sic2 = pd.to_numeric(df["sic2"], errors="coerce")
    return sic2.ne(49)


def _spec_variant_defs(df: pd.DataFrame) -> list[dict[str, object]]:
    return [
        {
            "number": "(1)",
            "label": "Firm + year FE",
            "absorb_col": "cik",
            "mask": pd.Series(True, index=df.index),
            "footer": {
                "Controls": "Y",
                "Firm FE": "Y",
                "Industry FE": "N",
                "Year FE": "Y",
                "Non-fin.": "N",
                "No util.": "N",
            },
        },
        {
            "number": "(2)",
            "label": "Industry + year FE",
            "absorb_col": "sic2",
            "mask": df["sic2"].notna()
            if "sic2" in df.columns
            else pd.Series(False, index=df.index),
            "footer": {
                "Controls": "Y",
                "Firm FE": "N",
                "Industry FE": "Y",
                "Year FE": "Y",
                "Non-fin.": "N",
                "No util.": "N",
            },
        },
        {
            "number": "(3)",
            "label": "Firm + year FE, non-fin.",
            "absorb_col": "cik",
            "mask": _non_financial_mask(df),
            "footer": {
                "Controls": "Y",
                "Firm FE": "Y",
                "Industry FE": "N",
                "Year FE": "Y",
                "Non-fin.": "Y",
                "No util.": "N",
            },
        },
        {
            "number": "(4)",
            "label": "Firm + year FE, non-fin./non-util.",
            "absorb_col": "cik",
            "mask": _non_financial_mask(df) & _non_utility_mask(df),
            "footer": {
                "Controls": "Y",
                "Firm FE": "Y",
                "Industry FE": "N",
                "Year FE": "Y",
                "Non-fin.": "Y",
                "No util.": "Y",
            },
        },
    ]


def _add_patent_mismatch(df: pd.DataFrame) -> pd.DataFrame:
    panel = df.copy()
    if "any_ai_talk" not in panel.columns:
        if "ai_total" in panel.columns:
            panel["any_ai_talk"] = (
                pd.to_numeric(panel["ai_total"], errors="coerce").fillna(0) > 0
            ).astype(int)
        else:
            panel["any_ai_talk"] = 0

    if "log_patents_ai_lead0" not in panel.columns:
        if "patents_ai" in panel.columns:
            panel["log_patents_ai_lead0"] = np.log1p(
                pd.to_numeric(panel["patents_ai"], errors="coerce").fillna(0)
            )
        else:
            panel["log_patents_ai_lead0"] = np.nan

    sic2 = pd.to_numeric(panel.get("sic2"), errors="coerce")
    year = pd.to_numeric(panel.get("year"), errors="coerce")
    panel["industry_year"] = pd.Series(pd.NA, index=panel.index, dtype="object")
    valid_industry = sic2.notna() & year.notna()
    if valid_industry.any():
        sic2_int = sic2.loc[valid_industry].astype(int).astype(str)
        year_int = year.loc[valid_industry].astype(int).astype(str)
        panel.loc[valid_industry, "industry_year"] = sic2_int.str.cat(year_int, sep="_")

    talk_mask = panel["any_ai_talk"].fillna(0).astype(int).eq(1)
    panel["LowCredibility"] = 0
    if talk_mask.any():
        talk_df = panel.loc[talk_mask, ["year", "A_S", "SpecShare"]].copy()
        as_cut = talk_df.groupby("year")["A_S"].transform(lambda s: s.quantile(0.25))
        spec_cut = talk_df.groupby("year")["SpecShare"].transform(lambda s: s.quantile(0.75))
        low_cred = (talk_df["A_S"] <= as_cut) | (talk_df["SpecShare"] >= spec_cut)
        panel.loc[talk_mask, "LowCredibility"] = low_cred.astype(int).to_numpy()

    panel["industry_year_mean_log_patents_t"] = panel.groupby("industry_year")[
        "log_patents_ai_lead0"
    ].transform("mean")
    panel["WeakPatentRelative"] = (
        (panel["log_patents_ai_lead0"] < panel["industry_year_mean_log_patents_t"])
        .fillna(False)
        .astype(int)
    )

    panel["PatentMismatch"] = (
        talk_mask & panel["LowCredibility"].astype(bool) & panel["WeakPatentRelative"].astype(bool)
    ).astype(int)
    panel["AS_x_PatentMismatch"] = panel["A_S"] * panel["PatentMismatch"]
    return panel


def _mismatch_spec_variant_defs(df: pd.DataFrame) -> list[dict[str, object]]:
    has_industry_year = (
        df["industry_year"].notna()
        if "industry_year" in df.columns
        else pd.Series(False, index=df.index)
    )
    return [
        {
            "number": "(1)",
            "label": "Firm + year FE",
            "absorb_col": "cik",
            "include_year": True,
            "mask": pd.Series(True, index=df.index),
            "footer": {
                "Controls": "Y",
                "Firm FE": "Y",
                "Industry×Year FE": "N",
                "Year FE": "Y",
                "Non-fin.": "N",
                "No util.": "N",
            },
        },
        {
            "number": "(2)",
            "label": "Industry×year FE",
            "absorb_col": "industry_year",
            "include_year": False,
            "mask": has_industry_year,
            "footer": {
                "Controls": "Y",
                "Firm FE": "N",
                "Industry×Year FE": "Y",
                "Year FE": "N",
                "Non-fin.": "N",
                "No util.": "N",
            },
        },
        {
            "number": "(3)",
            "label": "Firm + year FE, non-fin.",
            "absorb_col": "cik",
            "include_year": True,
            "mask": _non_financial_mask(df),
            "footer": {
                "Controls": "Y",
                "Firm FE": "Y",
                "Industry×Year FE": "N",
                "Year FE": "Y",
                "Non-fin.": "Y",
                "No util.": "N",
            },
        },
        {
            "number": "(4)",
            "label": "Firm + year FE, non-fin./non-util.",
            "absorb_col": "cik",
            "include_year": True,
            "mask": _non_financial_mask(df) & _non_utility_mask(df),
            "footer": {
                "Controls": "Y",
                "Firm FE": "Y",
                "Industry×Year FE": "N",
                "Year FE": "Y",
                "Non-fin.": "Y",
                "No util.": "Y",
            },
        },
    ]


def summarize_patent_mismatch_construct(panel_path: str | Path) -> dict[str, object]:
    df = load_panel(panel_path)
    df = _add_patent_mismatch(df)
    talk_rows = int(df["any_ai_talk"].fillna(0).astype(int).eq(1).sum())
    mismatch_rows = int(df["PatentMismatch"].fillna(0).astype(int).sum())
    mismatch_share_all = mismatch_rows / len(df) if len(df) else float("nan")
    mismatch_share_talk = mismatch_rows / talk_rows if talk_rows else float("nan")
    rows = [
        {"label": "Ever-speaker firm-year observations", "value": f"{len(df):,}"},
        {"label": "AI-talking firm-year observations", "value": f"{talk_rows:,}"},
        {"label": "PatentMismatch firm-year observations", "value": f"{mismatch_rows:,}"},
        {"label": "Mismatch share of ever-speaker sample", "value": fmt_num(mismatch_share_all)},
        {
            "label": "Mismatch share of AI-talking firm-years",
            "value": fmt_num(mismatch_share_talk),
        },
    ]
    note = (
        "PatentMismatch is constructed on the regression-ready ever-speaker annual panel. "
        "A firm-year is flagged as low-credibility when it is an AI-talking year and either `A_S` falls in the bottom year-specific quartile "
        "or `SpecShare` falls in the top year-specific quartile among AI-talking firm-years. "
        "It is flagged as weak-patent-relative when contemporaneous `log(1 + AI patents)` is below the industry-year mean. "
        "PatentMismatch equals one only when both conditions hold."
    )
    return {
        "title": "PatentMismatch Construct Summary",
        "note": note,
        "rows": rows,
    }


def summarize_table_1(panel_path: str | Path) -> dict[str, object]:
    values: dict[str, list[float]] = {column: [] for column, _ in TABLE1_VARS}
    with Path(panel_path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            for column, _ in TABLE1_VARS:
                raw = row.get(column, "")
                if raw in {"", None}:
                    continue
                try:
                    value = float(raw)
                except ValueError:
                    continue
                if math.isnan(value) or math.isinf(value):
                    continue
                values[column].append(value)

    rows: list[dict[str, str]] = []
    for column, label in TABLE1_VARS:
        arr = values[column]
        arr.sort()
        nobs = len(arr)
        mean = sum(arr) / nobs if nobs else float("nan")
        sd = statistics.stdev(arr) if nobs > 1 else float("nan")
        rows.append(
            {
                "Variable": label,
                "Mean": fmt_num(mean),
                "Std. Dev.": fmt_num(sd),
                "p5": fmt_num(quantile(arr, 0.05)),
                "p25": fmt_num(quantile(arr, 0.25)),
                "p50": fmt_num(quantile(arr, 0.50)),
                "p75": fmt_num(quantile(arr, 0.75)),
                "p95": fmt_num(quantile(arr, 0.95)),
                "N": f"{nobs:,}",
            }
        )

    note = (
        "This table presents summary statistics for the variables used in the analysis. "
        "It reports the mean, standard deviation, selected percentiles (p5, p25, p50, p75, and p95), "
        "and the number of observations (N) for the regression-ready ever-speaker `2016-2024` firm-year sample."
    )
    return {
        "title": "Table 1. Summary Statistics",
        "note": note,
        "rows": rows,
        "headers": ["Variable", "Mean", "Std. Dev.", "p5", "p25", "p50", "p75", "p95", "N"],
    }


def _fit_fe_ols(
    df: pd.DataFrame,
    *,
    dependent: str,
    rhs_terms: list[str],
    controls: list[str] | None = None,
):
    controls = controls or CONTROL_CANDIDATES
    needed = [dependent, *rhs_terms, *controls, "cik", "year"]
    missing = [column for column in needed if column not in df.columns]
    if missing:
        raise KeyError(f"Missing columns for timing model: {missing}")

    use = df.dropna(subset=needed).copy()
    numeric = [dependent, *rhs_terms, *controls]
    use = _drop_infs(use, numeric)
    work_cols = [dependent, *rhs_terms, *controls]
    matrix = use[work_cols].astype(float).to_numpy()
    entity_codes, _ = pd.factorize(use["cik"], sort=False)
    time_codes, _ = pd.factorize(use["year"], sort=False)
    demeaned = _two_way_demean(matrix, entity_codes, time_codes)
    y = demeaned[:, 0]
    x = pd.DataFrame(demeaned[:, 1:], columns=[*rhs_terms, *controls], index=use.index)
    result = OLS(y, x).fit(cov_type="cluster", cov_kwds={"groups": use["cik"]})
    adj_r2 = _compute_absorbed_adj_r2(
        y,
        np.asarray(result.fittedvalues),
        nobs=len(use),
        n_slopes=x.shape[1],
        n_entities=len(np.unique(entity_codes)),
        n_periods=len(np.unique(time_codes)),
    )
    return result, use, adj_r2


def _fit_absorbed_ols(
    df: pd.DataFrame,
    *,
    dependent: str,
    rhs_terms: list[str],
    absorb_col: str,
    include_year: bool = True,
    controls: list[str] | None = None,
):
    controls = controls or CONTROL_CANDIDATES
    needed = [dependent, *rhs_terms, *controls, absorb_col, "cik"]
    if include_year:
        needed.append("year")
    missing = [column for column in needed if column not in df.columns]
    if missing:
        raise KeyError(f"Missing columns for absorbed model: {missing}")

    use = df.dropna(subset=needed).copy()
    numeric = [dependent, *rhs_terms, *controls]
    use = _drop_infs(use, numeric)
    work_cols = [dependent, *rhs_terms, *controls]
    matrix = use[work_cols].astype(float).to_numpy()
    absorb_codes, _ = pd.factorize(use[absorb_col], sort=False)
    if include_year:
        time_codes, _ = pd.factorize(use["year"], sort=False)
        demeaned = _two_way_demean(matrix, absorb_codes, time_codes)
        n_periods = len(np.unique(time_codes))
    else:
        demeaned = _demean_by_codes(matrix, absorb_codes)
        n_periods = 1
    y = demeaned[:, 0]
    x = pd.DataFrame(demeaned[:, 1:], columns=[*rhs_terms, *controls], index=use.index)
    result = OLS(y, x).fit(cov_type="cluster", cov_kwds={"groups": use["cik"]})
    adj_r2 = _compute_absorbed_adj_r2(
        y,
        np.asarray(result.fittedvalues),
        nobs=len(use),
        n_slopes=x.shape[1],
        n_entities=len(np.unique(absorb_codes)),
        n_periods=n_periods,
    )
    return result, use, adj_r2


def _fit_cross_section_ols(
    df: pd.DataFrame,
    *,
    dependent: str,
    rhs_terms: list[str],
    absorb_col: str | None = None,
    cluster_col: str | None = None,
):
    needed = [dependent, *rhs_terms]
    if absorb_col:
        needed.append(absorb_col)
    if cluster_col:
        needed.append(cluster_col)
    missing = [column for column in needed if column not in df.columns]
    if missing:
        raise KeyError(f"Missing columns for cross-section model: {missing}")

    use = df.dropna(subset=needed).copy()
    numeric = [dependent, *rhs_terms]
    use = _drop_infs(use, numeric)

    x = use[rhs_terms].astype(float)
    if absorb_col:
        absorb = pd.to_numeric(use[absorb_col], errors="coerce")
        use = use.loc[absorb.notna()].copy()
        x = x.loc[use.index]
        absorb = absorb.loc[use.index].astype(int).astype(str)
        fe_dummies = pd.get_dummies(absorb, prefix="fe", drop_first=True, dtype=float)
        x = pd.concat([x, fe_dummies], axis=1)

    x = add_constant(x, has_constant="add")
    y = use[dependent].astype(float)

    fit_kwargs: dict[str, object] = {}
    if cluster_col:
        groups = pd.to_numeric(use[cluster_col], errors="coerce")
        cluster_mask = groups.notna()
        use = use.loc[cluster_mask].copy()
        x = x.loc[use.index]
        y = y.loc[use.index]
        groups = groups.loc[use.index]
        fit_kwargs = {"cov_type": "cluster", "cov_kwds": {"groups": groups}}

    result = OLS(y, x).fit(**fit_kwargs)
    return result, use, float(result.rsquared_adj)


def _build_mismatch_firm_sample(panel_path: str | Path) -> pd.DataFrame:
    df = load_panel(panel_path)
    df = _add_patent_mismatch(df)
    base = (
        df.loc[
            df["year"].eq(2016), ["cik", "sic2", *[term for _label, term in DETERMINANT_METRICS]]
        ]
        .sort_values("cik")
        .drop_duplicates(subset=["cik"])
        .copy()
    )
    firm_summary = (
        df.groupby("cik", as_index=False)
        .agg(
            mismatch_years=("PatentMismatch", "sum"),
            talk_years=("any_ai_talk", "sum"),
        )
        .copy()
    )
    talk_years = pd.to_numeric(firm_summary["talk_years"], errors="coerce").fillna(0)
    mismatch_years = pd.to_numeric(firm_summary["mismatch_years"], errors="coerce").fillna(0)
    firm_summary["ever_mismatch"] = (mismatch_years > 0).astype(int)
    firm_summary["mismatch_share_talk"] = np.where(
        talk_years > 0,
        mismatch_years / talk_years,
        np.nan,
    )
    merged = base.merge(
        firm_summary[["cik", "ever_mismatch", "mismatch_share_talk", "talk_years"]],
        on="cik",
        how="left",
    )
    return merged


def _summarize_timing_focus(
    panel_path: str | Path,
    *,
    outcomes: list[tuple[str, str]],
    title: str,
    dependent_label: str,
    note: str,
) -> dict[str, object]:
    df = load_panel(panel_path)
    models = []
    coef_cells: list[str] = []
    se_cells: list[str] = []
    nobs_cells: list[str] = []
    adj_r2_cells: list[str] = []

    for idx, (horizon_label, dependent) in enumerate(outcomes, start=1):
        result, _, adj_r2 = _fit_fe_ols(df, dependent=dependent, rhs_terms=["AI_Focus"])
        coef = result.params.get("AI_Focus", float("nan"))
        se = result.bse.get("AI_Focus", float("nan"))
        pvalue = result.pvalues.get("AI_Focus")
        models.append({"number": f"({idx})", "label": horizon_label})
        coef_cells.append(f"{coef:.3f}{sig_stars(pvalue)}" if not math.isnan(coef) else "")
        se_cells.append(f"({se:.3f})" if not math.isnan(se) else "")
        nobs_cells.append(f"{int(result.nobs):,}")
        adj_r2_cells.append(fmt_num(adj_r2))

    return {
        "title": title,
        "note": note,
        "dependent_label": dependent_label,
        "models": models,
        "panels": [
            {
                "heading": None,
                "label": "AI_Focus",
                "coef_cells": coef_cells,
                "se_cells": se_cells,
                "footer_rows": [
                    {"label": "Controls", "cells": ["Y"] * len(models)},
                    {"label": "Firm FE", "cells": ["Y"] * len(models)},
                    {"label": "Year FE", "cells": ["Y"] * len(models)},
                    {"label": "Adj. R²", "cells": adj_r2_cells},
                    {"label": "Observations", "cells": nobs_cells},
                ],
            }
        ],
    }


def summarize_table_2_timing_focus(panel_path: str | Path) -> dict[str, object]:
    note = (
        "This table presents firm-year panel regressions on the regression-ready ever-speaker annual panel. "
        "The dependent variable is `log(1 + AI patents)` measured at different calendar-time horizons relative to the disclosure year. "
        "The focal regressor is `AI_Focus`, defined as `log(1 + AI sentences)`. Control variables include size, leverage, cash/assets, "
        "R&D/assets, CAPX/assets, ROA, sales growth, and employees. Firm and year fixed effects are included in all columns. "
        "Standard errors clustered at the firm level are shown in parentheses. Constants are omitted. (* p<0.1, ** p<0.05, *** p<0.01)."
    )
    return _summarize_timing_focus(
        panel_path,
        outcomes=TIMING_LOG_AI_OUTCOMES,
        title="Table 2. AI Disclosure Intensity and AI Patent Timing",
        dependent_label="Dependent variable: log(1 + AI patents)",
        note=note,
    )


def summarize_table_2_timing_focus_counts(panel_path: str | Path) -> dict[str, object]:
    note = (
        "This companion table presents firm-year panel regressions on the regression-ready ever-speaker annual panel. "
        "The dependent variable is the raw count of AI patents measured at different calendar-time horizons relative to the disclosure year. "
        "The focal regressor is `AI_Focus`, defined as `log(1 + AI sentences)`. Control variables include size, leverage, cash/assets, "
        "R&D/assets, CAPX/assets, ROA, sales growth, and employees. Firm and year fixed effects are included in all columns. "
        "Standard errors clustered at the firm level are shown in parentheses. Constants are omitted. (* p<0.1, ** p<0.05, *** p<0.01)."
    )
    return _summarize_timing_focus(
        panel_path,
        outcomes=TIMING_COUNT_AI_OUTCOMES,
        title="Table 2B. AI Disclosure Intensity and AI Patent Timing (Count Outcome)",
        dependent_label="Dependent variable: AI patents",
        note=note,
    )


def _summarize_timing_composition(
    panel_path: str | Path,
    *,
    outcomes: list[tuple[str, str]],
    title: str,
    dependent_label: str,
    note: str,
) -> dict[str, object]:
    df = load_panel(panel_path)
    models = [
        {"number": f"({idx})", "label": label} for idx, (label, _) in enumerate(outcomes, start=1)
    ]
    panel_defs = [
        ("Panel A. Actionable disclosure", "Actionable disclosure (dummy)", "has_actionable"),
        (
            "Panel B. Speculative-only disclosure",
            "Speculative-only disclosure (dummy)",
            "has_spec_only",
        ),
    ]

    panels: list[dict[str, object]] = []
    for panel_index, (heading, label, rhs) in enumerate(panel_defs):
        coef_cells: list[str] = []
        se_cells: list[str] = []
        nobs_cells: list[str] = []
        adj_r2_cells: list[str] = []
        for _, dependent in outcomes:
            result, _, adj_r2 = _fit_fe_ols(df, dependent=dependent, rhs_terms=[rhs])
            coef = result.params.get(rhs, float("nan"))
            se = result.bse.get(rhs, float("nan"))
            pvalue = result.pvalues.get(rhs)
            coef_cells.append(f"{coef:.3f}{sig_stars(pvalue)}" if not math.isnan(coef) else "")
            se_cells.append(f"({se:.3f})" if not math.isnan(se) else "")
            nobs_cells.append(f"{int(result.nobs):,}")
            adj_r2_cells.append(fmt_num(adj_r2))
        panels.append(
            {
                "heading": heading,
                "label": label,
                "coef_cells": coef_cells,
                "se_cells": se_cells,
                "footer_rows": (
                    [
                        {"label": "Controls", "cells": ["Y"] * len(models)},
                        {"label": "Firm FE", "cells": ["Y"] * len(models)},
                        {"label": "Year FE", "cells": ["Y"] * len(models)},
                        {"label": "Adj. R²", "cells": adj_r2_cells},
                        {"label": "Observations", "cells": nobs_cells},
                    ]
                    if panel_index == len(panel_defs) - 1
                    else []
                ),
            }
        )

    return {
        "title": title,
        "note": note,
        "dependent_label": dependent_label,
        "models": models,
        "panels": panels,
    }


def summarize_table_3_timing_composition(panel_path: str | Path) -> dict[str, object]:
    note = (
        "This table presents firm-year panel regressions on the regression-ready ever-speaker annual panel. "
        "The dependent variable is `log(1 + AI patents)` measured at different calendar-time horizons relative to the disclosure year. "
        "Panel A uses the actionable-disclosure indicator and Panel B uses the speculative-only disclosure indicator. "
        "Each panel reports one-variable regressions with the same baseline control set: size, leverage, cash/assets, R&D/assets, CAPX/assets, ROA, sales growth, and employees. "
        "Firm and year fixed effects are included in all columns. Standard errors clustered at the firm level are shown in parentheses. "
        "Constants are omitted. (* p<0.1, ** p<0.05, *** p<0.01)."
    )
    return _summarize_timing_composition(
        panel_path,
        outcomes=TIMING_LOG_AI_OUTCOMES,
        title="Table 3. Disclosure Composition and AI Patent Timing",
        dependent_label="Dependent variable: log(1 + AI patents)",
        note=note,
    )


def summarize_table_3_timing_composition_counts(panel_path: str | Path) -> dict[str, object]:
    note = (
        "This companion table presents firm-year panel regressions on the regression-ready ever-speaker annual panel. "
        "The dependent variable is the raw count of AI patents measured at different calendar-time horizons relative to the disclosure year. "
        "Panel A uses the actionable-disclosure indicator and Panel B uses the speculative-only disclosure indicator. "
        "Each panel reports one-variable regressions with the same baseline control set: size, leverage, cash/assets, R&D/assets, CAPX/assets, ROA, sales growth, and employees. "
        "Firm and year fixed effects are included in all columns. Standard errors clustered at the firm level are shown in parentheses. "
        "Constants are omitted. (* p<0.1, ** p<0.05, *** p<0.01)."
    )
    return _summarize_timing_composition(
        panel_path,
        outcomes=TIMING_COUNT_AI_OUTCOMES,
        title="Table 3B. Disclosure Composition and AI Patent Timing (Count Outcome)",
        dependent_label="Dependent variable: AI patents",
        note=note,
    )


def _summarize_spec_ladder(
    panel_path: str | Path,
    *,
    dependent: str,
    title: str,
    dependent_label: str,
    note: str,
) -> dict[str, object]:
    df = load_panel(panel_path)
    spec_defs = _spec_variant_defs(df)

    panels: list[dict[str, object]] = []
    panel_defs = [
        ("Panel A. Actionable disclosure", "Actionable disclosure (dummy)", "has_actionable"),
        (
            "Panel B. Speculative-only disclosure",
            "Speculative-only disclosure (dummy)",
            "has_spec_only",
        ),
    ]

    models = [{"number": spec["number"], "label": spec["label"]} for spec in spec_defs]

    footer_template = [
        "Controls",
        "Firm FE",
        "Industry FE",
        "Year FE",
        "Non-fin.",
        "No util.",
        "Adj. R²",
        "Observations",
    ]

    for panel_index, (heading, label, rhs) in enumerate(panel_defs):
        coef_cells: list[str] = []
        se_cells: list[str] = []
        adj_r2_cells: list[str] = []
        nobs_cells: list[str] = []
        footers = {key: [] for key in footer_template[:-2]}

        for spec in spec_defs:
            mask = spec["mask"]
            spec_df = df.loc[mask].copy()
            result, use, adj_r2 = _fit_absorbed_ols(
                spec_df,
                dependent=dependent,
                rhs_terms=[rhs],
                absorb_col=spec["absorb_col"],
            )
            coef = result.params.get(rhs, float("nan"))
            se = result.bse.get(rhs, float("nan"))
            pvalue = result.pvalues.get(rhs)
            coef_cells.append(f"{coef:.3f}{sig_stars(pvalue)}" if not math.isnan(coef) else "")
            se_cells.append(f"({se:.3f})" if not math.isnan(se) else "")
            adj_r2_cells.append(fmt_num(adj_r2))
            nobs_cells.append(f"{int(result.nobs):,}")
            for footer_key in footers:
                footers[footer_key].append(spec["footer"][footer_key])

        footer_rows = (
            [
                {"label": "Controls", "cells": footers["Controls"]},
                {"label": "Firm FE", "cells": footers["Firm FE"]},
                {"label": "Industry FE", "cells": footers["Industry FE"]},
                {"label": "Year FE", "cells": footers["Year FE"]},
                {"label": "Non-fin.", "cells": footers["Non-fin."]},
                {"label": "No util.", "cells": footers["No util."]},
                {"label": "Adj. R²", "cells": adj_r2_cells},
                {"label": "Observations", "cells": nobs_cells},
            ]
            if panel_index == len(panel_defs) - 1
            else []
        )

        panels.append(
            {
                "heading": heading,
                "label": label,
                "coef_cells": coef_cells,
                "se_cells": se_cells,
                "footer_rows": footer_rows,
            }
        )

    return {
        "title": title,
        "note": note,
        "dependent_label": dependent_label,
        "models": models,
        "panels": panels,
    }


def summarize_table_4_spec_ladder_tplus1(panel_path: str | Path) -> dict[str, object]:
    note = (
        "This table presents specification-ladder regressions on the regression-ready ever-speaker annual panel. "
        "The dependent variable is `log(1 + AI patents)` measured at `t+1`. Columns vary the fixed-effects structure and sample trim while keeping the same baseline control set. "
        "Panel A uses the actionable-disclosure indicator and Panel B uses the speculative-only disclosure indicator. "
        "Standard errors clustered at the firm level are shown in parentheses. Constants are omitted. (* p<0.1, ** p<0.05, *** p<0.01)."
    )
    return _summarize_spec_ladder(
        panel_path,
        dependent="log_patents_ai_lead1",
        title="Table 4. Specification Ladder for Future AI Patent Timing",
        dependent_label="Dependent variable: log(1 + AI patents at t+1)",
        note=note,
    )


def summarize_table_4b_spec_ladder_t(panel_path: str | Path) -> dict[str, object]:
    note = (
        "This companion table presents the same specification ladder as Table 4 but uses contemporaneous AI patent outcomes. "
        "The dependent variable is `log(1 + AI patents)` measured at `t`. Columns vary the fixed-effects structure and sample trim while keeping the same baseline control set. "
        "Panel A uses the actionable-disclosure indicator and Panel B uses the speculative-only disclosure indicator. "
        "Standard errors clustered at the firm level are shown in parentheses. Constants are omitted. (* p<0.1, ** p<0.05, *** p<0.01)."
    )
    return _summarize_spec_ladder(
        panel_path,
        dependent="log_patents_ai_lead0",
        title="Table 4B. Specification Ladder for Contemporaneous AI Patent Timing",
        dependent_label="Dependent variable: log(1 + AI patents at t)",
        note=note,
    )


def _timing_row_label(label: str) -> str:
    return f"log(1 + AI patents) at {label}"


def _summarize_patent_timing_matrix(
    panel_path: str | Path,
    *,
    dependent: str,
    title: str,
    dependent_label: str,
    note: str,
    outcomes: list[tuple[str, str]] = TIMING_LOG_AI_OUTCOMES,
) -> dict[str, object]:
    df = load_panel(panel_path)
    spec_defs = _spec_variant_defs(df)
    models = [{"number": spec["number"], "label": spec["label"]} for spec in spec_defs]

    results_by_spec: list[tuple[object, float | None]] = []
    nobs_cells: list[str] = []
    adj_r2_cells: list[str] = []
    footer_flags = {
        key: []
        for key in ["Controls", "Firm FE", "Industry FE", "Year FE", "Non-fin.", "No util."]
    }

    rhs_terms = [term for _, term in outcomes]
    for spec in spec_defs:
        spec_df = df.loc[spec["mask"]].copy()
        result, _, adj_r2 = _fit_absorbed_ols(
            spec_df,
            dependent=dependent,
            rhs_terms=rhs_terms,
            absorb_col=str(spec["absorb_col"]),
        )
        results_by_spec.append((result, adj_r2))
        nobs_cells.append(f"{int(result.nobs):,}")
        adj_r2_cells.append(fmt_num(adj_r2))
        for footer_key in footer_flags:
            footer_flags[footer_key].append(str(spec["footer"][footer_key]))

    body_rows: list[dict[str, object]] = []
    for horizon_label, term in outcomes:
        coef_cells: list[str] = []
        se_cells: list[str] = []
        for result, _adj_r2 in results_by_spec:
            coef = result.params.get(term, float("nan"))
            se = result.bse.get(term, float("nan"))
            pvalue = result.pvalues.get(term)
            coef_cells.append(f"{coef:.3f}{sig_stars(pvalue)}" if not math.isnan(coef) else "")
            se_cells.append(f"({se:.3f})" if not math.isnan(se) else "")
        body_rows.append(
            {"label": _timing_row_label(horizon_label), "cells": coef_cells, "kind": "coef"}
        )
        body_rows.append({"label": "", "cells": se_cells, "kind": "se"})

    footer_rows = [
        {"label": "Controls", "cells": footer_flags["Controls"]},
        {"label": "Firm FE", "cells": footer_flags["Firm FE"]},
        {"label": "Industry FE", "cells": footer_flags["Industry FE"]},
        {"label": "Year FE", "cells": footer_flags["Year FE"]},
        {"label": "Non-fin.", "cells": footer_flags["Non-fin."]},
        {"label": "No util.", "cells": footer_flags["No util."]},
        {"label": "Adj. R²", "cells": adj_r2_cells},
        {"label": "Observations", "cells": nobs_cells},
    ]
    return {
        "title": title,
        "note": note,
        "dependent_label": dependent_label,
        "models": models,
        "body_rows": body_rows,
        "footer_rows": footer_rows,
    }


def summarize_table_4_actionable_patent_timing(panel_path: str | Path) -> dict[str, object]:
    note = (
        "This table presents distributed-lag style firm-year regressions on the regression-ready ever-speaker annual panel. "
        "The dependent variable is the actionable-disclosure indicator. Each column includes the full set of AI patent timing terms "
        "from `t-2` through `t+2`, so the rows trace how prior, contemporaneous, and future AI patenting line up with actionable AI disclosure. "
        "Columns vary the fixed-effects structure and sample trim while keeping the same baseline control set: size, leverage, cash/assets, "
        "R&D/assets, CAPX/assets, ROA, sales growth, and employees. Standard errors clustered at the firm level are shown in parentheses. "
        "Constants are omitted. (* p<0.1, ** p<0.05, *** p<0.01)."
    )
    return _summarize_patent_timing_matrix(
        panel_path,
        dependent="has_actionable",
        title="Table 4. Actionable Disclosure and AI Patent Timing",
        dependent_label="Dependent variable: Actionable disclosure",
        note=note,
    )


def summarize_table_4b_speculative_patent_timing(panel_path: str | Path) -> dict[str, object]:
    note = (
        "This companion table presents the same distributed-lag style design as Table 4 but uses the speculative-only disclosure indicator as the dependent variable. "
        "Each column includes the full set of AI patent timing terms from `t-2` through `t+2`, so the rows trace how prior, contemporaneous, and future AI patenting line up with speculative-only AI disclosure. "
        "Columns vary the fixed-effects structure and sample trim while keeping the same baseline control set: size, leverage, cash/assets, "
        "R&D/assets, CAPX/assets, ROA, sales growth, and employees. Standard errors clustered at the firm level are shown in parentheses. "
        "Constants are omitted. (* p<0.1, ** p<0.05, *** p<0.01)."
    )
    return _summarize_patent_timing_matrix(
        panel_path,
        dependent="has_spec_only",
        title="Table 4B. Speculative-Only Disclosure and AI Patent Timing",
        dependent_label="Dependent variable: Speculative-only disclosure",
        note=note,
    )


def _summarize_metric_matrix(
    panel_path: str | Path,
    *,
    dependent: str,
    title: str,
    dependent_label: str,
    note: str,
    metrics: list[tuple[str, str]] = CREDIBILITY_METRICS,
) -> dict[str, object]:
    df = load_panel(panel_path)
    spec_defs = _spec_variant_defs(df)
    models = [{"number": spec["number"], "label": spec["label"]} for spec in spec_defs]

    footer_flags = {
        key: []
        for key in ["Controls", "Firm FE", "Industry FE", "Year FE", "Non-fin.", "No util."]
    }
    results_by_spec: list[
        tuple[dict[str, tuple[float, float, float | None]], float | None, int]
    ] = []

    for spec in spec_defs:
        spec_df = df.loc[spec["mask"]].copy()
        metric_results: dict[str, tuple[float, float, float | None]] = {}
        spec_nobs = 0
        spec_adj_r2: float | None = None
        for label, term in metrics:
            result, _, adj_r2 = _fit_absorbed_ols(
                spec_df,
                dependent=dependent,
                rhs_terms=[term],
                absorb_col=str(spec["absorb_col"]),
            )
            coef = result.params.get(term, float("nan"))
            se = result.bse.get(term, float("nan"))
            pvalue = result.pvalues.get(term)
            metric_results[label] = (coef, se, pvalue)
            spec_nobs = int(result.nobs)
            spec_adj_r2 = adj_r2
        results_by_spec.append((metric_results, spec_adj_r2, spec_nobs))
        for footer_key in footer_flags:
            footer_flags[footer_key].append(str(spec["footer"][footer_key]))

    body_rows: list[dict[str, object]] = []
    for label, _term in metrics:
        coef_cells: list[str] = []
        se_cells: list[str] = []
        for metric_results, _adj_r2, _nobs in results_by_spec:
            coef, se, pvalue = metric_results[label]
            coef_cells.append(f"{coef:.3f}{sig_stars(pvalue)}" if not math.isnan(coef) else "")
            se_cells.append(f"({se:.3f})" if not math.isnan(se) else "")
        body_rows.append({"label": label, "cells": coef_cells, "kind": "coef"})
        body_rows.append({"label": "", "cells": se_cells, "kind": "se"})

    footer_rows = [
        {"label": "Controls", "cells": footer_flags["Controls"]},
        {"label": "Firm FE", "cells": footer_flags["Firm FE"]},
        {"label": "Industry FE", "cells": footer_flags["Industry FE"]},
        {"label": "Year FE", "cells": footer_flags["Year FE"]},
        {"label": "Non-fin.", "cells": footer_flags["Non-fin."]},
        {"label": "No util.", "cells": footer_flags["No util."]},
        {
            "label": "Adj. R²",
            "cells": [fmt_num(adj_r2) for _metric_results, adj_r2, _nobs in results_by_spec],
        },
        {
            "label": "Observations",
            "cells": [f"{nobs:,}" for _metric_results, _adj_r2, nobs in results_by_spec],
        },
    ]

    return {
        "title": title,
        "note": note,
        "dependent_label": dependent_label,
        "models": models,
        "body_rows": body_rows,
        "footer_rows": footer_rows,
    }


def summarize_table_5_credibility_metrics_tplus1(panel_path: str | Path) -> dict[str, object]:
    note = (
        "This appendix table presents exploratory credibility-metric regressions on the regression-ready ever-speaker annual panel. "
        "The dependent variable is `log(1 + AI patents)` at `t+1`. Rows report one-variable regressions for the broad AI-focus measure and the main disclosure-credibility constructs: "
        "`SpecShare`, `CredAI`, `A_S`, and `SpecMinusAct`. Columns vary the fixed-effects structure and sample trim while keeping the same baseline control set: size, leverage, cash/assets, "
        "R&D/assets, CAPX/assets, ROA, sales growth, and employees. Standard errors clustered at the firm level are shown in parentheses. "
        "Constants are omitted. This table is retained as an appendix companion rather than the main methodology-aligned AI-washing specification. (* p<0.1, ** p<0.05, *** p<0.01)."
    )
    return _summarize_metric_matrix(
        panel_path,
        dependent="log_patents_ai_lead1",
        title="Appendix Table A1. Exploratory Credibility Metrics and Future AI Patenting",
        dependent_label="Dependent variable: log(1 + AI patents at t+1)",
        note=note,
    )


def summarize_table_5b_credibility_metrics_tplus2(panel_path: str | Path) -> dict[str, object]:
    note = (
        "This appendix companion presents the same exploratory credibility-metric design as Appendix Table A1 but uses the longer-horizon outcome `log(1 + AI patents)` at `t+2`. "
        "Rows report one-variable regressions for `AI_Focus`, `SpecShare`, `CredAI`, `A_S`, and `SpecMinusAct`. Columns vary the fixed-effects structure and sample trim while keeping the same baseline control set: "
        "size, leverage, cash/assets, R&D/assets, CAPX/assets, ROA, sales growth, and employees. Standard errors clustered at the firm level are shown in parentheses. "
        "Constants are omitted. This table is retained as an appendix companion rather than the main methodology-aligned AI-washing specification. (* p<0.1, ** p<0.05, *** p<0.01)."
    )
    return _summarize_metric_matrix(
        panel_path,
        dependent="log_patents_ai_lead2",
        title="Appendix Table A2. Exploratory Credibility Metrics and Longer-Horizon AI Patenting",
        dependent_label="Dependent variable: log(1 + AI patents at t+2)",
        note=note,
    )


def _summarize_mismatch_matrix(
    panel_path: str | Path,
    *,
    dependent: str,
    title: str,
    dependent_label: str,
    note: str,
    metrics: list[tuple[str, str]] = MISMATCH_METRICS,
) -> dict[str, object]:
    df = load_panel(panel_path)
    df = _add_patent_mismatch(df)
    spec_defs = _mismatch_spec_variant_defs(df)
    models = [{"number": spec["number"], "label": spec["label"]} for spec in spec_defs]

    footer_flags = {
        key: []
        for key in ["Controls", "Firm FE", "Industry×Year FE", "Year FE", "Non-fin.", "No util."]
    }
    results_by_spec: list[
        tuple[dict[str, tuple[float, float, float | None]], float | None, int]
    ] = []

    for spec in spec_defs:
        spec_df = df.loc[spec["mask"]].copy()
        metric_results: dict[str, tuple[float, float, float | None]] = {}
        result, _, adj_r2 = _fit_absorbed_ols(
            spec_df,
            dependent=dependent,
            rhs_terms=[metric for _label, metric in metrics],
            absorb_col=str(spec["absorb_col"]),
            include_year=bool(spec.get("include_year", True)),
        )
        spec_nobs = int(result.nobs)
        spec_adj_r2: float | None = adj_r2
        for label, term in metrics:
            coef = result.params.get(term, float("nan"))
            se = result.bse.get(term, float("nan"))
            pvalue = result.pvalues.get(term)
            metric_results[label] = (coef, se, pvalue)
        results_by_spec.append((metric_results, spec_adj_r2, spec_nobs))
        for footer_key in footer_flags:
            footer_flags[footer_key].append(str(spec["footer"][footer_key]))

    body_rows: list[dict[str, object]] = []
    for label, _term in metrics:
        coef_cells: list[str] = []
        se_cells: list[str] = []
        for metric_results, _adj_r2, _nobs in results_by_spec:
            coef, se, pvalue = metric_results[label]
            coef_cells.append(f"{coef:.3f}{sig_stars(pvalue)}" if not math.isnan(coef) else "")
            se_cells.append(f"({se:.3f})" if not math.isnan(se) else "")
        body_rows.append({"label": label, "cells": coef_cells, "kind": "coef"})
        body_rows.append({"label": "", "cells": se_cells, "kind": "se"})

    footer_rows = [
        {"label": "Controls", "cells": footer_flags["Controls"]},
        {"label": "Firm FE", "cells": footer_flags["Firm FE"]},
        {"label": "Industry×Year FE", "cells": footer_flags["Industry×Year FE"]},
        {"label": "Year FE", "cells": footer_flags["Year FE"]},
        {"label": "Non-fin.", "cells": footer_flags["Non-fin."]},
        {"label": "No util.", "cells": footer_flags["No util."]},
        {
            "label": "Adj. R²",
            "cells": [fmt_num(adj_r2) for _metric_results, adj_r2, _nobs in results_by_spec],
        },
        {
            "label": "Observations",
            "cells": [f"{nobs:,}" for _metric_results, _adj_r2, nobs in results_by_spec],
        },
    ]

    return {
        "title": title,
        "note": note,
        "dependent_label": dependent_label,
        "models": models,
        "body_rows": body_rows,
        "footer_rows": footer_rows,
    }


def _summarize_mismatch_determinants(
    panel_path: str | Path,
    *,
    dependent: str,
    title: str,
    dependent_label: str,
    note: str,
    metrics: list[tuple[str, str]] = DETERMINANT_METRICS,
) -> dict[str, object]:
    df = _build_mismatch_firm_sample(panel_path)
    metric_terms = [term for _label, term in metrics]
    model_defs = [
        *[
            {"number": f"({idx})", "label": label, "rhs_terms": [term], "all_covars": "N"}
            for idx, (label, term) in enumerate(metrics, start=1)
        ],
        {
            "number": f"({len(metrics) + 1})",
            "label": "Multivar.",
            "rhs_terms": metric_terms,
            "all_covars": "Y",
        },
    ]

    models = [{"number": spec["number"], "label": spec["label"]} for spec in model_defs]
    results_by_spec: list[
        tuple[dict[str, tuple[float, float, float | None]], float | None, int]
    ] = []
    all_covars_flags: list[str] = []

    for spec in model_defs:
        result, use, adj_r2 = _fit_cross_section_ols(
            df,
            dependent=dependent,
            rhs_terms=list(spec["rhs_terms"]),
            absorb_col="sic2",
            cluster_col="sic2",
        )
        metric_results: dict[str, tuple[float, float, float | None]] = {}
        for label, term in metrics:
            coef = result.params.get(term, float("nan"))
            se = result.bse.get(term, float("nan"))
            pvalue = result.pvalues.get(term)
            metric_results[label] = (coef, se, pvalue)
        results_by_spec.append((metric_results, adj_r2, len(use)))
        all_covars_flags.append(str(spec["all_covars"]))

    body_rows: list[dict[str, object]] = []
    for label, _term in metrics:
        coef_cells: list[str] = []
        se_cells: list[str] = []
        for metric_results, _adj_r2, _nobs in results_by_spec:
            coef, se, pvalue = metric_results[label]
            coef_cells.append(f"{coef:.3f}{sig_stars(pvalue)}" if not math.isnan(coef) else "")
            se_cells.append(f"({se:.3f})" if not math.isnan(se) else "")
        body_rows.append({"label": label, "cells": coef_cells, "kind": "coef"})
        body_rows.append({"label": "", "cells": se_cells, "kind": "se"})

    footer_rows = [
        {"label": "Industry FE", "cells": ["Y"] * len(models)},
        {"label": "All baseline covars.", "cells": all_covars_flags},
        {"label": "Baseline year", "cells": ["2016"] * len(models)},
        {
            "label": "Adj. R²",
            "cells": [fmt_num(adj_r2) for _metric_results, adj_r2, _nobs in results_by_spec],
        },
        {
            "label": "Observations",
            "cells": [f"{nobs:,}" for _metric_results, _adj_r2, nobs in results_by_spec],
        },
    ]

    return {
        "title": title,
        "note": note,
        "dependent_label": dependent_label,
        "models": models,
        "body_rows": body_rows,
        "footer_rows": footer_rows,
        "landscape": True,
    }


def summarize_table_6_as_patent_mismatch_tplus1(panel_path: str | Path) -> dict[str, object]:
    note = (
        "This table presents the methodology-aligned AI-washing specification on the regression-ready ever-speaker annual panel. "
        "The dependent variable is `log(1 + AI patents)` at `t+1`. Rows report the main `A_S` ratio and its interaction with `PatentMismatch`. "
        "PatentMismatch flags AI-talking firm-years with low credibility (`low A_S / high SpecShare`) and weak contemporaneous AI patenting relative to the industry-year mean. "
        "Columns vary the fixed-effects structure and sample trim while keeping the same baseline control set: size, leverage, cash/assets, R&D/assets, CAPX/assets, ROA, sales growth, and employees. "
        "Standard errors clustered at the firm level are shown in parentheses. Constants are omitted. (* p<0.1, ** p<0.05, *** p<0.01)."
    )
    return _summarize_mismatch_matrix(
        panel_path,
        dependent="log_patents_ai_lead1",
        title="Table 6. A/S Ratio, Patent Mismatch, and Future AI Patenting",
        dependent_label="Dependent variable: log(1 + AI patents at t+1)",
        note=note,
    )


def summarize_table_6b_as_patent_mismatch_tplus2(panel_path: str | Path) -> dict[str, object]:
    note = (
        "This companion table presents the same methodology-aligned AI-washing specification as Table 6 but uses the longer-horizon outcome `log(1 + AI patents)` at `t+2`. "
        "Rows report the main `A_S` ratio and its interaction with `PatentMismatch`. PatentMismatch is constructed from year-`t` disclosure credibility and contemporaneous AI patenting relative to the industry-year. "
        "Columns vary the fixed-effects structure and sample trim while keeping the same baseline control set: size, leverage, cash/assets, R&D/assets, CAPX/assets, ROA, sales growth, and employees. "
        "Standard errors clustered at the firm level are shown in parentheses. Constants are omitted. (* p<0.1, ** p<0.05, *** p<0.01)."
    )
    return _summarize_mismatch_matrix(
        panel_path,
        dependent="log_patents_ai_lead2",
        title="Table 6B. A/S Ratio, Patent Mismatch, and Longer-Horizon AI Patenting",
        dependent_label="Dependent variable: log(1 + AI patents at t+2)",
        note=note,
    )


def summarize_table_7_mismatch_determinants(panel_path: str | Path) -> dict[str, object]:
    note = (
        "This table presents firm-level cross-sectional regressions examining the determinants of PatentMismatch. "
        "The dependent variable is an indicator for whether the firm records at least one PatentMismatch incident during `2016-2024`. "
        "Independent variables are baseline firm characteristics measured in 2016: log assets, cash/assets, leverage, R&D/assets, CAPX/assets, ROA, and employees (k). "
        "All specifications include industry fixed effects based on baseline `sic2`, and standard errors clustered at the industry level are shown in parentheses. "
        "Columns (1)-(7) report one-variable specifications; column (8) includes all baseline characteristics jointly. Constants are omitted. (* p<0.1, ** p<0.05, *** p<0.01)."
    )
    return _summarize_mismatch_determinants(
        panel_path,
        dependent="ever_mismatch",
        title="Table 7. Firm-Level Determinants of PatentMismatch",
        dependent_label="Dependent variable: any PatentMismatch incident, 2016-2024",
        note=note,
    )


def summarize_table_7b_mismatch_intensity(panel_path: str | Path) -> dict[str, object]:
    note = (
        "This companion table presents firm-level cross-sectional regressions using PatentMismatch intensity rather than the extensive-margin indicator. "
        "The dependent variable is the share of AI-talking years during `2016-2024` that are flagged as PatentMismatch. "
        "Independent variables are baseline firm characteristics measured in 2016: log assets, cash/assets, leverage, R&D/assets, CAPX/assets, ROA, and employees (k). "
        "All specifications include industry fixed effects based on baseline `sic2`, and standard errors clustered at the industry level are shown in parentheses. "
        "Columns (1)-(7) report one-variable specifications; column (8) includes all baseline characteristics jointly. Constants are omitted. (* p<0.1, ** p<0.05, *** p<0.01)."
    )
    return _summarize_mismatch_determinants(
        panel_path,
        dependent="mismatch_share_talk",
        title="Table 7B. Firm-Level Determinants of PatentMismatch Intensity",
        dependent_label="Dependent variable: PatentMismatch share among AI-talking years, 2016-2024",
        note=note,
    )


def summarize_table_7c_mismatch_determinants_reduced(panel_path: str | Path) -> dict[str, object]:
    note = (
        "This refinement revisits the firm-level PatentMismatch determinants table using a reduced baseline characteristic set to preserve sample size. "
        "The dependent variable is an indicator for whether the firm records at least one PatentMismatch incident during `2016-2024`. "
        "Baseline characteristics are measured in 2016 and include log assets, cash/assets, leverage, CAPX/assets, and ROA. "
        "R&D/assets and employees are omitted from this variant because they sharply reduce the multivariate complete-case sample. "
        "All specifications include industry fixed effects based on baseline `sic2`, and standard errors clustered at the industry level are shown in parentheses. "
        "Columns (1)-(5) report one-variable specifications; column (6) includes all reduced baseline characteristics jointly. Constants are omitted. (* p<0.1, ** p<0.05, *** p<0.01)."
    )
    return _summarize_mismatch_determinants(
        panel_path,
        dependent="ever_mismatch",
        title="Table 7C. Firm-Level Determinants of PatentMismatch (Reduced Baseline Set)",
        dependent_label="Dependent variable: any PatentMismatch incident, 2016-2024",
        note=note,
        metrics=DETERMINANT_METRICS_REDUCED,
    )


def summarize_table_7d_mismatch_intensity_reduced(panel_path: str | Path) -> dict[str, object]:
    note = (
        "This companion refinement revisits PatentMismatch intensity using the reduced baseline characteristic set that preserves sample size. "
        "The dependent variable is the share of AI-talking years during `2016-2024` that are flagged as PatentMismatch. "
        "Baseline characteristics are measured in 2016 and include log assets, cash/assets, leverage, CAPX/assets, and ROA. "
        "R&D/assets and employees are omitted from this variant because they sharply reduce the multivariate complete-case sample. "
        "All specifications include industry fixed effects based on baseline `sic2`, and standard errors clustered at the industry level are shown in parentheses. "
        "Columns (1)-(5) report one-variable specifications; column (6) includes all reduced baseline characteristics jointly. Constants are omitted. (* p<0.1, ** p<0.05, *** p<0.01)."
    )
    return _summarize_mismatch_determinants(
        panel_path,
        dependent="mismatch_share_talk",
        title="Table 7D. Firm-Level Determinants of PatentMismatch Intensity (Reduced Baseline Set)",
        dependent_label="Dependent variable: PatentMismatch share among AI-talking years, 2016-2024",
        note=note,
        metrics=DETERMINANT_METRICS_REDUCED,
    )
