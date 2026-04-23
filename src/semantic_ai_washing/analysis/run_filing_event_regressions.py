"""Run pilot filing-date event regressions on the matched filing estimation sample."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from math import erfc, sqrt
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

DEFAULT_INPUT = "data/processed/panel/filing_event_estimation_sample_v1.parquet"
DEFAULT_REPORT = "reports/analysis/filing_event_regressions_v1.json"
DEFAULT_COEFFICIENTS = "reports/analysis/filing_event_regressions_v1_coefficients.csv"
DEFAULT_SUMMARY = "projects/ai_washing/docs/track_a_first_car_regressions_v1.md"

CORE_CONTROLS = ["ln_assets", "leverage", "cash", "roa"]
EXTENDED_CONTROLS = ["rd_intensity", "capx_at", "sales_growth"]
FOCAL_TERMS = [
    "share_actionable",
    "share_speculative",
    "post_chatgpt",
    "share_actionable_x_post_chatgpt",
    "share_speculative_x_post_chatgpt",
]


@dataclass(frozen=True)
class ModelSpec:
    model_id: str
    dependent: str
    sample_flag: str
    covariance: str = "hc3"
    cluster_col: str | None = None
    include_year_fe: bool = False
    include_post_chatgpt: bool = False
    include_interactions: bool = False
    use_extended_controls: bool = False
    note: str = ""


@dataclass
class RegressionResult:
    model_id: str
    dependent: str
    sample_flag: str
    covariance: str
    cluster_col: str | None
    nobs: int
    unique_gvkey: int
    unique_permno: int
    k_params: int
    r_squared: float | None
    adj_r_squared: float | None
    df_resid: float | None
    formula_like: str
    focal_terms: dict[str, dict[str, float | None]]
    all_terms: dict[str, dict[str, float | None]]
    note: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    parser.add_argument("--coefficients", default=DEFAULT_COEFFICIENTS)
    parser.add_argument("--summary", default=DEFAULT_SUMMARY)
    return parser.parse_args()


MODEL_SPECS = [
    ModelSpec(
        model_id="car_m1_p1_yearfe_core_hc3",
        dependent="car_m1_p1",
        sample_flag="sample_car_core",
        include_year_fe=True,
        note="Pilot short-window CAR spec with filing-year fixed effects and core lagged controls.",
    ),
    ModelSpec(
        model_id="car_m1_p1_post_core_hc3",
        dependent="car_m1_p1",
        sample_flag="sample_car_core",
        include_post_chatgpt=True,
        include_interactions=True,
        note="Headline pilot short-window CAR spec with explicit post-ChatGPT interaction and core lagged controls.",
    ),
    ModelSpec(
        model_id="car_m1_p1_post_extended_hc3",
        dependent="car_m1_p1",
        sample_flag="sample_car_extended",
        include_post_chatgpt=True,
        include_interactions=True,
        use_extended_controls=True,
        note="Extended pilot short-window CAR spec adding R&D intensity, CAPX/assets, and sales growth.",
    ),
    ModelSpec(
        model_id="car_m1_p1_post_core_cluster_gvkey",
        dependent="car_m1_p1",
        sample_flag="sample_car_core",
        covariance="cluster",
        cluster_col="gvkey",
        include_post_chatgpt=True,
        include_interactions=True,
        note="Firm-clustered robustness version of the headline pilot CAR spec.",
    ),
    ModelSpec(
        model_id="car_m2_p2_post_core_hc3",
        dependent="car_m2_p2",
        sample_flag="sample_car_core",
        include_post_chatgpt=True,
        include_interactions=True,
        note="Wider short-window CAR robustness spec.",
    ),
    ModelSpec(
        model_id="bhar_6m_post_core_hc3",
        dependent="bhar_6m",
        sample_flag="sample_bhar_6m_core",
        include_post_chatgpt=True,
        include_interactions=True,
        note="Six-month drift pilot spec using the same AI-share interaction design.",
    ),
]


def _ensure_parent(path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def _drop_infs(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    if not columns:
        return df.copy()
    mask = np.isfinite(df[columns].astype(float).to_numpy()).all(axis=1)
    return df.loc[mask].copy()


def _control_terms(spec: ModelSpec) -> list[str]:
    terms = list(CORE_CONTROLS)
    if spec.use_extended_controls:
        terms.extend(EXTENDED_CONTROLS)
    return terms


def _prepare_sample(df: pd.DataFrame, spec: ModelSpec) -> pd.DataFrame:
    if spec.sample_flag not in df.columns:
        raise KeyError(f"Missing sample flag '{spec.sample_flag}'")
    use = df.loc[df[spec.sample_flag].eq(1)].copy()
    if spec.include_interactions:
        use["share_actionable_x_post_chatgpt"] = use["share_actionable"].astype(float) * use[
            "post_chatgpt"
        ].astype(float)
        use["share_speculative_x_post_chatgpt"] = use["share_speculative"].astype(float) * use[
            "post_chatgpt"
        ].astype(float)
    numeric_needed = [
        spec.dependent,
        "share_actionable",
        "share_speculative",
        *_control_terms(spec),
    ]
    if spec.include_post_chatgpt:
        numeric_needed.append("post_chatgpt")
    if spec.include_interactions:
        numeric_needed.extend(
            ["share_actionable_x_post_chatgpt", "share_speculative_x_post_chatgpt"]
        )
    use = use.dropna(subset=numeric_needed)
    use = _drop_infs(use, numeric_needed)
    if use.empty:
        raise ValueError(f"No usable rows remain for model {spec.model_id}")
    return use


def _design_matrix(
    use: pd.DataFrame, spec: ModelSpec
) -> tuple[np.ndarray, np.ndarray, list[str], pd.DataFrame]:
    pieces: list[pd.DataFrame] = []
    names: list[str] = []

    const = pd.DataFrame({"const": np.ones(len(use), dtype=float)}, index=use.index)
    pieces.append(const)
    names.append("const")

    base_cols = ["share_actionable", "share_speculative"]
    if spec.include_post_chatgpt:
        base_cols.append("post_chatgpt")
    if spec.include_interactions:
        base_cols.extend(["share_actionable_x_post_chatgpt", "share_speculative_x_post_chatgpt"])
    base_cols.extend(_control_terms(spec))
    base = use[base_cols].astype(float)
    pieces.append(base)
    names.extend(base_cols)

    if spec.include_year_fe:
        year = pd.to_numeric(use["filing_year"], errors="coerce")
        year_mask = year.notna()
        use = use.loc[year_mask].copy()
        year = year.loc[use.index].astype(int).astype(str)
        pieces = [piece.loc[use.index] for piece in pieces]
        fe = pd.get_dummies(year, prefix="year", drop_first=True, dtype=float)
        pieces.append(fe)
        names.extend(fe.columns.tolist())

    x_frame = pd.concat(pieces, axis=1)
    y = use[spec.dependent].astype(float).to_numpy()
    x = x_frame.astype(float).to_numpy()
    return y, x, names, use


def _fit_ols(
    y: np.ndarray, x: np.ndarray, *, covariance: str, clusters: np.ndarray | None = None
) -> dict[str, Any]:
    nobs, k_params = x.shape
    xtx = x.T @ x
    xtx_inv = np.linalg.pinv(xtx)
    beta = xtx_inv @ x.T @ y
    fitted = x @ beta
    resid = y - fitted
    rss = float(resid.T @ resid)
    tss = float(((y - y.mean()) ** 2).sum())
    r_squared = None if np.isclose(tss, 0.0) else 1.0 - (rss / tss)
    df_resid = max(nobs - k_params, 1)
    adj_r_squared = None
    if r_squared is not None and nobs > k_params:
        adj_r_squared = 1.0 - (1.0 - r_squared) * ((nobs - 1) / (nobs - k_params))

    if covariance == "hc3":
        hat_diag = np.sum(x * (x @ xtx_inv), axis=1)
        denom = np.clip(1.0 - hat_diag, 1e-12, None)
        scaled = resid / denom
        meat = x.T @ ((scaled**2)[:, None] * x)
        vcov = xtx_inv @ meat @ xtx_inv
        se_df = df_resid
    elif covariance == "cluster":
        if clusters is None:
            raise ValueError("cluster covariance requires cluster labels")
        cluster_series = pd.Series(clusters)
        valid = cluster_series.notna().to_numpy()
        if not valid.all():
            x = x[valid]
            y = y[valid]
            resid = resid[valid]
            cluster_series = cluster_series.loc[valid].reset_index(drop=True)
            nobs, k_params = x.shape
            xtx = x.T @ x
            xtx_inv = np.linalg.pinv(xtx)
            beta = xtx_inv @ x.T @ y
            fitted = x @ beta
            resid = y - fitted
            rss = float(resid.T @ resid)
            tss = float(((y - y.mean()) ** 2).sum())
            r_squared = None if np.isclose(tss, 0.0) else 1.0 - (rss / tss)
            df_resid = max(nobs - k_params, 1)
            if r_squared is not None and nobs > k_params:
                adj_r_squared = 1.0 - (1.0 - r_squared) * ((nobs - 1) / (nobs - k_params))
        meat = np.zeros((k_params, k_params), dtype=float)
        groups = cluster_series.astype(str)
        unique_groups = groups.unique()
        for group in unique_groups:
            mask = groups.eq(group).to_numpy()
            x_g = x[mask]
            resid_g = resid[mask]
            score = x_g.T @ resid_g
            meat += np.outer(score, score)
        g = len(unique_groups)
        factor = 1.0
        if g > 1 and nobs > k_params:
            factor = (g / (g - 1)) * ((nobs - 1) / (nobs - k_params))
        vcov = factor * (xtx_inv @ meat @ xtx_inv)
        se_df = max(g - 1, 1)
    else:
        raise ValueError(f"Unsupported covariance '{covariance}'")

    se = np.sqrt(np.clip(np.diag(vcov), 0.0, None))
    with np.errstate(divide="ignore", invalid="ignore"):
        t_stat = np.divide(beta, se, out=np.full_like(beta, np.nan), where=se > 0)
    p_value = np.array(
        [erfc(abs(float(value)) / sqrt(2.0)) if np.isfinite(value) else np.nan for value in t_stat]
    )

    return {
        "beta": beta,
        "se": se,
        "t_stat": t_stat,
        "p_value": p_value,
        "nobs": int(nobs),
        "k_params": int(k_params),
        "r_squared": r_squared,
        "adj_r_squared": adj_r_squared,
        "df_resid": float(df_resid),
        "se_df": float(se_df),
    }


def _formula_like(spec: ModelSpec) -> str:
    rhs = ["share_actionable", "share_speculative"]
    if spec.include_post_chatgpt:
        rhs.append("post_chatgpt")
    if spec.include_interactions:
        rhs.extend(
            [
                "share_actionable_x_post_chatgpt",
                "share_speculative_x_post_chatgpt",
            ]
        )
    rhs.extend(_control_terms(spec))
    if spec.include_year_fe:
        rhs.append("C(filing_year)")
    return f"{spec.dependent} ~ {' + '.join(rhs)}"


def _format_term_map(
    term_names: list[str], fit: dict[str, Any]
) -> dict[str, dict[str, float | None]]:
    out: dict[str, dict[str, float | None]] = {}
    for idx, term in enumerate(term_names):
        out[term] = {
            "coef": float(fit["beta"][idx]),
            "se": float(fit["se"][idx]),
            "t_stat": float(fit["t_stat"][idx]),
            "p_value": float(fit["p_value"][idx]),
        }
    return out


def run_models(df: pd.DataFrame) -> tuple[list[RegressionResult], pd.DataFrame]:
    results: list[RegressionResult] = []
    coefficient_rows: list[dict[str, Any]] = []

    for spec in MODEL_SPECS:
        use = _prepare_sample(df, spec)
        y, x, names, use = _design_matrix(use, spec)
        clusters = None
        if spec.covariance == "cluster" and spec.cluster_col:
            clusters = use[spec.cluster_col].to_numpy()
        fit = _fit_ols(y, x, covariance=spec.covariance, clusters=clusters)
        term_map = _format_term_map(names, fit)
        focal = {
            term: term_map.get(term, {"coef": None, "se": None, "t_stat": None, "p_value": None})
            for term in FOCAL_TERMS
        }
        results.append(
            RegressionResult(
                model_id=spec.model_id,
                dependent=spec.dependent,
                sample_flag=spec.sample_flag,
                covariance=spec.covariance,
                cluster_col=spec.cluster_col,
                nobs=fit["nobs"],
                unique_gvkey=int(use["gvkey"].nunique()),
                unique_permno=int(use["permno"].nunique()),
                k_params=fit["k_params"],
                r_squared=fit["r_squared"],
                adj_r_squared=fit["adj_r_squared"],
                df_resid=fit["df_resid"],
                formula_like=_formula_like(spec),
                focal_terms=focal,
                all_terms=term_map,
                note=spec.note,
            )
        )
        for term, values in term_map.items():
            coefficient_rows.append(
                {
                    "model_id": spec.model_id,
                    "dependent": spec.dependent,
                    "term": term,
                    **values,
                    "nobs": fit["nobs"],
                    "covariance": spec.covariance,
                    "sample_flag": spec.sample_flag,
                }
            )

    coefficients = pd.DataFrame(coefficient_rows)
    return results, coefficients


def _headline_findings(results: list[RegressionResult]) -> list[str]:
    findings: list[str] = []
    for result in results:
        act = result.focal_terms.get("share_actionable", {})
        spec = result.focal_terms.get("share_speculative", {})
        if act.get("coef") is None:
            continue
        findings.append(
            (
                f"{result.model_id}: share_actionable={act['coef']:.4f} (p={act['p_value']:.3f}), "
                f"share_speculative={spec['coef']:.4f} (p={spec['p_value']:.3f}), N={result.nobs}."
            )
        )
    return findings


def build_report(
    df: pd.DataFrame, results: list[RegressionResult], *, input_path: str | None = None
) -> dict[str, Any]:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input": input_path or "",
        "sample_summary": {
            "row_count": int(len(df)),
            "unique_gvkey": int(df["gvkey"].nunique()),
            "unique_permno": int(df["permno"].nunique()),
            "filing_year_min": int(df["filing_year"].min()),
            "filing_year_max": int(df["filing_year"].max()),
            "sample_car_core": int(df["sample_car_core"].sum()),
            "sample_car_extended": int(df["sample_car_extended"].sum()),
            "sample_bhar_6m_core": int(df["sample_bhar_6m_core"].sum()),
        },
        "model_specs": [asdict(spec) for spec in MODEL_SPECS],
        "results": [asdict(result) for result in results],
        "headline_findings": _headline_findings(results),
        "notes": [
            "This is the pilot matched-filing event-study surface, not the final full-sample paper panel.",
            "Year fixed effects and explicit post-ChatGPT interactions are run as separate families because post_chatgpt is close to a time dummy.",
            "share_irrelevant is omitted as the baseline composition share.",
            "Pilot p-values use a normal approximation over HC3 or cluster-robust standard errors to keep the runner lightweight and stable in this environment.",
        ],
    }


def write_summary(report: dict[str, Any], path: str | Path) -> None:
    lines = [
        "# Filing-Date CAR Regressions",
        "",
        "## Scope",
        "",
        "This note records the first pilot filing-date event regressions on the matched filing sample.",
        "The current surface is a pipeline-validation sample, not the full paper sample.",
        "",
        "## Sample",
        "",
        f"- matched filings: `{report['sample_summary']['row_count']}`",
        f"- unique `gvkey`: `{report['sample_summary']['unique_gvkey']}`",
        f"- unique `permno`: `{report['sample_summary']['unique_permno']}`",
        f"- years: `{report['sample_summary']['filing_year_min']}-{report['sample_summary']['filing_year_max']}`",
        f"- CAR core sample: `{report['sample_summary']['sample_car_core']}`",
        f"- CAR extended sample: `{report['sample_summary']['sample_car_extended']}`",
        f"- BHAR 6m core sample: `{report['sample_summary']['sample_bhar_6m_core']}`",
        "",
        "## Headline read",
        "",
    ]
    lines.extend([f"- {item}" for item in report["headline_findings"]])
    lines.extend(["", "## Notes", ""])
    lines.extend([f"- {note}" for note in report["notes"]])
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    df = pd.read_parquet(args.input)
    results, coefficients = run_models(df)
    report = build_report(df, results, input_path=args.input)

    _ensure_parent(args.report)
    _ensure_parent(args.coefficients)
    _ensure_parent(args.summary)
    Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")
    coefficients.to_csv(args.coefficients, index=False)
    write_summary(report, args.summary)


if __name__ == "__main__":
    main()
