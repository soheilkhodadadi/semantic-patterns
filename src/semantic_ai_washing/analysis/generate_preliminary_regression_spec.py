"""Generate a preliminary regression specification scaffold for the paper lane."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_REPORT_PATH = "reports/analysis/regression_specification_prelim_v1.json"
DEFAULT_PANEL_INPUT = (
    "data/processed/panel/panel_ai_patents_controls_2016_2024_applied_v2_legalnorm_unique.csv"
)
DEFAULT_PANEL_REG_READY = (
    "data/processed/panel/panel_reg_ready_2016_2024_applied_v2_legalnorm_unique.csv"
)
DEFAULT_OUTPUT_DIR = "results/01_baseline/tables_2016_2024_applied_v2_legalnorm_unique"


MINIMAL_REQUIRED_COLUMNS = ["cik", "year", "n_A", "n_S", "patents_ai"]
OPTIONAL_REQUIRED_COLUMNS = ["n_total", "n_I", "sic", "sic2"]
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

PRIMARY_MODEL_SPEC = [
    {
        "model_id": "OLS_k1_logcounts",
        "model_name": "Patents t+1 (log) ~ log counts + FE",
        "equation": "log_patents_ai_lead1 ~ log_n_A + log_n_S + controls + C(cik) + C(year)",
        "notes": "Primary k=1 count specification with firm/year fixed effects and firm-clustered SEs.",
        "estimator": "OLS",
    },
    {
        "model_id": "OLS_k1_dummies",
        "model_name": "Patents t+1 (log) ~ dummies + FE",
        "equation": "log_patents_ai_lead1 ~ has_actionable + has_spec_only + controls + C(cik) + C(year)",
        "notes": "Primary k=1 disclosure-binary specification.",
        "estimator": "OLS",
    },
    {
        "model_id": "OLS_k0_logcounts",
        "model_name": "Patents t (log) ~ log counts + FE",
        "equation": "log_patents_ai_lead0 ~ log_n_A + log_n_S + controls + C(cik) + C(year)",
        "notes": "Contemporaneous log-count specification for robustness.",
        "estimator": "OLS",
    },
    {
        "model_id": "LPM_anypat_k1_dummies",
        "model_name": "Any AI patent t+1 (LPM) ~ dummies + FE",
        "equation": "any_pat_1 ~ has_actionable + has_spec_only + controls + C(cik) + C(year)",
        "notes": "Binary outcome alternative: whether firm has >0 AI patents in t+1.",
        "estimator": "OLS (LPM)",
    },
]

PORTFOLIO_MODEL_SPEC = [
    {
        "model_id": "portfolio_lpm_anypat_k1_dummies_fe",
        "model_name": "Any AI patent t+1 (LPM) ~ disclosure dummies + firm/year FE",
        "family": "headline_dual",
        "estimator": "LPM",
        "dependent_variable": "any_pat_1",
        "rhs": ["has_actionable", "has_spec_only"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["firm", "year"],
        "cluster": "cik",
        "sample_filter": "full",
        "tier": "baseline",
        "notes": "Headline binary future-patent specification with firm and year fixed effects.",
    },
    {
        "model_id": "portfolio_logit_anypat_k1_dummies_industry_year",
        "model_name": "Any AI patent t+1 (logit) ~ disclosure dummies + industry/year FE",
        "family": "headline_dual",
        "estimator": "LOGIT",
        "dependent_variable": "any_pat_1",
        "rhs": ["has_actionable", "has_spec_only"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["industry", "year"],
        "cluster": "cik",
        "sample_filter": "full",
        "tier": "baseline",
        "notes": "Logit robustness that avoids high-dimensional firm FE.",
    },
    {
        "model_id": "portfolio_poisson_patents_k1_logcounts_fe",
        "model_name": "Patents t+1 (Poisson) ~ log counts + industry/year FE",
        "family": "count_models",
        "estimator": "POISSON",
        "dependent_variable": "patents_ai_lead1",
        "rhs": ["log_n_A", "log_n_S"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["industry", "year"],
        "cluster": "cik",
        "sample_filter": "full",
        "tier": "baseline",
        "notes": "Count-outcome robustness using logged narrative counts.",
    },
    {
        "model_id": "portfolio_lpm_anypat_k1_shares_fe",
        "model_name": "Any AI patent t+1 (LPM) ~ shares + firm/year FE",
        "family": "share_models",
        "estimator": "LPM",
        "dependent_variable": "any_pat_1",
        "rhs": ["ActShare", "SpecShare"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["firm", "year"],
        "cluster": "cik",
        "sample_filter": "full",
        "tier": "robustness",
        "notes": "Share-based robustness using actionable and speculative narrative shares.",
    },
    {
        "model_id": "portfolio_logit_anypat_k1_shares_industry_year",
        "model_name": "Any AI patent t+1 (logit) ~ shares + industry/year FE",
        "family": "share_models",
        "estimator": "LOGIT",
        "dependent_variable": "any_pat_1",
        "rhs": ["ActShare", "SpecShare"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["industry", "year"],
        "cluster": "cik",
        "sample_filter": "full",
        "tier": "robustness",
        "notes": "Share-based binary-outcome robustness.",
    },
    {
        "model_id": "portfolio_lpm_anypat_k1_dummies_nonfin",
        "model_name": "Any AI patent t+1 (LPM) ~ dummies + FE, non-financial firms",
        "family": "headline_dual",
        "estimator": "LPM",
        "dependent_variable": "any_pat_1",
        "rhs": ["has_actionable", "has_spec_only"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["firm", "year"],
        "cluster": "cik",
        "sample_filter": "non_financial",
        "tier": "robustness",
        "notes": "Headline trim excluding SIC 6000-6999 firms.",
    },
    {
        "model_id": "portfolio_lpm_anypat_k1_dummies_nonreg",
        "model_name": "Any AI patent t+1 (LPM) ~ dummies + FE, non-financial/non-utility firms",
        "family": "headline_dual",
        "estimator": "LPM",
        "dependent_variable": "any_pat_1",
        "rhs": ["has_actionable", "has_spec_only"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["firm", "year"],
        "cluster": "cik",
        "sample_filter": "non_financial_non_utility",
        "tier": "appendix",
        "notes": "Cleaner corporate baseline excluding financials and utilities.",
    },
    {
        "model_id": "portfolio_ols_logcounts_k1_nonfin",
        "model_name": "Patents t+1 (log) ~ log counts + FE, non-financial firms",
        "family": "count_models",
        "estimator": "OLS",
        "dependent_variable": "log_patents_ai_lead1",
        "rhs": ["log_n_A", "log_n_S"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["firm", "year"],
        "cluster": "cik",
        "sample_filter": "non_financial",
        "tier": "appendix",
        "notes": "Sample-trim robustness for the log-count count model.",
    },
    {
        "model_id": "portfolio_lpm_anypat_k1_dummies_industry_year",
        "model_name": "Any AI patent t+1 (LPM) ~ disclosure dummies + industry/year FE",
        "family": "headline_dual",
        "estimator": "LPM",
        "dependent_variable": "any_pat_1",
        "rhs": ["has_actionable", "has_spec_only"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["industry", "year"],
        "cluster": "cik",
        "sample_filter": "full",
        "tier": "appendix",
        "notes": "Industry-year FE comparison to the firm/year headline model.",
    },
    {
        "model_id": "portfolio_poisson_patents_k1_dummies_nonfin",
        "model_name": "Patents t+1 (Poisson) ~ disclosure dummies + industry/year FE, non-financial firms",
        "family": "count_models",
        "estimator": "POISSON",
        "dependent_variable": "patents_ai_lead1",
        "rhs": ["has_actionable", "has_spec_only"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["industry", "year"],
        "cluster": "cik",
        "sample_filter": "non_financial",
        "tier": "appendix",
        "notes": "Count robustness combining non-financial trim with disclosure dummies.",
    },
    {
        "model_id": "portfolio_poisson_patents_k1_shares_nonreg",
        "model_name": "Patents t+1 (Poisson) ~ shares + industry/year FE, non-financial/non-utility firms",
        "family": "count_models",
        "estimator": "POISSON",
        "dependent_variable": "patents_ai_lead1",
        "rhs": ["ActShare", "SpecShare"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["industry", "year"],
        "cluster": "cik",
        "sample_filter": "non_financial_non_utility",
        "tier": "appendix",
        "notes": "Share-based count robustness on the cleanest corporate sample.",
    },
    {
        "model_id": "portfolio_ols_logdv_leveliv_fe",
        "model_name": "log patents t+1 (OLS) ~ raw counts + firm/year FE",
        "family": "functional_form",
        "estimator": "OLS",
        "dependent_variable": "log_patents_ai_lead1",
        "rhs": ["n_A", "n_S"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["firm", "year"],
        "cluster": "cik",
        "sample_filter": "full",
        "tier": "appendix",
        "notes": "Unlogged RHS variant.",
    },
    {
        "model_id": "portfolio_ols_leveldv_logiv_fe",
        "model_name": "patents t+1 (OLS) ~ log counts + firm/year FE",
        "family": "functional_form",
        "estimator": "OLS",
        "dependent_variable": "patents_ai_lead1",
        "rhs": ["log_n_A", "log_n_S"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["firm", "year"],
        "cluster": "cik",
        "sample_filter": "full",
        "tier": "appendix",
        "notes": "Raw-count dependent variable with logged narrative counts.",
    },
    {
        "model_id": "portfolio_ols_leveldv_leveliv_fe",
        "model_name": "patents t+1 (OLS) ~ raw counts + firm/year FE",
        "family": "functional_form",
        "estimator": "OLS",
        "dependent_variable": "patents_ai_lead1",
        "rhs": ["n_A", "n_S"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["firm", "year"],
        "cluster": "cik",
        "sample_filter": "full",
        "tier": "appendix",
        "notes": "Fully unlogged exploratory count specification.",
    },
    {
        "model_id": "portfolio_lpm_anypat_k1_gap_fe",
        "model_name": "Any AI patent t+1 (LPM) ~ speculative minus actionable share + firm/year FE",
        "family": "credibility_metrics",
        "estimator": "LPM",
        "dependent_variable": "any_pat_1",
        "rhs": ["SpecMinusAct"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["firm", "year"],
        "cluster": "cik",
        "sample_filter": "full",
        "tier": "appendix",
        "notes": "Single-gap alternative credibility measure.",
    },
    {
        "model_id": "portfolio_lpm_anypat_k1_dummies_hightech",
        "model_name": "Any AI patent t+1 (LPM) ~ dummies + FE, high-tech industries",
        "family": "cross_sectional",
        "estimator": "LPM",
        "dependent_variable": "any_pat_1",
        "rhs": ["has_actionable", "has_spec_only"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["firm", "year"],
        "cluster": "cik",
        "sample_filter": "sic2_in:35,36,37,73,87",
        "tier": "appendix",
        "notes": "Cross-sectional split focused on technology-intensive SIC2 groups.",
    },
    {
        "model_id": "portfolio_lpm_anypat_k1_dummies_sic2_73",
        "model_name": "Any AI patent t+1 (LPM) ~ dummies + FE, SIC2 73 business services",
        "family": "cross_sectional",
        "estimator": "LPM",
        "dependent_variable": "any_pat_1",
        "rhs": ["has_actionable", "has_spec_only"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["firm", "year"],
        "cluster": "cik",
        "sample_filter": "sic2_eq:73",
        "tier": "appendix",
        "notes": "Cross-sectional split for the business-services/software-heavy slice.",
    },
    {
        "model_id": "portfolio_lpm_anypat_k1_actionable_only_fe",
        "model_name": "Any AI patent t+1 (LPM) ~ actionable disclosure + firm/year FE",
        "family": "single_regressor",
        "estimator": "LPM",
        "dependent_variable": "any_pat_1",
        "rhs": ["has_actionable"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["firm", "year"],
        "cluster": "cik",
        "sample_filter": "full",
        "tier": "appendix",
        "notes": "Actionable-only headline-style model.",
    },
    {
        "model_id": "portfolio_lpm_anypat_k1_speculative_only_fe",
        "model_name": "Any AI patent t+1 (LPM) ~ speculative-only disclosure + firm/year FE",
        "family": "single_regressor",
        "estimator": "LPM",
        "dependent_variable": "any_pat_1",
        "rhs": ["has_spec_only"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["firm", "year"],
        "cluster": "cik",
        "sample_filter": "full",
        "tier": "appendix",
        "notes": "Speculative-only headline-style model.",
    },
    {
        "model_id": "portfolio_lpm_anypat_k1_actionable_only_industry_year",
        "model_name": "Any AI patent t+1 (LPM) ~ actionable disclosure + industry/year FE",
        "family": "single_regressor",
        "estimator": "LPM",
        "dependent_variable": "any_pat_1",
        "rhs": ["has_actionable"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["industry", "year"],
        "cluster": "cik",
        "sample_filter": "full",
        "tier": "appendix",
        "notes": "Actionable-only industry/year FE variant.",
    },
    {
        "model_id": "portfolio_lpm_anypat_k1_speculative_only_industry_year",
        "model_name": "Any AI patent t+1 (LPM) ~ speculative-only disclosure + industry/year FE",
        "family": "single_regressor",
        "estimator": "LPM",
        "dependent_variable": "any_pat_1",
        "rhs": ["has_spec_only"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["industry", "year"],
        "cluster": "cik",
        "sample_filter": "full",
        "tier": "appendix",
        "notes": "Speculative-only industry/year FE variant.",
    },
    {
        "model_id": "portfolio_lpm_anypat_k1_actionable_only_nofe",
        "model_name": "Any AI patent t+1 (LPM) ~ actionable disclosure, no FE",
        "family": "single_regressor",
        "estimator": "LPM",
        "dependent_variable": "any_pat_1",
        "rhs": ["has_actionable"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": [],
        "cluster": "cik",
        "sample_filter": "full",
        "tier": "appendix",
        "notes": "Actionable-only no-FE reference.",
    },
    {
        "model_id": "portfolio_lpm_anypat_k1_speculative_only_nofe",
        "model_name": "Any AI patent t+1 (LPM) ~ speculative-only disclosure, no FE",
        "family": "single_regressor",
        "estimator": "LPM",
        "dependent_variable": "any_pat_1",
        "rhs": ["has_spec_only"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": [],
        "cluster": "cik",
        "sample_filter": "full",
        "tier": "appendix",
        "notes": "Speculative-only no-FE reference.",
    },
    {
        "model_id": "portfolio_lpm_anypat_k1_aifocus_fe",
        "model_name": "Any AI patent t+1 (LPM) ~ AI_Focus + firm/year FE",
        "family": "credibility_metrics",
        "estimator": "LPM",
        "dependent_variable": "any_pat_1",
        "rhs": ["AI_Focus"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["firm", "year"],
        "cluster": "cik",
        "sample_filter": "full",
        "tier": "appendix",
        "notes": "Narrative intensity as its own focal regressor family.",
    },
    {
        "model_id": "portfolio_lpm_anypat_k1_credai_fe",
        "model_name": "Any AI patent t+1 (LPM) ~ CredAI + firm/year FE",
        "family": "credibility_metrics",
        "estimator": "LPM",
        "dependent_variable": "any_pat_1",
        "rhs": ["CredAI"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["firm", "year"],
        "cluster": "cik",
        "sample_filter": "full",
        "tier": "appendix",
        "notes": "Credibility index from standardized actionable minus speculative counts.",
    },
    {
        "model_id": "portfolio_lpm_anypat_k1_asratio_fe",
        "model_name": "Any AI patent t+1 (LPM) ~ A_S + firm/year FE",
        "family": "credibility_metrics",
        "estimator": "LPM",
        "dependent_variable": "any_pat_1",
        "rhs": ["A_S"],
        "include_log_docs": False,
        "controls": CONTROL_CANDIDATES,
        "fixed_effects": ["firm", "year"],
        "cluster": "cik",
        "sample_filter": "full",
        "tier": "appendix",
        "notes": "Actionable-to-speculative log ratio from the methodology credibility architecture.",
    },
]


def sha256_file(path: str | Path) -> str | None:
    """Return SHA-256 checksum for a file, or None when file is missing."""
    resolved = Path(path)
    if not resolved.exists():
        return None
    hasher = hashlib.sha256()
    with resolved.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def file_metadata(path: str | Path) -> dict[str, Any]:
    """Return lightweight provenance fields for an expected artifact."""
    resolved = Path(path)
    if not resolved.exists():
        return {
            "path": str(resolved),
            "exists": False,
            "sha256": None,
            "size_bytes": None,
            "mtime_utc": None,
        }
    stat = resolved.stat()
    return {
        "path": str(resolved),
        "exists": True,
        "sha256": sha256_file(resolved),
        "size_bytes": int(stat.st_size),
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
    }


def expected_outputs(outdir: str | Path) -> list[str]:
    """Return expected regression outputs for the baseline path."""
    outdir_path = Path(outdir)
    return [
        str(outdir_path / "baseline_table.txt"),
        str(outdir_path / "baseline_table.tex"),
        str(outdir_path / "baseline_table_clean.md"),
        str(outdir_path / "baseline_table_clean.html"),
        str(outdir_path / "baseline_coefficients.csv"),
        str(outdir_path / "baseline_table_clean.docx"),
        str(outdir_path / "portfolio_summary.md"),
        str(outdir_path / "portfolio_summary.csv"),
        str(outdir_path / "portfolio_manifest.json"),
        str(outdir_path / "portfolio_coefficients.csv"),
    ]


def panel_summary(path: str | Path) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    """Read panel and collect checks for minimal regression readiness."""
    if not Path(path).exists():
        summary = {
            "rows": 0,
            "columns": [],
            "duplicate_cik_year": 0,
            "missing_required_columns": [],
            "nonnull_counts": {},
        }
        return summary, {"status": "missing"}, ["panel_reg_ready missing"]

    frame = pd.read_csv(path)
    missing_required = [c for c in MINIMAL_REQUIRED_COLUMNS if c not in frame.columns]
    duplicate_keys = 0
    if "cik" in frame.columns and "year" in frame.columns:
        duplicate_keys = int(
            frame.dropna(subset=["cik", "year"]).duplicated(subset=["cik", "year"]).sum()
        )

    summary = {
        "rows": int(len(frame)),
        "columns": list(frame.columns),
        "duplicate_cik_year": duplicate_keys,
        "missing_required_columns": missing_required,
        "nonnull_counts": {
            c: int(frame[c].notna().sum()) for c in MINIMAL_REQUIRED_COLUMNS if c in frame.columns
        },
    }
    controls_present = [c for c in CONTROL_CANDIDATES if c in frame.columns]

    gating = []
    status = "ready" if not missing_required else "blocked"

    if missing_required:
        gating.extend([f"missing_required_column::{c}" for c in missing_required])
    if summary["rows"] == 0:
        status = "blocked"
        gating.append("panel_reg_ready_empty")

    summary["controls_available"] = controls_present
    return summary, {"status": status, "blocking_issues": gating}, []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel-input", default=DEFAULT_PANEL_INPUT)
    parser.add_argument("--panel-reg-ready", default=DEFAULT_PANEL_REG_READY)
    parser.add_argument("--outdir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--output", default=DEFAULT_REPORT_PATH)
    return parser.parse_args()


def build_spec(args: argparse.Namespace) -> dict[str, Any]:
    panel_input_meta = file_metadata(args.panel_input)
    panel_ready_meta = file_metadata(args.panel_reg_ready)
    outdir = Path(args.outdir)

    panel_summary_payload, panel_gate, _ = panel_summary(args.panel_reg_ready)
    blocking_issues: list[str] = []
    todos: list[str] = []

    if not panel_input_meta["exists"]:
        blocking_issues.append("missing_panel_input")
        todos.append(
            f"Run semantic_ai_washing.aggregation.build_panel to create {args.panel_input}."
        )
    if not panel_ready_meta["exists"]:
        blocking_issues.append("missing_panel_reg_ready")
        todos.append(
            f"Run semantic_ai_washing.analysis.prepare_panel_for_regression to create {args.panel_reg_ready}."
        )
    if panel_summary_payload["missing_required_columns"]:
        blocking_issues.extend(panel_summary_payload["missing_required_columns"])
        todos.append(
            "Rebuild panel_reg_ready so required columns cik/year/n_A/n_S/patents_ai are present."
        )
    if panel_summary_payload.get("duplicate_cik_year", 0) > 0:
        blocking_issues.append("panel_reg_ready_duplicate_cik_year")
        todos.append("Resolve duplicate (cik, year) rows in panel_reg_ready before running regression.")

    if not panel_ready_meta["exists"] or not panel_input_meta["exists"]:
        status = "blocked"
    elif panel_gate["status"] != "ready":
        status = "blocked"
    elif blocking_issues:
        status = "blocked"
    else:
        status = "ready"

    spec = {
        "artifact": "preliminary_regression_spec_prelim_v1",
        "version": 1,
        "generated_at_utc": datetime.now(tz=timezone.utc).isoformat(),
        "status": status,
        "scope": "preliminary_results",
        "intended_inputs": {
            "panel_merge_input": {
                "path": args.panel_input,
                "metadata": panel_input_meta,
                "expected_columns": [
                    "cik",
                    "year",
                    "doc_count",
                    "n_total",
                    "n_A",
                    "n_S",
                    "n_I",
                    "ai_total",
                    "share_A",
                    "share_S",
                    "share_I",
                    "patents_ai",
                    "patents_total",
                    *CONTROL_CANDIDATES,
                    "sic",
                ],
            },
            "panel_reg_ready": {
                "path": args.panel_reg_ready,
                "metadata": panel_ready_meta,
                "required_columns": MINIMAL_REQUIRED_COLUMNS,
                "optional_columns": [
                    *OPTIONAL_REQUIRED_COLUMNS,
                    *CONTROL_CANDIDATES,
                    "share_A",
                    "share_S",
                    "share_I",
                    "AI_Focus",
                    "CredAI",
                    "A_S",
                    "SpecMinusAct",
                    "log_docs",
                    "log_n_A",
                    "log_n_S",
                    "log_n_I",
                    "has_actionable",
                    "has_spec_only",
                    "ActShare",
                    "SpecShare",
                ],
            },
        },
        "data_quality": {
            "panel_reg_ready": panel_summary_payload,
            "blocking_issues": blocking_issues,
        },
        "modeling": {
            "estimation_mode": "portfolio_modular",
            "fallback_mode": "minimal",
            "primary_models": PRIMARY_MODEL_SPEC,
            "portfolio_models": PORTFOLIO_MODEL_SPEC,
            "leads_supported": [0, 1, 2],
            "dependent_variables": {
                "patents_count": "patents_ai",
                "transforms": [
                    "log_patents_ai_lead0",
                    "log_patents_ai_lead1",
                    "log_patents_ai_lead2",
                ],
                "binary_outcome": "any_pat_1",
            },
            "features": {
                "counts": ["n_A", "n_S", "n_I", "n_total"],
                "shares": ["share_A", "share_S", "share_I", "ActShare", "SpecShare"],
                "credibility_metrics": ["AI_Focus", "CredAI", "A_S", "SpecMinusAct"],
                "doc_transform": "log_docs (descriptive only; not a default control)",
                "controls": CONTROL_CANDIDATES,
            },
            "estimator_conventions": {
                "cluster": "cik",
                "standard_errors": "clustered",
            },
            "sample_filters_supported": {
                "full": "All cleaned firm-year observations in the regression-ready panel.",
                "non_financial": "Exclude SIC 6000-6999 firm-years.",
                "non_financial_non_utility": "Exclude SIC 4900-4999 and SIC 6000-6999 firm-years.",
                "sic2_eq:<code>": "Keep only SIC2 equal to the supplied two-digit code.",
                "sic2_in:<a,b,...>": "Keep only SIC2 codes in the supplied comma-separated set.",
                "sic2_notin:<a,b,...>": "Drop SIC2 codes in the supplied comma-separated set.",
            },
        },
        "outputs": {
            "artifact_dir": str(outdir),
            "files": expected_outputs(outdir),
        },
        "gating_and_todos": {
            "ready": status == "ready",
            "status": status,
            "todos": todos or (["No blocking issues detected; run portfolio families."] if status == "ready" else []),
        },
        "commands": {
            "build_panel": "python -m semantic_ai_washing.aggregation.build_panel",
            "prepare_panel": "python -m semantic_ai_washing.analysis.prepare_panel_for_regression",
            "run_regressions_minimal": f"python -m semantic_ai_washing.analysis.run_regressions --panel {args.panel_reg_ready} --outdir {args.outdir} --mode minimal",
            "run_regressions_full": f"python -m semantic_ai_washing.analysis.run_regressions --panel {args.panel_reg_ready} --outdir {args.outdir} --mode full",
            "run_regressions_portfolio": f"python -m semantic_ai_washing.analysis.run_regression_portfolio --panel {args.panel_reg_ready} --spec-path {args.output} --outdir {args.outdir}",
        },
    }
    return spec


def main() -> None:
    args = parse_args()
    spec = build_spec(args)
    report_path = Path(args.output)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(spec, indent=2), encoding="utf-8")
    print(f"[prelim-reg-spec] status={spec['status']} path={report_path}")


if __name__ == "__main__":
    main()
