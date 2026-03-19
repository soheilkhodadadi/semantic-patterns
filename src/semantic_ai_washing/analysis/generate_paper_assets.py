"""Generate paper-facing snippets and tables from current project artifacts."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import pandas as pd


def _read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _fmt_pct(value: float | int | None) -> str:
    if value is None:
        return ""
    return f"{100.0 * float(value):.1f}%"


def _fmt_int(value: int | float | None) -> str:
    if value is None:
        return ""
    return f"{int(value):,}"


def _write_text(path: str | Path, text: str) -> None:
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    payload = text.rstrip() + "\n"
    temp_path = resolved.with_suffix(resolved.suffix + ".tmp")
    temp_path.write_text(payload, encoding="utf-8")
    os.replace(temp_path, resolved)


def _read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _build_benchmark_table(benchmark_matrix: dict[str, Any], selected_model_id: str) -> str:
    rows: list[dict[str, Any]] = []
    for model in benchmark_matrix.get("models", []):
        heldout = (model.get("benchmarks") or {}).get("held_out_v2", {})
        if not heldout:
            continue
        rows.append(
            {
                "Model": model.get("model_id", ""),
                "Selected": "Yes" if model.get("model_id") == selected_model_id else "",
                "Accuracy": _fmt_pct(heldout.get("accuracy")),
                "Macro F1": f"{float(heldout.get('macro_f1', 0.0)):.3f}",
                "A/S Accuracy": _fmt_pct(
                    heldout.get("actionable_speculative_conditional_accuracy")
                ),
            }
        )
    table = pd.DataFrame(rows)
    if table.empty:
        return "_Benchmark table unavailable._\n"
    return _to_markdown_table(table)


def _build_cleanup_table(cleanup: dict[str, Any]) -> str:
    rows: list[dict[str, Any]] = []
    for year, payload in sorted((cleanup.get("years") or {}).items(), key=lambda item: item[0]):
        if payload.get("status") != "cleaned":
            continue
        rows.append(
            {
                "Year": year,
                "Input": _fmt_int(payload.get("rows_input")),
                "Retained": _fmt_int(payload.get("rows_retained")),
                "Dropped": _fmt_int(payload.get("rows_dropped")),
            }
        )
    table = pd.DataFrame(rows)
    if table.empty:
        return "_Cleanup table unavailable._\n"
    return _to_markdown_table(table)


def _to_markdown_table(frame: pd.DataFrame) -> str:
    headers = [str(column) for column in frame.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in frame.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines) + "\n"


def _build_benchmark_snippet(
    *,
    selected_manifest: dict[str, Any],
    heldout_eval: dict[str, Any],
    freeze: dict[str, Any],
) -> str:
    winner = selected_manifest.get("winner", {})
    summary = heldout_eval.get("summary", {})
    freeze_summary = freeze.get("summary", {})
    return f"""
The current preliminary benchmark uses the frozen `held_out_v2` asset with {_fmt_int(freeze_summary.get("rows_total"))} reviewed sentences after excluding {_fmt_int(freeze_summary.get("rows_excluded"))} invalid rows. The selected preliminary model is `{winner.get("model_id", "")}`, chosen by held-out macro-F1 with secondary tie-breaks on overall accuracy and actionable/speculative conditional accuracy.

On the frozen held-out benchmark, the selected model achieved accuracy of {_fmt_pct(summary.get("accuracy"))}, macro-F1 of {float(summary.get("macro_f1", 0.0)):.3f}, binary relevance accuracy of {_fmt_pct(summary.get("binary_relevance_accuracy"))}, and actionable/speculative conditional accuracy of {_fmt_pct(summary.get("actionable_speculative_conditional_accuracy"))}. This clears the preliminary gate for active-window use, but it does not yet clear the stricter publication-grade accuracy threshold of {_fmt_pct(summary.get("publication_grade_threshold"))}.
""".strip()


def _build_data_snippet(
    *,
    freeze: dict[str, Any],
    cleanup: dict[str, Any],
    panel_merged_path: str | Path,
    panel_reg_ready_path: str | Path,
    controls_path: str | Path,
) -> str:
    freeze_summary = freeze.get("summary", {})
    cleanup_summary = cleanup.get("summary", {})
    label_counts = freeze_summary.get("label_counts", {})
    panel_merged = pd.read_csv(panel_merged_path, usecols=["patents_total", "patents_ai"])
    panel_reg_ready = pd.read_csv(panel_reg_ready_path, usecols=["year"])
    controls = pd.read_csv(controls_path, usecols=["year"])
    merged_rows = len(panel_merged)
    any_pat_rows = int((panel_merged["patents_total"].fillna(0) > 0).sum())
    ai_pat_rows = int((panel_merged["patents_ai"].fillna(0) > 0).sum())
    reg_ready_rows = len(panel_reg_ready)
    controls_rows = len(controls)
    return f"""
The canonical preliminary benchmark asset is `held_out_v2`, frozen at {_fmt_int(freeze_summary.get("rows_total"))} reviewed sentences. Its final label mix is {_fmt_int(label_counts.get("Actionable"))} Actionable, {_fmt_int(label_counts.get("Speculative"))} Speculative, and {_fmt_int(label_counts.get("Irrelevant"))} Irrelevant. Three malformed rows were excluded before freezing.

For the broader filing universe, the cleaned annual 10-K sentence layer currently covers {_fmt_int(cleanup_summary.get("rows_retained"))} retained AI-related sentences across `2016–2024`, down from {_fmt_int(cleanup_summary.get("rows_input"))} raw extracted rows. The cleaner drops long table-like fragments, OCR-style noise, and artifact-only `(ai)` false positives before the classification stage.

The promoted patent series for the preliminary panel is `applied_v2_legalnorm_unique`, which combines the broader applied keyword tier with assignee legal-suffix normalization and duplicate cleanup. After merging narrative measures, patents, and Compustat controls, the full `2016–2024` AI panel contains {_fmt_int(merged_rows)} firm-year rows, including {_fmt_int(any_pat_rows)} rows with any patents and {_fmt_int(ai_pat_rows)} rows with AI patents. The regression-ready panel retains {_fmt_int(reg_ready_rows)} firm-year rows, while the controls backbone contributes {_fmt_int(controls_rows)} firm-year observations before panel cleaning.
""".strip()


def _build_regression_snippet(regression_spec: dict[str, Any]) -> str:
    modeling = regression_spec.get("modeling", {})
    primary_models = modeling.get("primary_models", [])
    portfolio_models = modeling.get("portfolio_models", [])
    blocking = regression_spec.get("data_quality", {}).get("blocking_issues", [])
    lines = [
        "The preliminary regression lane is scaffolded around forward-looking patent outcomes and now includes a broader model portfolio rather than a single baseline table.",
        "",
    ]
    for model in primary_models[:2]:
        lines.append(
            f"- `{model.get('model_id', '')}`: {model.get('equation', '')}"
        )
    if portfolio_models:
        estimators = sorted(
            {str(model.get("estimator", "")).upper() for model in portfolio_models if model.get("estimator")}
        )
        filters = sorted(
            {str(model.get("sample_filter", "full")) for model in portfolio_models}
        )
        lines.extend(
            [
                "",
                f"The current spec registry defines {_fmt_int(len(portfolio_models))} portfolio models across estimator families {', '.join(estimators)}.",
                f"Implemented sample filters currently cover: {', '.join(filters)}.",
            ]
        )
    if blocking:
        lines.extend(
            [
                "",
                f"Current blocking data issue: {', '.join(str(item) for item in blocking)}.",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def _build_results_status_snippet(
    *,
    progress_path: str | Path,
) -> str:
    progress_file = Path(progress_path)
    if not progress_file.exists():
        return "Classification progress report has not been generated yet.\n"
    progress = _read_json(progress_file)
    if progress.get("status") in {"completed", "passed"}:
        return "The cleaned `2016–2024` classification run is complete for all requested years.\n"
    summary = progress.get("summary", {})
    current_year = summary.get("current_year")
    completed = summary.get("years_completed", [])
    years = progress.get("years", {})
    if current_year is None:
        return (
            f"The cleaned classification run is in state `{progress.get('status', '')}` "
            f"with completed years {completed}.\n"
        )
    year_state = years.get(str(current_year), {})
    return (
        f"The cleaned classification run is still in progress. "
        f"It has completed years {completed} and is currently working on `{current_year}`, "
        f"with {_fmt_int(year_state.get('rows_processed'))} of {_fmt_int(year_state.get('rows_total'))} "
        f"rows processed so far.\n"
    )


def _build_regression_results_snippet(
    *,
    regression_coefficients_path: str | Path,
    panel_reg_ready_path: str | Path,
) -> str:
    coeffs = pd.read_csv(
        regression_coefficients_path,
        usecols=["term", "coef", "p", "model", "N"],
    )
    panel = pd.read_csv(panel_reg_ready_path, usecols=["year"])
    years = sorted(panel["year"].dropna().astype(int).unique()) if "year" in panel.columns else []
    year_span = f"{years[0]}–{years[-1]}" if years else "the available years"
    focal = coeffs.loc[
        coeffs["term"].isin(
            ["log_n_A", "log_n_S", "has_actionable", "has_spec_only"]
        )
    ].copy()
    if focal.empty:
        return (
            "Baseline regressions ran, but the focal disclosure terms could not be summarized "
            "from the current coefficient export.\n"
        )

    focal["significant_5pct"] = focal["p"] < 0.05
    focal["significant_10pct"] = focal["p"] < 0.10
    lpm_dummies = focal.loc[focal["model"] == "LPM_anypat_k1_dummies"].copy()
    ols_counts = focal.loc[focal["model"] == "OLS_k1_logcounts"].copy()

    spec_row = lpm_dummies.loc[lpm_dummies["term"] == "has_spec_only"]
    act_row = lpm_dummies.loc[lpm_dummies["term"] == "has_actionable"]
    count_hits = ols_counts.loc[ols_counts["significant_10pct"]]

    if not spec_row.empty and float(spec_row.iloc[0]["p"]) < 0.10:
        headline = (
            f"In the current `{year_span}` preliminary panel pass, the continuous patent-count models remain weak, "
            "but the binary future-AI-patent specification shows a positive signal for speculative-only disclosure."
        )
    elif not count_hits.empty:
        terms = ", ".join(sorted(count_hits["term"].astype(str).unique()))
        headline = (
            f"In the current `{year_span}` preliminary panel pass, the count-style patent models show activity in "
            f"{terms}, while the binary outcome remains the key robustness check."
        )
    else:
        headline = (
            f"In the current `{year_span}` preliminary panel pass, the focal AI-disclosure coefficients remain weak across the baseline specifications."
        )

    n_by_model = (
        focal.groupby("model", dropna=False)["N"].max().sort_values().astype(int).tolist()
    )
    n_text = ", ".join(_fmt_int(value) for value in n_by_model)
    detail_lines: list[str] = []
    if not spec_row.empty:
        detail_lines.append(
            f"`has_spec_only` in the future-patent LPM is {float(spec_row.iloc[0]['coef']):.3f} with p={float(spec_row.iloc[0]['p']):.3f}."
        )
    if not act_row.empty:
        detail_lines.append(
            f"`has_actionable` in the same LPM is {float(act_row.iloc[0]['coef']):.3f} with p={float(act_row.iloc[0]['p']):.3f}."
        )
    return (
        f"{headline}\n\n"
        f"The current regression-ready sample contains {_fmt_int(len(panel))} firm-year rows after panel cleaning. "
        f"Depending on whether the specification uses contemporaneous or lead patent outcomes, the effective model "
        f"sample sizes are {n_text} observations. "
        + (" ".join(detail_lines) if detail_lines else "")
        + "\n"
    )


def _build_portfolio_results_snippet(portfolio_manifest_path: str | Path) -> str:
    path = Path(portfolio_manifest_path)
    if not path.exists():
        return "A broader regression portfolio has not been materialized yet.\n"
    manifest = _read_json(path)
    specs = manifest.get("specs", [])
    estimated = [spec for spec in specs if spec.get("status") == "estimated"]
    failed = [spec for spec in specs if spec.get("status") == "failed"]
    estimators = sorted({str(spec.get("estimator", "")).upper() for spec in estimated if spec.get("estimator")})
    samples = sorted({str(spec.get("sample_filter", "full")) for spec in estimated})
    unstable_specs = [
        spec
        for spec in estimated
        if spec.get("nan_pvalue_terms")
    ]
    if not estimated:
        return "A broader regression portfolio was configured, but none of the portfolio models finished successfully yet.\n"
    text = (
        f"The broader regression portfolio now estimates {_fmt_int(len(estimated))} feasible full-panel models "
        f"across estimator families {', '.join(estimators)}, using sample definitions {', '.join(samples)}."
    )
    coeff_path = manifest.get("portfolio_coefficients")
    if coeff_path and Path(coeff_path).exists():
        coeffs = pd.read_csv(coeff_path)

        def _extract(model: str, term: str) -> tuple[float | None, float | None]:
            match = coeffs.loc[
                (coeffs["model"] == model) & (coeffs["term"] == term),
                ["coef", "p"],
            ]
            if match.empty:
                return None, None
            row = match.iloc[0]
            return float(row["coef"]), float(row["p"]) if pd.notna(row["p"]) else None

        spec_coef, spec_p = _extract("portfolio_lpm_anypat_k1_dummies_fe", "has_spec_only")
        nonfin_coef, nonfin_p = _extract("portfolio_lpm_anypat_k1_dummies_nonfin", "has_spec_only")
        if spec_coef is not None and spec_p is not None:
            text += (
                f" The most stable pattern remains the binary future-patent outcome: "
                f"`has_spec_only` is {spec_coef:.3f} (p={spec_p:.3f}) in the full-sample LPM"
            )
            if nonfin_coef is not None and nonfin_p is not None:
                text += f" and {nonfin_coef:.3f} (p={nonfin_p:.3f}) after excluding financial firms"
            text += "."
        share_coef, share_p = _extract("portfolio_logit_anypat_k1_shares_industry_year", "SpecShare")
        if share_coef is not None:
            text += f" The share-based logit robustness is stronger, with `SpecShare` at {share_coef:.3f}"
            if share_p is None:
                text += ", but some logit variants still have unstable inference."
            else:
                text += f" (p={share_p:.3f})."
        if unstable_specs:
            unstable_ids = ", ".join(f"`{spec.get('model_id', '')}`" for spec in unstable_specs)
            text += (
                f" One caution is that {unstable_ids} still shows unstable clustered logit inference "
                "for some dummy-based focal terms, so those specifications are better treated as appendix "
                "robustness than as the headline result."
            )
    if failed:
        text += f" {_fmt_int(len(failed))} portfolio models failed and remain flagged for follow-up."
    return text + "\n"


def _build_portfolio_table(portfolio_manifest_path: str | Path) -> str:
    path = Path(portfolio_manifest_path)
    if not path.exists():
        return "_Portfolio results unavailable._\n"
    manifest = _read_json(path)
    coeff_path = manifest.get("portfolio_coefficients")
    if not coeff_path or not Path(coeff_path).exists():
        return "_Portfolio results unavailable._\n"

    coeffs = pd.read_csv(coeff_path)
    rows: list[dict[str, Any]] = []
    for spec in manifest.get("specs", []):
        if spec.get("status") != "estimated":
            continue
        model_id = str(spec.get("model_id", ""))
        focal_matches = coeffs.loc[
            (coeffs["model"] == model_id)
            & (
                coeffs["term"].isin(
                    ["log_n_A", "log_n_S", "has_actionable", "has_spec_only", "ActShare", "SpecShare"]
                )
            ),
            ["term", "coef", "p"],
        ]
        focal_bits: list[str] = []
        for row in focal_matches.itertuples(index=False):
            pvalue = None if pd.isna(row.p) else float(row.p)
            if pvalue is None:
                focal_bits.append(f"`{row.term}` = {float(row.coef):.3f} (p=NaN)")
            else:
                focal_bits.append(f"`{row.term}` = {float(row.coef):.3f} (p={pvalue:.3f})")
        rows.append(
            {
                "Spec": f"`{model_id}`",
                "Tier": str(spec.get("tier", "")).title(),
                "Estimator": str(spec.get("estimator", "")),
                "Sample": str(spec.get("sample_filter", "")),
                "Outcome": f"`{spec.get('dependent_variable', '')}`",
                "N": _fmt_int(spec.get("nobs")),
                "Focal Terms": "; ".join(focal_bits),
            }
        )
    table = pd.DataFrame(rows)
    if table.empty:
        return "_Portfolio results unavailable._\n"
    return _to_markdown_table(table)


def _build_full_panel_coverage_table(
    *,
    panel_merged_path: str | Path,
    panel_reg_ready_path: str | Path,
    controls_path: str | Path,
) -> str:
    panel_merged = pd.read_csv(panel_merged_path, usecols=["patents_total", "patents_ai"])
    panel_reg_ready = pd.read_csv(panel_reg_ready_path, usecols=["year"])
    controls = pd.read_csv(controls_path, usecols=["year"])
    years = sorted(panel_reg_ready["year"].dropna().astype(int).unique())
    table = pd.DataFrame(
        [
            {"Metric": "Merged AI base rows", "Value": _fmt_int(len(panel_merged))},
            {
                "Metric": "Rows with any patents",
                "Value": _fmt_int(int((panel_merged["patents_total"].fillna(0) > 0).sum())),
            },
            {
                "Metric": "Rows with AI patents",
                "Value": _fmt_int(int((panel_merged["patents_ai"].fillna(0) > 0).sum())),
            },
            {"Metric": "Regression-ready rows", "Value": _fmt_int(len(panel_reg_ready))},
            {"Metric": "Controls rows", "Value": _fmt_int(len(controls))},
            {
                "Metric": "Year span",
                "Value": f"{years[0]}–{years[-1]}" if years else "",
            },
        ]
    )
    return _to_markdown_table(table)


def generate_assets(args: argparse.Namespace) -> None:
    selected_manifest = _read_json(args.selected_manifest)
    heldout_eval = _read_json(args.heldout_eval)
    benchmark_matrix = _read_json(args.benchmark_matrix)
    freeze = _read_json(args.freeze_report)
    cleanup = _read_json(args.cleanup_report)
    regression_spec = _read_json(args.regression_spec)

    selected_model_id = (
        selected_manifest.get("winner", {}) or {}
    ).get("model_id", "")

    _write_text(
        Path(args.output_dir) / "snippets" / "classifier_benchmark_prelim_v1.md",
        _build_benchmark_snippet(
            selected_manifest=selected_manifest,
            heldout_eval=heldout_eval,
            freeze=freeze,
        ),
    )
    _write_text(
        Path(args.output_dir) / "snippets" / "data_construction_prelim_v1.md",
        _build_data_snippet(
            freeze=freeze,
            cleanup=cleanup,
            panel_merged_path=args.panel_merged,
            panel_reg_ready_path=args.panel_reg_ready,
            controls_path=args.controls_file,
        ),
    )
    _write_text(
        Path(args.output_dir) / "snippets" / "regression_design_prelim_v1.md",
        _build_regression_snippet(regression_spec),
    )
    _write_text(
        Path(args.output_dir) / "snippets" / "results_status_prelim_v1.md",
        _build_results_status_snippet(progress_path=args.classification_progress),
    )
    _write_text(
        Path(args.output_dir) / "snippets" / "regression_results_prelim_v1.md",
        _build_regression_results_snippet(
            regression_coefficients_path=args.regression_coefficients,
            panel_reg_ready_path=args.panel_reg_ready,
        ),
    )
    _write_text(
        Path(args.output_dir) / "snippets" / "regression_portfolio_prelim_v1.md",
        _build_portfolio_results_snippet(args.portfolio_manifest),
    )
    _write_text(
        Path(args.output_dir) / "tables" / "classifier_benchmark_prelim_v1.md",
        _build_benchmark_table(benchmark_matrix, selected_model_id),
    )
    _write_text(
        Path(args.output_dir) / "tables" / "sentence_cleanup_prelim_v1.md",
        _build_cleanup_table(cleanup),
    )
    _write_text(
        Path(args.output_dir) / "tables" / "full_panel_coverage_prelim_v1.md",
        _build_full_panel_coverage_table(
            panel_merged_path=args.panel_merged,
            panel_reg_ready_path=args.panel_reg_ready,
            controls_path=args.controls_file,
        ),
    )
    regression_table_path = Path(args.regression_table_markdown)
    if regression_table_path.exists():
        _write_text(
            Path(args.output_dir) / "tables" / "regression_baseline_prelim_v1.md",
            _read_text(regression_table_path),
        )
    _write_text(
        Path(args.output_dir) / "tables" / "regression_portfolio_prelim_v1.md",
        _build_portfolio_table(args.portfolio_manifest),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--selected-manifest",
        default="artifacts/models/prelim_selected_model_v1.json",
    )
    parser.add_argument(
        "--heldout-eval",
        default="reports/evaluation/heldout_eval_prelim_v2.json",
    )
    parser.add_argument(
        "--benchmark-matrix",
        default="reports/evaluation/model_benchmark_matrix_prelim_v1.json",
    )
    parser.add_argument(
        "--freeze-report",
        default="reports/validation/held_out_sentences_v2_freeze.json",
    )
    parser.add_argument(
        "--cleanup-report",
        default="reports/data/sentence_cleanup_v2.json",
    )
    parser.add_argument(
        "--classification-progress",
        default="reports/classification/active_window_coverage_prelim_clean_restartable_v1.json",
    )
    parser.add_argument(
        "--regression-spec",
        default="reports/analysis/regression_specification_prelim_v1.json",
    )
    parser.add_argument(
        "--regression-coefficients",
        default="results/01_baseline/tables_2016_2024_applied_v2_legalnorm_unique/baseline_coefficients.csv",
    )
    parser.add_argument(
        "--regression-table-markdown",
        default="results/01_baseline/tables_2016_2024_applied_v2_legalnorm_unique/baseline_table_clean.md",
    )
    parser.add_argument(
        "--panel-merged",
        default="data/processed/panel/panel_ai_patents_controls_2016_2024_applied_v2_legalnorm_unique.csv",
    )
    parser.add_argument(
        "--panel-reg-ready",
        default="data/processed/panel/panel_reg_ready_2016_2024_applied_v2_legalnorm_unique.csv",
    )
    parser.add_argument(
        "--controls-file",
        default="data/interim/controls/controls_by_firm_year_active_annual_allyears_2016_2024_v3.csv",
    )
    parser.add_argument(
        "--portfolio-manifest",
        default="results/01_baseline/tables_2016_2024_applied_v2_legalnorm_unique/portfolio_manifest.json",
    )
    parser.add_argument(
        "--portfolio-summary-markdown",
        default="results/01_baseline/tables_2016_2024_applied_v2_legalnorm_unique/portfolio_summary.md",
    )
    parser.add_argument("--output-dir", default="paper/generated")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate_assets(args)
    print(f"[paper-assets] wrote generated markdown under {args.output_dir}")


if __name__ == "__main__":
    main()
