"""Publication run driver for Test 21: analyst discernment around low-credibility AI disclosure."""

from __future__ import annotations

import argparse
import json
import math
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

from docx import Document
from dotenv import dotenv_values
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import psycopg2

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
DEFAULT_TEST_ROOT = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_2/test_runs/test_21_analyst_discernment"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated/v3_2"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_aiw_v3_2_test_21_analyst_discernment_main_v1"
TEST_ID = "test_21_analyst_discernment"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.test_21_analyst_discernment"

VARIANT_SPECS: list[tuple[str, str]] = [
    ("PatentMismatch", "PatentMismatch"),
    ("LowCredibility", "LowCredibility"),
    ("A_S", "A/S ratio"),
]
OUTCOME_SPECS: list[tuple[str, str]] = [
    ("log_analyst_coverage_lead1", "Log(1 + analyst coverage) t+1"),
    ("analyst_dispersion_scaled_lead1", "Scaled forecast dispersion t+1"),
    ("analyst_revision_balance_lead1", "Net revision balance t+1"),
]
CONTROL_SPECS = ["AI_Focus", "ln_assets", "cash", "leverage", "roa"]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annual-panel", type=Path, default=DEFAULT_ANNUAL_PANEL)
    parser.add_argument("--test-root", type=Path, default=DEFAULT_TEST_ROOT)
    parser.add_argument("--paper-root", type=Path, default=DEFAULT_PAPER_ROOT)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--dotenv-path", type=Path, default=REPO_ROOT / ".env")
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


def _wrds_connection(dotenv_path: Path) -> psycopg2.extensions.connection:
    values = dotenv_values(dotenv_path)
    return psycopg2.connect(
        dbname="wrds",
        user=values["WRDS_USER"],
        password=values["WRDS_PASS"],
        host=values["WRDS_DB_HOST"],
        port=int(values["WRDS_DB_PORT"]),
        connect_timeout=15,
    )


def _load_panel(path: Path) -> pd.DataFrame:
    panel = pd.read_parquet(path).copy()
    panel = _add_construct_variants(panel)
    if "sic2" not in panel.columns and "sic" in panel.columns:
        sic = pd.to_numeric(panel["sic"], errors="coerce")
        panel["sic2"] = (sic // 100).astype("Int64")
    panel["cik"] = panel["cik"].map(_normalize_cik)
    panel["ticker"] = panel["ticker"].map(_normalize_ticker)
    panel["year"] = pd.to_numeric(panel["year"], errors="coerce").astype("Int64")
    panel = panel.loc[panel["year"].between(2016, 2024, inclusive="both")].copy()
    panel = panel.loc[panel["any_ai_talk"].fillna(0).astype(int).eq(1)].copy()
    for column in [*CONTROL_SPECS, "A_S", "PatentMismatch", "LowCredibility", "AI_Focus"]:
        if column in panel.columns:
            panel[column] = pd.to_numeric(panel[column], errors="coerce")
    return panel


def _pull_ibes_summary(panel: pd.DataFrame, *, dotenv_path: Path) -> pd.DataFrame:
    tickers = sorted({ticker for ticker in panel["ticker"].dropna().unique().tolist() if ticker})
    if not tickers:
        return pd.DataFrame()
    query = """
        with base as (
            select
                upper(coalesce(oftic, ticker)) as ibes_ticker,
                statpers,
                extract(year from statpers)::int as statpers_year,
                fpedats,
                numest,
                numup,
                numdown,
                meanest,
                stdev
            from ibes.statsum_epsus
            where measure = 'EPS'
              and fiscalp = 'ANN'
              and fpi = '1'
              and upper(coalesce(oftic, ticker)) = any(%s)
              and statpers >= date '2017-01-01'
              and statpers < date '2026-01-01'
        ), ranked as (
            select
                *,
                row_number() over (
                    partition by ibes_ticker, statpers_year
                    order by statpers desc, fpedats asc
                ) as rn
            from base
        )
        select
            ibes_ticker,
            statpers,
            statpers_year,
            fpedats,
            numest,
            numup,
            numdown,
            meanest,
            stdev
        from ranked
        where rn = 1
    """
    conn = _wrds_connection(dotenv_path)
    try:
        frame = pd.read_sql_query(query, conn, params=(tickers,))
    finally:
        conn.close()
    return frame


def _build_analyst_annual(raw: pd.DataFrame) -> pd.DataFrame:
    if raw.empty:
        return pd.DataFrame(
            columns=[
                "ticker",
                "year",
                "log_analyst_coverage_lead1",
                "analyst_dispersion_scaled_lead1",
                "analyst_revision_balance_lead1",
            ]
        )
    out = raw.copy()
    out["ticker"] = out["ibes_ticker"].map(_normalize_ticker)
    out["ibes_snapshot_year"] = pd.to_numeric(out["statpers_year"], errors="coerce").astype(int)
    out["year"] = out["ibes_snapshot_year"] - 1
    out["numest"] = pd.to_numeric(out["numest"], errors="coerce")
    out["numup"] = pd.to_numeric(out["numup"], errors="coerce")
    out["numdown"] = pd.to_numeric(out["numdown"], errors="coerce")
    out["meanest"] = pd.to_numeric(out["meanest"], errors="coerce")
    out["stdev"] = pd.to_numeric(out["stdev"], errors="coerce")
    out["log_analyst_coverage_lead1"] = np.log1p(out["numest"].clip(lower=0))
    denom = out["meanest"].abs()
    out["analyst_dispersion_scaled_lead1"] = np.where(
        denom.gt(1e-8), out["stdev"] / denom, np.nan
    )
    out["analyst_revision_balance_lead1"] = np.where(
        out["numest"].gt(0), (out["numup"] - out["numdown"]) / out["numest"], np.nan
    )
    for column in [
        "analyst_dispersion_scaled_lead1",
        "analyst_revision_balance_lead1",
    ]:
        series = pd.to_numeric(out[column], errors="coerce")
        lo = series.quantile(0.01)
        hi = series.quantile(0.99)
        if pd.notna(lo) and pd.notna(hi):
            out[column] = series.clip(lower=lo, upper=hi)
    keep = [
        "ticker",
        "year",
        "ibes_snapshot_year",
        "statpers",
        "fpedats",
        "numest",
        "numup",
        "numdown",
        "meanest",
        "stdev",
        "log_analyst_coverage_lead1",
        "analyst_dispersion_scaled_lead1",
        "analyst_revision_balance_lead1",
    ]
    out = out[keep].drop_duplicates(["ticker", "year"])
    return out


def _merge_sample(panel: pd.DataFrame, analyst: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    merged = panel.merge(analyst, on=["ticker", "year"], how="left", validate="many_to_one")
    summary = {
        "panel_rows": int(len(panel)),
        "panel_firms": int(panel["cik"].nunique()),
        "ibes_rows": int(len(analyst)),
        "ibes_tickers": int(analyst["ticker"].nunique()) if not analyst.empty else 0,
        "coverage_nonmissing": int(merged["log_analyst_coverage_lead1"].notna().sum()),
        "dispersion_nonmissing": int(merged["analyst_dispersion_scaled_lead1"].notna().sum()),
        "revision_nonmissing": int(merged["analyst_revision_balance_lead1"].notna().sum()),
        "years": [int(merged["year"].min()), int(merged["year"].max())],
        "guidance_note": "Detailed IBES guidance appears blocked under the current WRDS permissions; this first analyst packet therefore uses summary coverage, dispersion, and net revisions only.",
    }
    return merged, summary


def _fit_models(sample: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for outcome, outcome_label in OUTCOME_SPECS:
        for variant, variant_label in VARIANT_SPECS:
            needed = [outcome, variant, "sic2", "year", *CONTROL_SPECS]
            use = sample.dropna(subset=needed).copy()
            use = use.loc[use["cik"].astype(str).str.len().gt(0)].copy()
            if use.empty:
                rows.append(
                    {
                        "outcome": outcome,
                        "outcome_label": outcome_label,
                        "variant": variant,
                        "variant_label": variant_label,
                        "nobs": 0,
                        "coef": math.nan,
                        "se": math.nan,
                        "p_value": math.nan,
                        "outcome_mean": math.nan,
                    }
                )
                continue
            result, use, _adj_r2 = _fit_absorbed_ols(
                use,
                dependent=outcome,
                rhs_terms=[variant],
                absorb_col="sic2",
                include_year=True,
                controls=CONTROL_SPECS,
            )
            rows.append(
                {
                    "outcome": outcome,
                    "outcome_label": outcome_label,
                    "variant": variant,
                    "variant_label": variant_label,
                    "nobs": int(result.nobs),
                    "coef": float(result.params.get(variant, math.nan)),
                    "se": float(result.bse.get(variant, math.nan)),
                    "p_value": float(result.pvalues.get(variant, math.nan)),
                    "outcome_mean": float(use[outcome].mean()),
                }
            )
    return rows


def _build_table(results: list[dict[str, object]]) -> pd.DataFrame:
    keyed = {(row["outcome"], row["variant"]): row for row in results}
    rows: list[dict[str, object]] = []
    for outcome, outcome_label in OUTCOME_SPECS:
        row = {
            "row_label": outcome_label,
            "Outcome mean": f"{keyed[(outcome, 'PatentMismatch')]['outcome_mean']:.4f}" if math.isfinite(keyed[(outcome, 'PatentMismatch')]['outcome_mean']) else "",
            "Observations": keyed[(outcome, 'PatentMismatch')]['nobs'],
        }
        for variant, variant_label in VARIANT_SPECS:
            res = keyed[(outcome, variant)]
            row[variant_label] = _cell(res["coef"], res["se"], res["p_value"])
        rows.append(row)
    return pd.DataFrame(rows)


def _build_markdown(table_df: pd.DataFrame) -> str:
    headers = table_df.columns.tolist()
    rows = [[str(value) for value in row] for row in table_df.values.tolist()]
    return to_markdown_table(headers, rows)


def _render_latex(table_df: pd.DataFrame) -> str:
    lines = [
        "\\begin{table}[!htbp]",
        "\\centering",
        "\\caption{Analyst discernment and low-credibility AI disclosure}",
        "\\small",
        "\\begin{tabular}{lccccc}",
        "\\hline",
        "Outcome & PatentMismatch & LowCredibility & A/S ratio & Outcome mean & Observations "
        + "\\\\",
        "\\hline",
    ]
    for _, row in table_df.iterrows():
        lines.append(
            " & ".join(
                [
                    str(row["row_label"]).replace("_", "\\_"),
                    str(row["PatentMismatch"]),
                    str(row["LowCredibility"]),
                    str(row["A/S ratio"]),
                    str(row["Outcome mean"]),
                    str(row["Observations"]),
                ]
            )
            + " \\\\"
        )
    lines.extend(
        [
            "\\hline",
            "\\end{tabular}",
            "\\begin{flushleft}",
            "\\footnotesize Notes: The analyst outcomes come from the latest available annual EPS summary snapshot in each calendar year from `ibes.statsum_epsus`, then shifted back one year so the table reads current AI-disclosure characteristics against next-year analyst attention and uncertainty outcomes. All specifications use the AI-talking annual sample, SIC2 fixed effects, year fixed effects, lagged firm controls, and firm-clustered standard errors. Detailed guidance tests are deferred because `ibes.det_guidance` is not currently readable under the active WRDS permissions.",
            "\\end{flushleft}",
            "\\end{table}",
        ]
    )
    return "\n".join(lines)


def _write_docx(table_df: pd.DataFrame, path: Path) -> None:
    document = Document()
    _set_document_defaults(document)
    _set_landscape(document)
    _add_title(document, "Test 21. Analyst discernment")
    document.add_paragraph(
        "This table asks whether analysts react to low-credibility AI disclosure in ways that broad market prices did not clearly show. "
        "The outcomes use IBES annual EPS summary snapshots shifted back one year, so the disclosure variables in year `t` are related to analyst attention and uncertainty measures in `t+1`."
    )
    headers = list(table_df.columns)
    rows = [[(str(value), False) for value in row] for row in table_df.values.tolist()]
    _build_panel_table(document, headers, rows)
    _add_note(
        document,
        "Analyst outcomes come from `ibes.statsum_epsus`. Guidance tests are deferred because detailed guidance data are not currently readable under the active WRDS permissions."
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    document.save(path)


def _plot_outcomes(sample: pd.DataFrame, path: Path) -> None:
    _base_style()
    plot = sample.loc[sample["year"].between(2016, 2024)].copy()
    plot["mismatch_group"] = np.where(plot["PatentMismatch"].fillna(0).astype(int).eq(1), "Mismatch", "Non-mismatch")
    series = (
        plot.groupby(["year", "mismatch_group"], as_index=False)
        .agg(
            coverage=("log_analyst_coverage_lead1", "mean"),
            dispersion=("analyst_dispersion_scaled_lead1", "mean"),
        )
    )
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.5), sharex=True)
    for ax, value_col, title in [
        (axes[0], "coverage", "Analyst coverage t+1"),
        (axes[1], "dispersion", "Scaled dispersion t+1"),
    ]:
        for group, frame in series.groupby("mismatch_group", sort=False):
            frame = frame.sort_values("year")
            ax.plot(frame["year"], frame[value_col], marker="o", linewidth=2, label=group)
        ax.set_title(title)
        ax.set_xlabel("Disclosure year")
        ax.set_ylabel("Mean value")
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False)
    fig.suptitle("Analyst outcomes following annual AI-disclosure signals", y=0.98)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    fig.savefig(path.with_suffix('.pdf'), bbox_inches='tight')
    plt.close(fig)


def _write_writer_packet(*, output_path: Path, sample_summary: dict[str, object], keyed: dict[tuple[str, str], dict[str, object]]) -> None:
    disp = keyed[("analyst_dispersion_scaled_lead1", "PatentMismatch")]
    cov = keyed[("log_analyst_coverage_lead1", "PatentMismatch")]
    rev = keyed[("analyst_revision_balance_lead1", "PatentMismatch")]
    lines = [
        "# Writer Packet: Test 21 analyst discernment",
        "",
        "## Setup",
        "",
        "- Sample: AI-talking annual panel, years 2016-2024.",
        "- Analyst source: `ibes.statsum_epsus` annual EPS summary snapshots only.",
        "- Timing: latest annual IBES snapshot in year `t+1`, shifted back so the table reads disclosure year `t` against analyst outcomes in `t+1`.",
        f"- Panel rows: `{sample_summary['panel_rows']}` across `{sample_summary['panel_firms']}` firms.",
        f"- Non-missing coverage rows: `{sample_summary['coverage_nonmissing']}`.",
        f"- Non-missing dispersion rows: `{sample_summary['dispersion_nonmissing']}`.",
        f"- Non-missing revision rows: `{sample_summary['revision_nonmissing']}`.",
        "",
        "## Headline read",
        "",
        f"- PatentMismatch on analyst coverage t+1: `{cov['coef']:.4f}` (p=`{cov['p_value']:.3f}`).",
        f"- PatentMismatch on analyst dispersion t+1: `{disp['coef']:.4f}` (p=`{disp['p_value']:.3f}`).",
        f"- PatentMismatch on net revision balance t+1: `{rev['coef']:.4f}` (p=`{rev['p_value']:.3f}`).",
        "",
        "## Interpretation discipline",
        "",
        "- If coverage is flat but dispersion rises, that still supports an analyst-discernment story through uncertainty rather than attention.",
        "- Detailed guidance tests are deferred for now because the detailed guidance table is not currently readable under the active WRDS permissions.",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_result_notes(*, output_path: Path, sample_summary: dict[str, object], keyed: dict[tuple[str, str], dict[str, object]]) -> None:
    lines = [
        "- Test 21 opens Packet E using IBES annual EPS summary data only.",
        f"- Non-missing analyst coverage rows: `{sample_summary['coverage_nonmissing']}`.",
        f"- Non-missing analyst dispersion rows: `{sample_summary['dispersion_nonmissing']}`.",
        f"- Non-missing analyst revision rows: `{sample_summary['revision_nonmissing']}`.",
        f"- PatentMismatch on coverage t+1: `{keyed[('log_analyst_coverage_lead1', 'PatentMismatch')]['coef']:.4f}` (p=`{keyed[('log_analyst_coverage_lead1', 'PatentMismatch')]['p_value']:.3f}`).",
        f"- PatentMismatch on dispersion t+1: `{keyed[('analyst_dispersion_scaled_lead1', 'PatentMismatch')]['coef']:.4f}` (p=`{keyed[('analyst_dispersion_scaled_lead1', 'PatentMismatch')]['p_value']:.3f}`).",
        f"- PatentMismatch on net revision balance t+1: `{keyed[('analyst_revision_balance_lead1', 'PatentMismatch')]['coef']:.4f}` (p=`{keyed[('analyst_revision_balance_lead1', 'PatentMismatch')]['p_value']:.3f}`).",
        f"- Note: {sample_summary['guidance_note']}",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = _parse_args()
    run_dir = args.test_root / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    panel = _load_panel(args.annual_panel)
    raw_ibes = _pull_ibes_summary(panel, dotenv_path=args.dotenv_path)
    analyst = _build_analyst_annual(raw_ibes)
    sample, sample_summary = _merge_sample(panel, analyst)
    results = _fit_models(sample)
    table_df = _build_table(results)
    keyed = {(row['outcome'], row['variant']): row for row in results}

    base_name = f"{TEST_ID}_{args.run_id}"
    local_table_csv = run_dir / f"{base_name}.csv"
    table_df.to_csv(local_table_csv, index=False)
    local_raw = run_dir / 'ibes_annual_summary.parquet'
    analyst.to_parquet(local_raw, index=False)
    local_sample = run_dir / 'analyst_panel_sample.parquet'
    sample.to_parquet(local_sample, index=False)
    local_md = run_dir / f"{base_name}.md"
    local_md.write_text(_build_markdown(table_df), encoding='utf-8')
    local_tex = run_dir / f"{base_name}.tex"
    local_tex.write_text(_render_latex(table_df), encoding='utf-8')
    local_docx = run_dir / f"{base_name}.docx"
    _write_docx(table_df, local_docx)
    local_png = run_dir / f"{base_name}.png"
    _plot_outcomes(sample, local_png)
    local_writer = run_dir / f"{base_name}_writer_packet.md"
    _write_writer_packet(output_path=local_writer, sample_summary=sample_summary, keyed=keyed)
    local_notes = run_dir / f"{base_name}_result_notes.md"
    _write_result_notes(output_path=local_notes, sample_summary=sample_summary, keyed=keyed)

    paper_dirs = {
        'docx': args.paper_root / 'docx',
        'latex': args.paper_root / 'latex',
        'tables': args.paper_root / 'tables',
        'figures': args.paper_root / 'figures',
        'writer_packets': args.paper_root / 'writer_packets',
        'snippets': args.paper_root / 'snippets',
    }
    for dest in paper_dirs.values():
        dest.mkdir(parents=True, exist_ok=True)
    paper_docx = paper_dirs['docx'] / f"{base_name}.docx"
    paper_tex = paper_dirs['latex'] / f"{base_name}.tex"
    paper_csv = paper_dirs['tables'] / f"{base_name}.csv"
    paper_png = paper_dirs['figures'] / f"{base_name}.png"
    paper_pdf = paper_dirs['figures'] / f"{base_name}.pdf"
    paper_writer = paper_dirs['writer_packets'] / f"{base_name}.md"
    paper_notes = paper_dirs['snippets'] / f"{base_name}_result_notes.md"
    shutil.copy2(local_docx, paper_docx)
    shutil.copy2(local_tex, paper_tex)
    shutil.copy2(local_table_csv, paper_csv)
    shutil.copy2(local_png, paper_png)
    shutil.copy2(local_png.with_suffix('.pdf'), paper_pdf)
    shutil.copy2(local_writer, paper_writer)
    shutil.copy2(local_notes, paper_notes)

    manifest = {
        'test_id': TEST_ID,
        'module_path': MODULE_PATH,
        'run_id': args.run_id,
        'run_timestamp_utc': datetime.now(UTC).isoformat(),
        'inputs': {
            'annual_panel': str(args.annual_panel),
            'dotenv_path': str(args.dotenv_path),
        },
        'sample_summary': sample_summary,
        'paper_outputs': {
            'table_docx': str(paper_docx),
            'table_tex': str(paper_tex),
            'table_csv': str(paper_csv),
            'figure_png': str(paper_png),
            'figure_pdf': str(paper_pdf),
            'writer_packet': str(paper_writer),
            'result_notes': str(paper_notes),
        },
        'local_outputs': {
            'ibes_annual_summary': str(local_raw),
            'analyst_panel_sample': str(local_sample),
            'table_csv': str(local_table_csv),
            'table_docx': str(local_docx),
            'table_tex': str(local_tex),
            'figure_png': str(local_png),
            'writer_packet': str(local_writer),
            'result_notes': str(local_notes),
        },
        'results': results,
    }
    (run_dir / 'run_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
