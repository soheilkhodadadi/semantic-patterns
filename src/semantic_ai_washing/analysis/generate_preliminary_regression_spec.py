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
DEFAULT_PANEL_INPUT = "data/processed/panel/panel_ai_patents_controls.csv"
DEFAULT_PANEL_REG_READY = "data/processed/panel/panel_reg_ready.csv"
DEFAULT_OUTPUT_DIR = "results/01_baseline/tables"


MINIMAL_REQUIRED_COLUMNS = ["cik", "year", "n_A", "n_S", "patents_ai"]
OPTIONAL_REQUIRED_COLUMNS = ["n_total"]
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
        "equation": "log_patents_ai_lead1 ~ log_n_A + log_n_S + [log_docs] + controls + C(cik) + C(year)",
        "notes": "Primary k=1 count specification with firm/year fixed effects and firm-clustered SEs.",
        "estimator": "OLS",
    },
    {
        "model_id": "OLS_k1_dummies",
        "model_name": "Patents t+1 (log) ~ dummies + FE",
        "equation": "log_patents_ai_lead1 ~ has_actionable + has_spec_only + [log_docs] + controls + C(cik) + C(year)",
        "notes": "Primary k=1 disclosure-binary specification.",
        "estimator": "OLS",
    },
    {
        "model_id": "OLS_k0_logcounts",
        "model_name": "Patents t (log) ~ log counts + FE",
        "equation": "log_patents_ai_lead0 ~ log_n_A + log_n_S + [log_docs] + controls + C(cik) + C(year)",
        "notes": "Contemporaneous log-count specification for robustness.",
        "estimator": "OLS",
    },
    {
        "model_id": "LPM_anypat_k1_dummies",
        "model_name": "Any AI patent t+1 (LPM) ~ dummies + FE",
        "equation": "any_pat_1 ~ has_actionable + has_spec_only + [log_docs] + controls + C(cik) + C(year)",
        "notes": "Binary outcome alternative: whether firm has >0 AI patents in t+1.",
        "estimator": "OLS (LPM)",
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

    if any(c not in frame.columns for c in MINIMAL_REQUIRED_COLUMNS):
        status = "blocked"
        missing = [c for c in MINIMAL_REQUIRED_COLUMNS if c not in frame.columns]
        gating.extend([f"missing_required_column::{c}" for c in missing])
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
            f"Run semantic_ai_washing.aggregation.build_panel with input ai-patents and controls "
            f"to create {args.panel_input}."
        )
    if not panel_ready_meta["exists"]:
        blocking_issues.append("missing_panel_reg_ready")
        todos.append(
            "Run semantic_ai_washing.analysis.prepare_panel_for_regression to materialize "
            f"{args.panel_reg_ready}."
        )
    if panel_summary_payload["missing_required_columns"]:
        blocking_issues.extend(panel_summary_payload["missing_required_columns"])
        todos.append(
            "Rebuild panel_reg_ready so required columns cik/year/n_A/n_S/patents_ai are present."
        )
    if panel_summary_payload.get("duplicate_cik_year", 0) > 0:
        blocking_issues.append("panel_reg_ready_duplicate_cik_year")
        todos.append(
            "Resolve duplicate (cik, year) rows in panel_reg_ready before running regression."
        )

    if not panel_ready_meta["exists"] or not panel_input_meta["exists"]:
        status = "blocked"
    elif panel_gate["status"] != "ready":
        status = "blocked"
    elif blocking_issues:
        status = "blocked"
    else:
        status = "ready"

    if not status:
        status = panel_gate["status"]

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
                    "ln_assets",
                    "leverage",
                    "cash",
                    "rd_intensity",
                    "capx_at",
                    "roa",
                    "sales_growth",
                    "emp",
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
            "crosswalks": {
                "path": "data/externals/crosswalks/cik_gvkey.csv",
                "status": "required_for_panel_work_not_required_for_current_script",
            },
        },
        "data_quality": {
            "panel_reg_ready": panel_summary_payload,
            "blocking_issues": blocking_issues,
        },
        "modeling": {
            "estimation_mode": "minimal",
            "fallback_mode": "full",
            "primary_models": PRIMARY_MODEL_SPEC,
            "full_model_catalog": [
                "OLS_k0_levels",
                "OLS_k0_shares",
                "OLS_k0_logcounts",
                "OLS_k0_dummies",
                "OLS_k1_levels",
                "OLS_k1_shares",
                "OLS_k1_logcounts",
                "OLS_k1_dummies",
                "OLS_k2_levels",
                "OLS_k2_logcounts",
                "OLS_k2_dummies",
                "LPM_anypat_k1",
                "LPM_anypat_k1_logcounts",
                "LPM_anypat_k1_dummies",
            ],
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
                "doc_transform": "log_docs",
                "controls": CONTROL_CANDIDATES,
            },
            "estimator_conventions": {
                "fixed_effects": ["firm (C(cik))", "year (C(year))"],
                "cluster": "cik",
                "standard_errors": "clustered",
            },
        },
        "outputs": {
            "artifact_dir": str(outdir),
            "files": expected_outputs(outdir),
        },
        "gating_and_todos": {
            "ready": status == "ready",
            "status": status,
            "todos": todos
            or (
                ["No blocking issues detected; run in minimal mode."] if status == "ready" else []
            ),
        },
        "commands": {
            "build_panel": "python -m semantic_ai_washing.aggregation.build_panel",
            "prepare_panel": "python -m semantic_ai_washing.analysis.prepare_panel_for_regression",
            "run_regressions_minimal": "python -m semantic_ai_washing.analysis.run_regressions --panel "
            f"{args.panel_reg_ready} --outdir {args.outdir} --mode minimal",
            "run_regressions_full": "python -m semantic_ai_washing.analysis.run_regressions --panel "
            f"{args.panel_reg_ready} --outdir {args.outdir} --mode full",
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
