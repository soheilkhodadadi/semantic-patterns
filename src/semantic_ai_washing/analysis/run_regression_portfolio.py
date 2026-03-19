"""Run a spec-driven regression portfolio on the prepared panel."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

from semantic_ai_washing.analysis.run_regressions import (
    VAR_LABELS,
    _star_str,
    add_engineered_cols,
    make_leads,
)


DEFAULT_PANEL = "data/processed/panel/panel_reg_ready_2016_2024_applied_v2_legalnorm_unique.csv"
DEFAULT_SPEC_PATH = "reports/analysis/regression_specification_prelim_v1.json"
DEFAULT_OUTDIR = "results/01_baseline/tables_2016_2024_applied_v2_legalnorm_unique"

FOCAL_TERMS = [
    "n_A",
    "n_S",
    "log_n_A",
    "log_n_S",
    "has_actionable",
    "has_spec_only",
    "AI_Focus",
    "CredAI",
    "A_S",
    "ActShare",
    "SpecShare",
    "SpecMinusAct",
]

FIXED_EFFECT_MAP = {
    "firm": "C(cik)",
    "year": "C(year)",
    "industry": "C(sic2)",
    "industry_year": "C(sic2):C(year)",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", default=DEFAULT_PANEL)
    parser.add_argument("--spec-path", default=DEFAULT_SPEC_PATH)
    parser.add_argument("--outdir", default=DEFAULT_OUTDIR)
    parser.add_argument(
        "--tiers",
        default="baseline,robustness",
        help="Comma-separated portfolio tiers to run (for example: baseline,robustness,appendix).",
    )
    return parser.parse_args()


def _load_specs(path: str | Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    specs = payload.get("specs")
    if specs is None:
        specs = (payload.get("modeling") or {}).get("portfolio_models", [])
    if not specs:
        raise ValueError(f"No portfolio specs found in {path}")
    seen_model_ids: set[str] = set()
    duplicates: list[str] = []
    for spec in specs:
        model_id = str(spec.get("model_id", ""))
        if model_id in seen_model_ids:
            duplicates.append(model_id)
        seen_model_ids.add(model_id)
    if duplicates:
        duplicate_list = ", ".join(sorted(set(duplicates)))
        raise ValueError(f"Duplicate portfolio model_id values in {path}: {duplicate_list}")
    return payload, specs


def _apply_sample_filter(df: pd.DataFrame, filter_name: str | None) -> pd.DataFrame:
    if filter_name in (None, "", "full"):
        return df.copy()
    if "sic" not in df.columns:
        raise KeyError("sample filters require a 'sic' column in the panel")

    sic = pd.to_numeric(df["sic"], errors="coerce")
    mask = pd.Series(True, index=df.index)
    if filter_name == "non_financial":
        mask &= ~sic.between(6000, 6999, inclusive="both")
    elif filter_name == "non_financial_non_utility":
        mask &= ~sic.between(6000, 6999, inclusive="both")
        mask &= ~sic.between(4900, 4999, inclusive="both")
    elif filter_name.startswith("sic2_eq:"):
        target = filter_name.split(":", 1)[1]
        if "sic2" not in df.columns:
            raise KeyError("sic2-based filters require a 'sic2' column")
        mask &= df["sic2"].astype(str) == target
    elif filter_name.startswith("sic2_in:"):
        if "sic2" not in df.columns:
            raise KeyError("sic2-based filters require a 'sic2' column")
        targets = {
            value.strip()
            for value in filter_name.split(":", 1)[1].split(",")
            if value.strip()
        }
        mask &= df["sic2"].astype(str).isin(targets)
    elif filter_name.startswith("sic2_notin:"):
        if "sic2" not in df.columns:
            raise KeyError("sic2-based filters require a 'sic2' column")
        targets = {
            value.strip()
            for value in filter_name.split(":", 1)[1].split(",")
            if value.strip()
        }
        mask &= ~df["sic2"].astype(str).isin(targets)
    else:
        raise ValueError(f"Unsupported sample_filter '{filter_name}'")
    return df.loc[mask].copy()


def _fixed_effect_terms(fixed_effects: list[str]) -> list[str]:
    return [FIXED_EFFECT_MAP[name] for name in fixed_effects if name in FIXED_EFFECT_MAP]


def _build_formula(dep_var: str, rhs_terms: list[str], fixed_effects: list[str]) -> str:
    terms = list(rhs_terms) + _fixed_effect_terms(fixed_effects)
    if not terms:
        raise ValueError(f"No RHS terms supplied for dependent variable {dep_var}")
    return f"{dep_var} ~ {' + '.join(terms)}"


def _drop_infs(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    if not cols:
        return df
    mask = np.isfinite(df[cols].astype(float)).all(axis=1)
    return df.loc[mask].copy()


def _prepare_model_frame(
    df: pd.DataFrame,
    *,
    dep_var: str,
    rhs_terms: list[str],
    fixed_effects: list[str],
    cluster: str,
) -> pd.DataFrame:
    needed = [dep_var, cluster, *rhs_terms]
    if "firm" in fixed_effects:
        needed.append("cik")
    if "year" in fixed_effects:
        needed.append("year")
    if "industry" in fixed_effects or "industry_year" in fixed_effects:
        needed.append("sic2")

    missing = [col for col in needed if col not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns: {missing}")

    use = df.dropna(subset=needed).copy()
    numeric_cols = [
        col
        for col in [dep_var, *rhs_terms]
        if col in use.columns and pd.api.types.is_numeric_dtype(use[col])
    ]
    use = _drop_infs(use, numeric_cols)
    if use.empty:
        raise ValueError("No rows left after dropping NA/inf for required columns.")
    return use


def _fit_model(
    df: pd.DataFrame,
    *,
    dep_var: str,
    rhs_terms: list[str],
    fixed_effects: list[str],
    estimator: str,
    cluster: str,
):
    use = _prepare_model_frame(
        df,
        dep_var=dep_var,
        rhs_terms=rhs_terms,
        fixed_effects=fixed_effects,
        cluster=cluster,
    )
    formula = _build_formula(dep_var, rhs_terms, fixed_effects)
    cov_kwds = {"groups": use[cluster]}
    estimator_upper = estimator.upper()

    if estimator_upper in {"OLS", "LPM"}:
        model = smf.ols(formula, data=use)
        result = model.fit(cov_type="cluster", cov_kwds=cov_kwds)
    elif estimator_upper == "LOGIT":
        model = smf.glm(formula, data=use, family=sm.families.Binomial())
        result = model.fit(cov_type="cluster", cov_kwds=cov_kwds)
    elif estimator_upper == "POISSON":
        model = smf.glm(formula, data=use, family=sm.families.Poisson())
        result = model.fit(cov_type="cluster", cov_kwds=cov_kwds)
    else:
        raise ValueError(f"Unsupported estimator '{estimator}'")

    return result, formula, use


def _result_stat_values(result) -> pd.Series:
    if hasattr(result, "tvalues"):
        return result.tvalues
    if hasattr(result, "zvalues"):
        return result.zvalues
    return pd.Series(np.nan, index=result.params.index)


def _format_focal_term(result, term: str) -> str:
    if term not in result.params.index:
        return ""
    coef = result.params[term]
    pvalue = result.pvalues[term]
    if pd.isna(pvalue):
        return f"{coef:.3f} (p=NaN; unstable)"
    if pvalue < 0.01:
        sig_band = "1%"
    elif pvalue < 0.05:
        sig_band = "5%"
    elif pvalue < 0.10:
        sig_band = "10%"
    else:
        sig_band = "n.s."
    return f"{coef:.3f}{_star_str(pvalue)} (p={pvalue:.3f}; {sig_band})"


def _collect_result_row(spec: dict[str, Any], result, formula: str, sample_rows: int) -> dict[str, Any]:
    row = {
        "spec_id": spec["model_id"],
        "model_name": spec.get("model_name", spec["model_id"]),
        "tier": spec.get("tier", "baseline"),
        "estimator": spec.get("estimator", ""),
        "dependent_variable": spec.get("dependent_variable", ""),
        "sample_filter": spec.get("sample_filter", "full"),
        "fixed_effects": ",".join(spec.get("fixed_effects", [])),
        "formula": formula,
        "N": int(result.nobs),
        "sample_rows_before_dropna": int(sample_rows),
        "aic": float(result.aic) if getattr(result, "aic", None) is not None else None,
        "bic": float(result.bic) if getattr(result, "bic", None) is not None else None,
    }
    for term in FOCAL_TERMS:
        row[term] = _format_focal_term(result, term)
    return row


def _nan_pvalue_terms(result) -> list[str]:
    terms: list[str] = []
    for term in FOCAL_TERMS:
        if term in result.pvalues.index and pd.isna(result.pvalues[term]):
            terms.append(term)
    return terms


def _portfolio_table(summary_rows: list[dict[str, Any]]) -> pd.DataFrame:
    display_columns = [
        "spec_id",
        "tier",
        "estimator",
        "sample_filter",
        "dependent_variable",
        "N",
        "n_A",
        "n_S",
        "log_n_A",
        "log_n_S",
        "has_actionable",
        "has_spec_only",
        "AI_Focus",
        "CredAI",
        "A_S",
        "ActShare",
        "SpecShare",
        "SpecMinusAct",
    ]
    table = pd.DataFrame(summary_rows)
    if table.empty:
        return table
    table = table.reindex(columns=display_columns)
    return table.rename(
        columns={
            "spec_id": "Spec",
            "tier": "Tier",
            "estimator": "Estimator",
            "sample_filter": "Sample",
            "dependent_variable": "Outcome",
            "N": "N",
            "n_A": VAR_LABELS.get("n_A", "n_A"),
            "n_S": VAR_LABELS.get("n_S", "n_S"),
            "log_n_A": VAR_LABELS.get("log_n_A", "log_n_A"),
            "log_n_S": VAR_LABELS.get("log_n_S", "log_n_S"),
            "has_actionable": VAR_LABELS.get("has_actionable", "has_actionable"),
            "has_spec_only": VAR_LABELS.get("has_spec_only", "has_spec_only"),
            "AI_Focus": VAR_LABELS.get("AI_Focus", "AI_Focus"),
            "CredAI": VAR_LABELS.get("CredAI", "CredAI"),
            "A_S": VAR_LABELS.get("A_S", "A_S"),
            "ActShare": VAR_LABELS.get("ActShare", "ActShare"),
            "SpecShare": VAR_LABELS.get("SpecShare", "SpecShare"),
            "SpecMinusAct": VAR_LABELS.get("SpecMinusAct", "SpecMinusAct"),
        }
    )


def _build_manifest(
    *,
    args: argparse.Namespace,
    payload: dict[str, Any],
    manifest_specs: list[dict[str, Any]],
    summary_md_path: Path,
    summary_csv_path: Path,
    coeff_path: Path,
) -> dict[str, Any]:
    return {
        "artifact": "regression_portfolio_prelim_v1",
        "generated_from_spec": str(args.spec_path),
        "panel": str(args.panel),
        "tiers_requested": [tier.strip() for tier in args.tiers.split(",") if tier.strip()],
        "portfolio_summary_markdown": str(summary_md_path),
        "portfolio_summary_csv": str(summary_csv_path),
        "portfolio_coefficients": str(coeff_path),
        "estimated_models": int(sum(item["status"] == "estimated" for item in manifest_specs)),
        "failed_models": int(sum(item["status"] == "failed" for item in manifest_specs)),
        "pending_models": int(sum(item["status"] == "pending" for item in manifest_specs)),
        "specs": manifest_specs,
        "portfolio_source_metadata": {
            "spec_artifact": payload.get("artifact"),
            "spec_generated_at_utc": payload.get("generated_at_utc"),
        },
    }


def _write_manifest(
    *,
    args: argparse.Namespace,
    payload: dict[str, Any],
    manifest_specs: list[dict[str, Any]],
    summary_md_path: Path,
    summary_csv_path: Path,
    coeff_path: Path,
    manifest_path: Path,
) -> None:
    manifest = _build_manifest(
        args=args,
        payload=payload,
        manifest_specs=manifest_specs,
        summary_md_path=summary_md_path,
        summary_csv_path=summary_csv_path,
        coeff_path=coeff_path,
    )
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _write_markdown_table(path: Path, frame: pd.DataFrame) -> None:
    if frame.empty:
        path.write_text("_Portfolio results unavailable._\n", encoding="utf-8")
        return
    headers = [str(column) for column in frame.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in frame.itertuples(index=False, name=None):
        lines.append("| " + " | ".join("" if pd.isna(value) else str(value) for value in row) + " |")
    text = "\n".join(lines)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def run_portfolio(args: argparse.Namespace) -> None:
    payload, specs = _load_specs(args.spec_path)
    tiers_requested = {tier.strip() for tier in args.tiers.split(",") if tier.strip()}
    specs = [spec for spec in specs if spec.get("tier", "baseline") in tiers_requested]
    if not specs:
        raise ValueError(f"No portfolio specs matched requested tiers: {sorted(tiers_requested)}")
    df = pd.read_csv(args.panel)
    df = add_engineered_cols(df)
    df = make_leads(df, k_list=(0, 1, 2))

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    manifest_path = outdir / "portfolio_manifest.json"
    summary_md_path = outdir / "portfolio_summary.md"
    summary_csv_path = outdir / "portfolio_summary.csv"
    coeff_path = outdir / "portfolio_coefficients.csv"

    coefficient_rows: list[pd.DataFrame] = []
    summary_rows: list[dict[str, Any]] = []
    manifest_specs: list[dict[str, Any]] = []

    for spec in specs:
        spec_record = {
            "model_id": spec.get("model_id"),
            "model_name": spec.get("model_name"),
            "status": "pending",
            "estimator": spec.get("estimator"),
            "tier": spec.get("tier", "baseline"),
            "sample_filter": spec.get("sample_filter", "full"),
            "dependent_variable": spec.get("dependent_variable"),
            "fixed_effects": spec.get("fixed_effects", []),
        }
        manifest_specs.append(spec_record)
        _write_manifest(
            args=args,
            payload=payload,
            manifest_specs=manifest_specs,
            summary_md_path=summary_md_path,
            summary_csv_path=summary_csv_path,
            coeff_path=coeff_path,
            manifest_path=manifest_path,
        )
        print(
            f"[portfolio] starting {spec['model_id']} "
            f"({spec.get('tier', 'baseline')}, {spec.get('estimator', '')})"
        )
        try:
            sample_df = _apply_sample_filter(df, spec.get("sample_filter"))
            rhs_terms = [
                term for term in spec.get("rhs", []) if term in sample_df.columns
            ]
            rhs_terms.extend(
                [
                    control
                    for control in spec.get("controls", [])
                    if control in sample_df.columns and control not in rhs_terms
                ]
            )
            result, formula, used_df = _fit_model(
                sample_df,
                dep_var=spec["dependent_variable"],
                rhs_terms=rhs_terms,
                fixed_effects=spec.get("fixed_effects", []),
                estimator=spec.get("estimator", "OLS"),
                cluster=spec.get("cluster", "cik"),
            )

            coef = result.params.to_frame("coef")
            coef["se"] = result.bse
            coef["stat"] = _result_stat_values(result)
            coef["p"] = result.pvalues
            coef["model"] = spec["model_id"]
            coef["N"] = result.nobs
            coefficient_rows.append(coef.reset_index().rename(columns={"index": "term"}))

            summary_rows.append(
                _collect_result_row(spec, result, formula, sample_rows=len(sample_df))
            )
            spec_record.update(
                {
                    "status": "estimated",
                    "formula": formula,
                    "nobs": int(result.nobs),
                    "aic": float(result.aic)
                    if getattr(result, "aic", None) is not None
                    else None,
                    "bic": float(result.bic)
                    if getattr(result, "bic", None) is not None
                    else None,
                    "sample_rows_before_dropna": int(len(sample_df)),
                    "sample_rows_estimated": int(len(used_df)),
                    "nan_pvalue_terms": _nan_pvalue_terms(result),
                }
            )
        except Exception as exc:  # noqa: BLE001
            spec_record.update({"status": "failed", "error": str(exc)})
        _write_manifest(
            args=args,
            payload=payload,
            manifest_specs=manifest_specs,
            summary_md_path=summary_md_path,
            summary_csv_path=summary_csv_path,
            coeff_path=coeff_path,
            manifest_path=manifest_path,
        )

    if coefficient_rows:
        pd.concat(coefficient_rows, ignore_index=True).to_csv(coeff_path, index=False)

    summary_table = _portfolio_table(summary_rows)
    if not summary_table.empty:
        summary_table.to_csv(summary_csv_path, index=False)
    _write_markdown_table(summary_md_path, summary_table)
    _write_manifest(
        args=args,
        payload=payload,
        manifest_specs=manifest_specs,
        summary_md_path=summary_md_path,
        summary_csv_path=summary_csv_path,
        coeff_path=coeff_path,
        manifest_path=manifest_path,
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    print(
        f"[portfolio] wrote manifest={manifest_path} "
        f"estimated={manifest['estimated_models']} failed={manifest['failed_models']}"
    )


def main() -> None:
    args = parse_args()
    run_portfolio(args)


if __name__ == "__main__":
    main()
