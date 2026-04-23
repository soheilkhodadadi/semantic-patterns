"""Publication run driver for Test 17: real-outcome dynamics in the AI-talking sample."""

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

from semantic_ai_washing.analysis.delivery_table_payloads import _fit_absorbed_ols
from semantic_ai_washing.analysis.publication_runs.test_03_post_filing_drift import (
    _add_note,
    _add_title,
    _build_panel_table,
    _set_document_defaults,
    _set_landscape,
)
from semantic_ai_washing.analysis.publication_runs.test_16_construct_variant_screen import (
    _add_construct_variants,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_ANNUAL_PANEL = (
    REPO_ROOT
    / "data/processed/panel/canonical/ever_speaker_panel_2016_2025_hybrid_api_a_conf49_v1.parquet"
)
DEFAULT_TEST_ROOT = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_1/test_runs/test_17_real_outcome_dynamics"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated/v3_1"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_aiw_v3_1_test_17_real_outcome_dynamics_main_v1"
TEST_ID = "test_17_real_outcome_dynamics"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.test_17_real_outcome_dynamics"
VARIANT_SPECS: list[tuple[str, str]] = [
    ("PatentMismatch", "Canonical grant mismatch"),
    ("ApplicationMismatch", "Application mismatch"),
    ("LowCredibility", "Low credibility only"),
]
OUTCOME_SPECS: list[tuple[str, str, list[str]]] = [
    ("roa", "ROA", ["AI_Focus", "ln_assets", "leverage", "cash"]),
    ("sales_growth", "Sales growth", ["AI_Focus", "ln_assets", "leverage", "cash", "roa"]),
    ("capx_at", "CAPX/assets", ["AI_Focus", "ln_assets", "leverage", "cash", "roa"]),
    ("rd_intensity", "R&D/assets", ["AI_Focus", "ln_assets", "leverage", "cash", "roa"]),
]
HORIZONS = [(1, "t+1"), (2, "t+2")]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annual-panel", type=Path, default=DEFAULT_ANNUAL_PANEL)
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
        }
    )


def _winsorize(series: pd.Series, lower_q: float = 0.01, upper_q: float = 0.99) -> pd.Series:
    valid = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan)
    if valid.notna().sum() == 0:
        return valid
    lower = valid.quantile(lower_q)
    upper = valid.quantile(upper_q)
    return valid.clip(lower=lower, upper=upper)


def _prepare_sample(panel: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    use = _add_construct_variants(panel).copy()
    use = use.sort_values(["cik", "year"]).reset_index(drop=True)
    for outcome, _label, _controls in OUTCOME_SPECS:
        use[outcome] = pd.to_numeric(use[outcome], errors="coerce").replace(
            [np.inf, -np.inf], np.nan
        )
        for horizon, _horizon_label in HORIZONS:
            lead = use.groupby("cik", sort=False)[outcome].shift(-horizon)
            use[f"{outcome}_lead{horizon}"] = _winsorize(lead)
    use = use.loc[use["any_ai_talk"].fillna(0).astype(int).eq(1)].copy()
    use = use.loc[use["cik"].astype(str).str.len().gt(0) & use["year"].notna()].copy()
    summary = {
        "ai_talking_rows": int(len(use)),
        "unique_firms": int(use["cik"].nunique()),
        "year_min": int(pd.to_numeric(use["year"], errors="coerce").min()),
        "year_max": int(pd.to_numeric(use["year"], errors="coerce").max()),
        "variant_shares": {
            column: float(pd.to_numeric(use[column], errors="coerce").fillna(0).mean())
            for column, _label in VARIANT_SPECS
        },
    }
    return use, summary


def _fit_model(
    sample: pd.DataFrame, variant: str, outcome: str, horizon: int, controls: list[str]
) -> dict[str, object]:
    dependent = f"{outcome}_lead{horizon}"
    result, use, adj_r2 = _fit_absorbed_ols(
        sample,
        dependent=dependent,
        rhs_terms=[variant],
        absorb_col="cik",
        include_year=True,
        controls=controls,
    )
    return {
        "variant": variant,
        "outcome": outcome,
        "horizon": horizon,
        "dependent": dependent,
        "nobs": int(result.nobs),
        "adj_r2": float(adj_r2) if adj_r2 is not None else math.nan,
        "params": result.params.to_dict(),
        "bse": result.bse.to_dict(),
        "pvalues": result.pvalues.to_dict(),
        "outcome_mean": float(use[dependent].mean()),
    }


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


def _coef_cell(coef: float | None, se: float | None, p_value: float | None) -> str:
    if coef is None or se is None or not math.isfinite(coef) or not math.isfinite(se):
        return ""
    return f"{coef:.4f}{_stars(p_value)} ({se:.4f})"


def _build_results_table(
    model_rows: list[dict[str, object]],
) -> tuple[pd.DataFrame, dict[tuple[str, int, str], dict[str, object]]]:
    keyed = {(row["outcome"], row["horizon"], row["variant"]): row for row in model_rows}
    rows: list[dict[str, object]] = []
    for outcome, outcome_label, _controls in OUTCOME_SPECS:
        for horizon, horizon_label in HORIZONS:
            row_label = f"{outcome_label} {horizon_label}"
            row = {"row_label": row_label}
            for variant, variant_label in VARIANT_SPECS:
                result = keyed[(outcome, horizon, variant)]
                row[variant_label] = _coef_cell(
                    result["params"].get(variant),
                    result["bse"].get(variant),
                    result["pvalues"].get(variant),
                )
            base_result = keyed[(outcome, horizon, VARIANT_SPECS[0][0])]
            row["Outcome mean"] = f"{base_result['outcome_mean']:.3f}"
            row["Observations"] = str(base_result["nobs"])
            rows.append(row)
    return pd.DataFrame(rows), keyed


def _render_table_outputs(table_df: pd.DataFrame) -> tuple[str, str]:
    headers = (
        ["Outcome"]
        + [label for _variant, label in VARIANT_SPECS]
        + ["Outcome mean", "Observations"]
    )
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in table_df.iterrows():
        cells = [str(row["row_label"])] + [str(row[h]) for h in headers[1:]]
        lines.append("| " + " | ".join(cells) + " |")
    md = "\n".join(["# Table Main", "", *lines, ""])

    latex_lines = [
        "\\begin{table}[!htbp]",
        "\\centering",
        "\\caption{Real-outcome dynamics in the AI-talking sample}",
        "\\begin{tabular}{l" + "c" * (len(headers) - 1) + "}",
        "\\hline",
        "Outcome & Canonical grant mismatch & Application mismatch & Low credibility only & Outcome mean & Observations \\\\",
        "\\hline",
    ]
    for _, row in table_df.iterrows():
        latex_lines.append(
            " & ".join([str(row["row_label"])] + [str(row[h]) for h in headers[1:]]) + " \\\\"
        )
    latex_lines.extend(["\\hline", "\\end{tabular}", "\\end{table}"])
    return md, "\n".join(latex_lines) + "\n"


def _build_table_docx(table_df: pd.DataFrame, output_path: Path) -> None:
    document = Document()
    _set_document_defaults(document)
    _set_landscape(document)
    _add_title(document, "Table 17. Real-Outcome Dynamics in the AI-Talking Sample")
    _add_note(
        document,
        "This table revisits non-market consequences inside the AI-talking sample. Each row is a future operating or investment outcome measured at t+1 or t+2. The columns compare the canonical grant-based PatentMismatch construct, the application-based mismatch variant, and the disclosure-side LowCredibility variant. All specifications absorb firm and year fixed effects, use outcome-appropriate core controls, cluster standard errors by firm, and winsorize each future outcome at the 1st and 99th percentiles.",
    )
    headers = (
        [""] + [label for _variant, label in VARIANT_SPECS] + ["Outcome mean", "Observations"]
    )
    rows: list[list[tuple[str, bool]]] = []
    for _, row in table_df.iterrows():
        rows.append([(str(row["row_label"]), True)] + [(str(row[h]), False) for h in headers[1:]])
    _build_panel_table(document, headers, rows)
    document.save(output_path)


def _plot_heatmap(
    model_rows: list[dict[str, object]], output_stem: Path
) -> tuple[Path, Path, pd.DataFrame]:
    _base_style()
    records = []
    row_order: list[str] = []
    for outcome, outcome_label, _controls in OUTCOME_SPECS:
        for horizon, horizon_label in HORIZONS:
            row_name = f"{outcome_label} {horizon_label}"
            row_order.append(row_name)
            for variant, variant_label in VARIANT_SPECS:
                result = next(
                    r
                    for r in model_rows
                    if r["outcome"] == outcome
                    and r["horizon"] == horizon
                    and r["variant"] == variant
                )
                records.append(
                    {
                        "row_name": row_name,
                        "variant": variant_label,
                        "coef": float(result["params"].get(variant, math.nan)),
                        "p_value": float(result["pvalues"].get(variant, math.nan)),
                    }
                )
    figure_df = pd.DataFrame(records)
    variant_order = [label for _variant, label in VARIANT_SPECS]
    pivot = figure_df.pivot(index="row_name", columns="variant", values="coef").reindex(
        index=row_order, columns=variant_order
    )
    ann = (
        figure_df.assign(
            label=lambda x: x.apply(lambda r: f"{r['coef']:.3f}{_stars(r['p_value'])}", axis=1)
        )
        .pivot(index="row_name", columns="variant", values="label")
        .reindex(index=row_order, columns=variant_order)
    )
    vmax = float(np.nanmax(np.abs(pivot.to_numpy(dtype=float)))) if not pivot.empty else 0.1
    vmax = max(vmax, 0.05)
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    im = ax.imshow(
        pivot.to_numpy(dtype=float), cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto"
    )
    ax.set_xticks(range(len(pivot.columns)), list(pivot.columns), rotation=12, ha="right")
    ax.set_yticks(range(len(pivot.index)), list(pivot.index))
    ax.set_title("Real-Outcome Dynamics: AI-Talking Sample")
    for i, row_name in enumerate(pivot.index):
        for j, col_name in enumerate(pivot.columns):
            ax.text(j, i, ann.loc[row_name, col_name], ha="center", va="center", fontsize=8)
    cbar = fig.colorbar(im, ax=ax, shrink=0.9)
    cbar.set_label("Coefficient")
    fig.tight_layout()
    png_path = output_stem.with_suffix(".png")
    pdf_path = output_stem.with_suffix(".pdf")
    fig.savefig(png_path, dpi=240)
    fig.savefig(pdf_path)
    plt.close(fig)
    return png_path, pdf_path, figure_df


def _result_notes(model_rows: list[dict[str, object]], sample_summary: dict[str, object]) -> str:
    keyed = {(row["outcome"], row["horizon"], row["variant"]): row for row in model_rows}
    roa_t2 = keyed[("roa", 2, "PatentMismatch")]
    rd_t2 = keyed[("rd_intensity", 2, "PatentMismatch")]
    lowcred_roa_t2 = keyed[("roa", 2, "LowCredibility")]
    return "\n".join(
        [
            f"# Result Notes: {TEST_ID}",
            "",
            f"- Sample: `{sample_summary['ai_talking_rows']}` AI-talking firm-years across `{sample_summary['unique_firms']}` firms.",
            f"- Canonical PatentMismatch on ROA t+2: `{roa_t2['params'].get('PatentMismatch', math.nan):.4f}` (p=`{roa_t2['pvalues'].get('PatentMismatch', math.nan):.3f}`).",
            f"- Canonical PatentMismatch on R&D/assets t+2: `{rd_t2['params'].get('PatentMismatch', math.nan):.4f}` (p=`{rd_t2['pvalues'].get('PatentMismatch', math.nan):.3f}`).",
            f"- LowCredibility on ROA t+2: `{lowcred_roa_t2['params'].get('LowCredibility', math.nan):.4f}` (p=`{lowcred_roa_t2['pvalues'].get('LowCredibility', math.nan):.3f}`).",
            "- Read this table as a consequences screen, not as a fully settled mechanism claim. The key question is whether the strongest signals line up into a coherent profitability-versus-investment pattern rather than a collection of unrelated coefficients.",
            "",
        ]
    )


def _writer_packet(
    args: argparse.Namespace,
    model_rows: list[dict[str, object]],
    sample_summary: dict[str, object],
) -> str:
    keyed = {(row["outcome"], row["horizon"], row["variant"]): row for row in model_rows}
    return "\n".join(
        [
            f"# Writer Packet: {TEST_ID}",
            "",
            "## Role In The Paper",
            "- This run asks whether the AI-talking sample reveals stronger non-market consequences than the older full-panel real-effects table.",
            "- The comparison keeps the canonical construct in the lead, but checks whether an application-side mismatch or a disclosure-only low-credibility flag tells a cleaner operating story.",
            "",
            "## Sample Definition",
            f"- Annual panel: `{args.annual_panel}`",
            "- Working sample: `AI-talking firm-years only`",
            f"- Rows: `{sample_summary['ai_talking_rows']}`",
            f"- Firms: `{sample_summary['unique_firms']}`",
            "- Fixed effects: `firm + year`",
            "- Winsorization: `1st / 99th percentile on each future outcome`",
            "",
            "## Headline Read",
            f"- Canonical PatentMismatch on ROA t+2: `{keyed[('roa', 2, 'PatentMismatch')]['params'].get('PatentMismatch', math.nan):.4f}` (p=`{keyed[('roa', 2, 'PatentMismatch')]['pvalues'].get('PatentMismatch', math.nan):.3f}`)",
            f"- Canonical PatentMismatch on R&D/assets t+2: `{keyed[('rd_intensity', 2, 'PatentMismatch')]['params'].get('PatentMismatch', math.nan):.4f}` (p=`{keyed[('rd_intensity', 2, 'PatentMismatch')]['pvalues'].get('PatentMismatch', math.nan):.3f}`)",
            f"- LowCredibility on ROA t+2: `{keyed[('roa', 2, 'LowCredibility')]['params'].get('LowCredibility', math.nan):.4f}` (p=`{keyed[('roa', 2, 'LowCredibility')]['pvalues'].get('LowCredibility', math.nan):.3f}`)",
            "",
            "## Caption Draft",
            "This table revisits non-market consequences inside the AI-talking sample. Each row is a future operating or investment outcome measured at t+1 or t+2. The columns compare the canonical grant-based PatentMismatch construct, the application-based mismatch variant, and the disclosure-side LowCredibility variant. All specifications absorb firm and year fixed effects, include outcome-appropriate core controls, cluster standard errors by firm, and winsorize each future outcome at the 1st and 99th percentiles.",
            "",
        ]
    )


def _dataset_summary(
    args: argparse.Namespace,
    sample_summary: dict[str, object],
    model_rows: list[dict[str, object]],
    figure_df: pd.DataFrame,
) -> dict[str, object]:
    return {
        "test_id": TEST_ID,
        "run_id": args.run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "inputs": {"annual_panel": str(args.annual_panel)},
        "sample_summary": sample_summary,
        "model_rows": model_rows,
        "figure_series": figure_df.to_dict(orient="records"),
    }


def _copy_exports(run_dir: Path, paper_root: Path, run_id: str) -> dict[str, str]:
    exports = {
        "table_csv": paper_root / "tables" / f"{TEST_ID}_{run_id}.csv",
        "table_md": paper_root / "tables" / f"{TEST_ID}_{run_id}.md",
        "table_tex": paper_root / "latex" / f"{TEST_ID}_{run_id}.tex",
        "table_docx": paper_root / "docx" / f"{TEST_ID}_{run_id}.docx",
        "figure_png": paper_root / "figures" / f"{TEST_ID}_{run_id}.png",
        "figure_pdf": paper_root / "figures" / f"{TEST_ID}_{run_id}.pdf",
        "figure_series": paper_root / "tables" / f"{TEST_ID}_{run_id}_figure_series.csv",
        "writer_packet": paper_root / "writer_packets" / f"{TEST_ID}_{run_id}.md",
        "result_notes": paper_root / "snippets" / f"{TEST_ID}_{run_id}_result_notes.md",
    }
    for path in exports.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    mapping = {
        run_dir / "table_main.csv": exports["table_csv"],
        run_dir / "table_main.md": exports["table_md"],
        run_dir / "table_main.tex": exports["table_tex"],
        run_dir / "table_main.docx": exports["table_docx"],
        run_dir / "figure_main.png": exports["figure_png"],
        run_dir / "figure_main.pdf": exports["figure_pdf"],
        run_dir / "figure_series.csv": exports["figure_series"],
        run_dir / "writer_packet.md": exports["writer_packet"],
        run_dir / "result_notes.md": exports["result_notes"],
    }
    for src, dst in mapping.items():
        shutil.copy2(src, dst)
    return {key: str(path) for key, path in exports.items()}


def main() -> None:
    args = _parse_args()
    run_dir = args.test_root / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    panel = pd.read_parquet(args.annual_panel)
    sample, sample_summary = _prepare_sample(panel)

    model_rows: list[dict[str, object]] = []
    for outcome, _label, controls in OUTCOME_SPECS:
        for horizon, _horizon_label in HORIZONS:
            for variant, _variant_label in VARIANT_SPECS:
                model_rows.append(_fit_model(sample, variant, outcome, horizon, controls))

    table_df, _keyed = _build_results_table(model_rows)
    table_df.to_csv(run_dir / "table_main.csv", index=False)
    table_md, table_tex = _render_table_outputs(table_df)
    (run_dir / "table_main.md").write_text(table_md, encoding="utf-8")
    (run_dir / "table_main.tex").write_text(table_tex, encoding="utf-8")
    _build_table_docx(table_df, run_dir / "table_main.docx")

    png_path, pdf_path, figure_df = _plot_heatmap(model_rows, run_dir / "figure_main")
    figure_df.to_csv(run_dir / "figure_series.csv", index=False)

    (run_dir / "result_notes.md").write_text(
        _result_notes(model_rows, sample_summary), encoding="utf-8"
    )
    (run_dir / "writer_packet.md").write_text(
        _writer_packet(args, model_rows, sample_summary), encoding="utf-8"
    )
    dataset_summary = _dataset_summary(args, sample_summary, model_rows, figure_df)
    (run_dir / "dataset_summary.json").write_text(
        json.dumps(dataset_summary, indent=2), encoding="utf-8"
    )

    paper_exports = _copy_exports(run_dir, args.paper_root, args.run_id)
    manifest = {
        "test_id": TEST_ID,
        "run_id": args.run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "module_path": MODULE_PATH,
        "run_dir": str(run_dir),
        "inputs": {"annual_panel": str(args.annual_panel)},
        "outputs": {
            "dataset_summary": str(run_dir / "dataset_summary.json"),
            "table_csv": str(run_dir / "table_main.csv"),
            "table_md": str(run_dir / "table_main.md"),
            "table_tex": str(run_dir / "table_main.tex"),
            "table_docx": str(run_dir / "table_main.docx"),
            "figure_png": str(png_path),
            "figure_pdf": str(pdf_path),
            "figure_series": str(run_dir / "figure_series.csv"),
            "writer_packet": str(run_dir / "writer_packet.md"),
            "result_notes": str(run_dir / "result_notes.md"),
        },
        "paper_exports": paper_exports,
        "sample_summary": sample_summary,
    }
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"[{TEST_ID}] wrote run bundle to {run_dir}")
    print(f"[{TEST_ID}] paper table: {paper_exports['table_docx']}")


if __name__ == "__main__":
    main()
