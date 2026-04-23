"""Publication run driver for Test 22: analyst monitoring interaction."""

from __future__ import annotations

import argparse
import json
import math
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

from docx import Document
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from semantic_ai_washing.analysis.delivery_table_payloads import _fit_absorbed_ols, to_markdown_table
from semantic_ai_washing.analysis.publication_runs.test_03_post_filing_drift import (
    _add_note,
    _add_title,
    _build_panel_table,
    _set_document_defaults,
    _set_landscape,
)
from semantic_ai_washing.analysis.publication_runs.test_16_construct_variant_screen import _add_construct_variants

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_ANNUAL_PANEL = (
    REPO_ROOT
    / "data/processed/panel/canonical/ever_speaker_panel_2016_2025_hybrid_api_a_conf49_v1.parquet"
)
DEFAULT_ANALYST_SUMMARY = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_2/test_runs/"
    "test_21_analyst_discernment/20260423_aiw_v3_2_test_21_analyst_discernment_main_v1/"
    "ibes_annual_summary.parquet"
)
DEFAULT_TEST_ROOT = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_2/test_runs/test_22_analyst_monitoring_interaction"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated/v3_2"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_aiw_v3_2_test_22_analyst_monitoring_interaction_main_v1"
TEST_ID = "test_22_analyst_monitoring_interaction"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.test_22_analyst_monitoring_interaction"
CONTROL_SPECS = ["AI_Focus", "ln_assets", "leverage", "cash", "roa"]
OUTCOME_SPECS: list[tuple[str, str]] = [
    ("PatentMismatch_lead1", "PatentMismatch t+1"),
    ("log_patents_ai_lead1", "Log(1 + AI grants) t+1"),
    ("roa_lead2", "ROA t+2"),
]
RHS_TERMS = ["PatentMismatch", "HighAnalystCoverage", "PM_x_HighCoverage"]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annual-panel", type=Path, default=DEFAULT_ANNUAL_PANEL)
    parser.add_argument("--analyst-summary", type=Path, default=DEFAULT_ANALYST_SUMMARY)
    parser.add_argument("--test-root", type=Path, default=DEFAULT_TEST_ROOT)
    parser.add_argument("--paper-root", type=Path, default=DEFAULT_PAPER_ROOT)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    return parser.parse_args()


def _base_style() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 8,
        }
    )


def _normalize_cik(value: object) -> str:
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())
    return digits.zfill(10) if digits else ""


def _normalize_ticker(value: object) -> str:
    return str(value or "").strip().upper()


def _stars(p_value: float | None) -> str:
    if p_value is None or not math.isfinite(p_value):
        return ""
    if p_value < 0.01:
        return "***"
    if p_value < 0.05:
        return "**"
    if p_value < 0.10:
        return "*"
    return ""


def _cell(coef: float, se: float, p_value: float) -> str:
    if not (math.isfinite(coef) and math.isfinite(se)):
        return ""
    return f"{coef:.4f}{_stars(p_value)} ({se:.4f})"


def _load_panel(path: Path) -> pd.DataFrame:
    panel = pd.read_parquet(path).copy()
    panel = _add_construct_variants(panel)
    panel["cik"] = panel["cik"].map(_normalize_cik)
    panel["ticker"] = panel["ticker"].map(_normalize_ticker)
    panel["year"] = pd.to_numeric(panel["year"], errors="coerce").astype("Int64")
    if "sic2" not in panel.columns and "sic" in panel.columns:
        sic = pd.to_numeric(panel["sic"], errors="coerce")
        panel["sic2"] = (sic // 100).astype("Int64")
    for column in [*CONTROL_SPECS, "PatentMismatch", "AI_Focus", "log_patents_ai_lead1", "roa"]:
        if column in panel.columns:
            panel[column] = pd.to_numeric(panel[column], errors="coerce")
    panel = panel.loc[panel["year"].between(2016, 2024, inclusive="both")].copy()
    panel = panel.sort_values(["cik", "year"]).reset_index(drop=True)
    panel["PatentMismatch_lead1"] = panel.groupby("cik", sort=False)["PatentMismatch"].shift(-1)
    panel["roa_lead2"] = panel.groupby("cik", sort=False)["roa"].shift(-2)
    return panel


def _load_current_coverage(path: Path) -> pd.DataFrame:
    analyst = pd.read_parquet(path).copy()
    analyst["ticker"] = analyst["ticker"].map(_normalize_ticker)
    analyst["year"] = pd.to_numeric(analyst["ibes_snapshot_year"], errors="coerce").astype("Int64")
    analyst["log_analyst_coverage_t"] = pd.to_numeric(
        analyst["log_analyst_coverage_lead1"], errors="coerce"
    )
    keep = ["ticker", "year", "log_analyst_coverage_t", "numest", "statpers"]
    analyst = analyst[keep].sort_values(["ticker", "year", "statpers"]).drop_duplicates(
        ["ticker", "year"], keep="last"
    )
    return analyst


def _prepare_sample(panel: pd.DataFrame, coverage: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    use = panel.merge(coverage, on=["ticker", "year"], how="left", validate="many_to_one")
    use = use.loc[use["any_ai_talk"].fillna(0).astype(int).eq(1)].copy()
    use["log_analyst_coverage_t"] = pd.to_numeric(use["log_analyst_coverage_t"], errors="coerce")
    med = use.groupby("year")["log_analyst_coverage_t"].transform("median")
    use["HighAnalystCoverage"] = np.where(
        use["log_analyst_coverage_t"].notna() & med.notna(),
        (use["log_analyst_coverage_t"] >= med).astype(int),
        np.nan,
    )
    use["PM_x_HighCoverage"] = use["PatentMismatch"] * use["HighAnalystCoverage"]
    summary = {
        "ai_talking_rows": int(len(use)),
        "unique_firms": int(use["cik"].nunique()),
        "coverage_nonmissing": int(use["log_analyst_coverage_t"].notna().sum()),
        "high_coverage_nonmissing": int(use["HighAnalystCoverage"].notna().sum()),
        "high_coverage_share": float(use["HighAnalystCoverage"].dropna().mean()) if use["HighAnalystCoverage"].notna().any() else math.nan,
        "years": [int(use["year"].min()), int(use["year"].max())],
    }
    return use, summary


def _fit_models(sample: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for outcome, outcome_label in OUTCOME_SPECS:
        needed = [outcome, *RHS_TERMS, "sic2", "year", *CONTROL_SPECS]
        use = sample.dropna(subset=needed).copy()
        if use.empty:
            rows.append(
                {
                    "outcome": outcome,
                    "outcome_label": outcome_label,
                    "nobs": 0,
                    "outcome_mean": math.nan,
                    "params": {},
                    "bse": {},
                    "pvalues": {},
                }
            )
            continue
        result, est_sample, _adj_r2 = _fit_absorbed_ols(
            use,
            dependent=outcome,
            rhs_terms=RHS_TERMS,
            absorb_col="cik",
            include_year=True,
            controls=CONTROL_SPECS,
        )
        rows.append(
            {
                "outcome": outcome,
                "outcome_label": outcome_label,
                "nobs": int(result.nobs),
                "outcome_mean": float(est_sample[outcome].mean()),
                "params": result.params.to_dict(),
                "bse": result.bse.to_dict(),
                "pvalues": result.pvalues.to_dict(),
            }
        )
    return rows


def _build_table(results: list[dict[str, object]]) -> tuple[pd.DataFrame, dict[str, dict[str, object]]]:
    keyed = {row["outcome"]: row for row in results}
    rows: list[dict[str, object]] = []
    for outcome, outcome_label in OUTCOME_SPECS:
        res = keyed[outcome]
        rows.append(
            {
                "row_label": outcome_label,
                "PatentMismatch": _cell(
                    res["params"].get("PatentMismatch", math.nan),
                    res["bse"].get("PatentMismatch", math.nan),
                    res["pvalues"].get("PatentMismatch", math.nan),
                ),
                "High coverage": _cell(
                    res["params"].get("HighAnalystCoverage", math.nan),
                    res["bse"].get("HighAnalystCoverage", math.nan),
                    res["pvalues"].get("HighAnalystCoverage", math.nan),
                ),
                "Mismatch x High coverage": _cell(
                    res["params"].get("PM_x_HighCoverage", math.nan),
                    res["bse"].get("PM_x_HighCoverage", math.nan),
                    res["pvalues"].get("PM_x_HighCoverage", math.nan),
                ),
                "Outcome mean": f"{res['outcome_mean']:.4f}" if math.isfinite(res['outcome_mean']) else "",
                "Observations": res["nobs"],
            }
        )
    return pd.DataFrame(rows), keyed


def _build_markdown(table_df: pd.DataFrame) -> str:
    headers = table_df.columns.tolist()
    rows = [[str(value) for value in row] for row in table_df.values.tolist()]
    return to_markdown_table(headers, rows)


def _render_latex(table_df: pd.DataFrame) -> str:
    lines = [
        "\\begin{table}[!htbp]",
        "\\centering",
        "\\caption{Analyst monitoring and the later consequences of low-credibility AI disclosure}",
        "\\small",
        "\\begin{tabular}{lccccc}",
        "\\hline",
        "Outcome & PatentMismatch & High coverage & Mismatch x High coverage & Outcome mean & Observations " + "\\\\",
        "\\hline",
    ]
    for _, row in table_df.iterrows():
        lines.append(
            " & ".join(
                [
                    str(row["row_label"]).replace("_", "\\_"),
                    str(row["PatentMismatch"]),
                    str(row["High coverage"]),
                    str(row["Mismatch x High coverage"]),
                    str(row["Outcome mean"]),
                    str(row["Observations"]),
                ]
            )
            + " "
            + "\\\\"
        )
    lines.extend(
        [
            "\\hline",
            "\\end{tabular}",
            "\\begin{flushleft}",
            "\\footnotesize Notes: `High coverage` is an indicator for being at or above the within-year median of same-year log analyst coverage from IBES annual EPS summary snapshots. The interaction asks whether stronger analyst monitoring attenuates mismatch persistence or the later weak outcomes linked to low-credibility AI disclosure. All specifications use the AI-talking annual sample, firm fixed effects, year fixed effects, current controls, and firm-clustered standard errors.",
            "\\end{flushleft}",
            "\\end{table}",
        ]
    )
    return "\n".join(lines)


def _write_docx(table_df: pd.DataFrame, path: Path) -> None:
    document = Document()
    _set_document_defaults(document)
    _set_landscape(document)
    _add_title(document, "Test 22. Analyst monitoring interaction")
    document.add_paragraph(
        "This table asks whether stronger same-year analyst coverage attenuates the later consequences of low-credibility AI disclosure. "
        "Coverage is measured from the annual IBES EPS summary snapshot in the same calendar year as the disclosure, and the outcomes are future mismatch persistence, future AI patent realization, and later profitability."
    )
    headers = list(table_df.columns)
    rows = [[(str(value), False) for value in row] for row in table_df.values.tolist()]
    _build_panel_table(document, headers, rows)
    _add_note(
        document,
        "`High coverage` is a within-year median indicator. A positive interaction on grants or ROA, or a negative interaction on future mismatch persistence, would support a monitoring interpretation."
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    document.save(path)


def _plot_groups(sample: pd.DataFrame, path: Path) -> None:
    _base_style()
    plot = sample.dropna(subset=["HighAnalystCoverage", "PatentMismatch", "log_patents_ai_lead1", "roa_lead2"]).copy()
    plot["group"] = np.select(
        [
            plot["PatentMismatch"].eq(1) & plot["HighAnalystCoverage"].eq(1),
            plot["PatentMismatch"].eq(1) & plot["HighAnalystCoverage"].eq(0),
            plot["PatentMismatch"].eq(0) & plot["HighAnalystCoverage"].eq(1),
        ],
        [
            "Mismatch + High coverage",
            "Mismatch + Low coverage",
            "Non-mismatch + High coverage",
        ],
        default="Non-mismatch + Low coverage",
    )
    summary = (
        plot.groupby("group", as_index=False)
        .agg(grants_t1=("log_patents_ai_lead1", "mean"), roa_t2=("roa_lead2", "mean"))
    )
    order = [
        "Mismatch + Low coverage",
        "Mismatch + High coverage",
        "Non-mismatch + Low coverage",
        "Non-mismatch + High coverage",
    ]
    summary["group"] = pd.Categorical(summary["group"], categories=order, ordered=True)
    summary = summary.sort_values("group")
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4))
    colors = ["#8c510a", "#d8b365", "#5ab4ac", "#01665e"]
    axes[0].bar(summary["group"].astype(str), summary["grants_t1"], color=colors)
    axes[0].set_title("Future AI grants t+1")
    axes[0].tick_params(axis="x", rotation=25)
    axes[1].bar(summary["group"].astype(str), summary["roa_t2"], color=colors)
    axes[1].set_title("ROA t+2")
    axes[1].tick_params(axis="x", rotation=25)
    fig.suptitle("Later outcomes by mismatch and analyst coverage", y=0.98)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    fig.savefig(path.with_suffix('.pdf'), bbox_inches='tight')
    plt.close(fig)


def _write_writer_packet(output_path: Path, sample_summary: dict[str, object], keyed: dict[str, dict[str, object]]) -> None:
    pm = keyed["PatentMismatch_lead1"]
    grants = keyed["log_patents_ai_lead1"]
    roa = keyed["roa_lead2"]
    lines = [
        "# Writer Packet: Test 22 analyst monitoring interaction",
        "",
        "## Setup",
        "",
        "- Sample: AI-talking annual panel with same-year analyst coverage from IBES annual EPS summaries.",
        "- Monitoring variable: `HighAnalystCoverage`, defined as at-or-above the within-year median of log analyst coverage.",
        f"- Coverage non-missing rows: `{sample_summary['coverage_nonmissing']}`.",
        f"- High-coverage share among non-missing rows: `{sample_summary['high_coverage_share']:.3f}`.",
        "",
        "## Headline read",
        "",
        f"- Future mismatch persistence interaction: `{pm['params'].get('PM_x_HighCoverage', math.nan):.4f}` (p=`{pm['pvalues'].get('PM_x_HighCoverage', math.nan):.3f}`).",
        f"- Future AI grants interaction: `{grants['params'].get('PM_x_HighCoverage', math.nan):.4f}` (p=`{grants['pvalues'].get('PM_x_HighCoverage', math.nan):.3f}`).",
        f"- ROA t+2 interaction: `{roa['params'].get('PM_x_HighCoverage', math.nan):.4f}` (p=`{roa['pvalues'].get('PM_x_HighCoverage', math.nan):.3f}`).",
        "",
        "## Interpretation discipline",
        "",
        "- A positive interaction on grants or ROA means coverage softens the negative later consequence of mismatch.",
        "- A negative interaction on future mismatch persistence means coverage helps prevent the behavior from persisting.",
        "- If the interaction is weak while the coverage level itself is strong, that is more consistent with selection or attention differences than with active monitoring.",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_result_notes(output_path: Path, sample_summary: dict[str, object], keyed: dict[str, dict[str, object]]) -> None:
    lines = [
        "- Test 22 asks whether same-year analyst coverage attenuates mismatch persistence or later weak outcomes.",
        f"- Coverage non-missing rows: `{sample_summary['coverage_nonmissing']}`.",
        f"- High-coverage share: `{sample_summary['high_coverage_share']:.3f}`.",
        f"- Interaction on PatentMismatch t+1: `{keyed['PatentMismatch_lead1']['params'].get('PM_x_HighCoverage', math.nan):.4f}` (p=`{keyed['PatentMismatch_lead1']['pvalues'].get('PM_x_HighCoverage', math.nan):.3f}`).",
        f"- Interaction on AI grants t+1: `{keyed['log_patents_ai_lead1']['params'].get('PM_x_HighCoverage', math.nan):.4f}` (p=`{keyed['log_patents_ai_lead1']['pvalues'].get('PM_x_HighCoverage', math.nan):.3f}`).",
        f"- Interaction on ROA t+2: `{keyed['roa_lead2']['params'].get('PM_x_HighCoverage', math.nan):.4f}` (p=`{keyed['roa_lead2']['pvalues'].get('PM_x_HighCoverage', math.nan):.3f}`).",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = _parse_args()
    run_dir = args.test_root / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    panel = _load_panel(args.annual_panel)
    coverage = _load_current_coverage(args.analyst_summary)
    sample, sample_summary = _prepare_sample(panel, coverage)
    results = _fit_models(sample)
    table_df, keyed = _build_table(results)

    base_name = f"{TEST_ID}_{args.run_id}"
    local_csv = run_dir / f"{base_name}.csv"
    table_df.to_csv(local_csv, index=False)
    local_sample = run_dir / "monitoring_sample.parquet"
    sample.to_parquet(local_sample, index=False)
    local_md = run_dir / f"{base_name}.md"
    local_md.write_text(_build_markdown(table_df), encoding="utf-8")
    local_tex = run_dir / f"{base_name}.tex"
    local_tex.write_text(_render_latex(table_df), encoding="utf-8")
    local_docx = run_dir / f"{base_name}.docx"
    _write_docx(table_df, local_docx)
    local_png = run_dir / f"{base_name}.png"
    _plot_groups(sample, local_png)
    local_writer = run_dir / f"{base_name}_writer_packet.md"
    _write_writer_packet(local_writer, sample_summary, keyed)
    local_notes = run_dir / f"{base_name}_result_notes.md"
    _write_result_notes(local_notes, sample_summary, keyed)

    paper_dirs = {
        "docx": args.paper_root / "docx",
        "latex": args.paper_root / "latex",
        "tables": args.paper_root / "tables",
        "figures": args.paper_root / "figures",
        "writer_packets": args.paper_root / "writer_packets",
        "snippets": args.paper_root / "snippets",
    }
    for dest in paper_dirs.values():
        dest.mkdir(parents=True, exist_ok=True)
    paper_docx = paper_dirs["docx"] / f"{base_name}.docx"
    paper_tex = paper_dirs["latex"] / f"{base_name}.tex"
    paper_csv = paper_dirs["tables"] / f"{base_name}.csv"
    paper_png = paper_dirs["figures"] / f"{base_name}.png"
    paper_pdf = paper_dirs["figures"] / f"{base_name}.pdf"
    paper_writer = paper_dirs["writer_packets"] / f"{base_name}.md"
    paper_notes = paper_dirs["snippets"] / f"{base_name}_result_notes.md"
    shutil.copy2(local_docx, paper_docx)
    shutil.copy2(local_tex, paper_tex)
    shutil.copy2(local_csv, paper_csv)
    shutil.copy2(local_png, paper_png)
    shutil.copy2(local_png.with_suffix('.pdf'), paper_pdf)
    shutil.copy2(local_writer, paper_writer)
    shutil.copy2(local_notes, paper_notes)

    manifest = {
        "test_id": TEST_ID,
        "module_path": MODULE_PATH,
        "run_id": args.run_id,
        "run_timestamp_utc": datetime.now(UTC).isoformat(),
        "inputs": {
            "annual_panel": str(args.annual_panel),
            "analyst_summary": str(args.analyst_summary),
        },
        "sample_summary": sample_summary,
        "paper_outputs": {
            "table_docx": str(paper_docx),
            "table_tex": str(paper_tex),
            "table_csv": str(paper_csv),
            "figure_png": str(paper_png),
            "figure_pdf": str(paper_pdf),
            "writer_packet": str(paper_writer),
            "result_notes": str(paper_notes),
        },
        "local_outputs": {
            "monitoring_sample": str(local_sample),
            "table_docx": str(local_docx),
            "table_tex": str(local_tex),
            "table_csv": str(local_csv),
            "figure_png": str(local_png),
            "writer_packet": str(local_writer),
            "result_notes": str(local_notes),
        },
        "results": results,
    }
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
