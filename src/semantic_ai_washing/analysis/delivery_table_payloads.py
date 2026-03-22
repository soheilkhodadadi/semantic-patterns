"""Shared payload builders for standalone delivery tables."""

from __future__ import annotations

import csv
import math
import statistics
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.regression.linear_model import OLS

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
    df = pd.read_csv(panel_path, low_memory=False)
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
    controls: list[str] | None = None,
):
    controls = controls or CONTROL_CANDIDATES
    needed = [dependent, *rhs_terms, *controls, absorb_col, "year", "cik"]
    missing = [column for column in needed if column not in df.columns]
    if missing:
        raise KeyError(f"Missing columns for absorbed model: {missing}")

    use = df.dropna(subset=needed).copy()
    numeric = [dependent, *rhs_terms, *controls]
    use = _drop_infs(use, numeric)
    work_cols = [dependent, *rhs_terms, *controls]
    matrix = use[work_cols].astype(float).to_numpy()
    absorb_codes, _ = pd.factorize(use[absorb_col], sort=False)
    time_codes, _ = pd.factorize(use["year"], sort=False)
    demeaned = _two_way_demean(matrix, absorb_codes, time_codes)
    y = demeaned[:, 0]
    x = pd.DataFrame(demeaned[:, 1:], columns=[*rhs_terms, *controls], index=use.index)
    result = OLS(y, x).fit(cov_type="cluster", cov_kwds={"groups": use["cik"]})
    adj_r2 = _compute_absorbed_adj_r2(
        y,
        np.asarray(result.fittedvalues),
        nobs=len(use),
        n_slopes=x.shape[1],
        n_entities=len(np.unique(absorb_codes)),
        n_periods=len(np.unique(time_codes)),
    )
    return result, use, adj_r2


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
    models = [{"number": f"({idx})", "label": label} for idx, (label, _) in enumerate(outcomes, start=1)]
    panel_defs = [
        ("Panel A. Actionable disclosure", "Actionable disclosure (dummy)", "has_actionable"),
        ("Panel B. Speculative-only disclosure", "Speculative-only disclosure (dummy)", "has_spec_only"),
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
    spec_defs = [
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
            "mask": df["sic2"].notna() if "sic2" in df.columns else pd.Series(False, index=df.index),
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

    panels: list[dict[str, object]] = []
    panel_defs = [
        ("Panel A. Actionable disclosure", "Actionable disclosure (dummy)", "has_actionable"),
        ("Panel B. Speculative-only disclosure", "Speculative-only disclosure (dummy)", "has_spec_only"),
    ]

    models = [{"number": spec["number"], "label": spec["label"]} for spec in spec_defs]

    footer_template = ["Controls", "Firm FE", "Industry FE", "Year FE", "Non-fin.", "No util.", "Adj. R²", "Observations"]

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
