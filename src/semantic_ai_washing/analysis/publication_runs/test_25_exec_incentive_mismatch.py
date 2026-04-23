"""Publication run driver for Test 25: executive incentives and low-credibility AI disclosure."""

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
from semantic_ai_washing.analysis.publication_runs.test_16_construct_variant_screen import (
    _add_construct_variants,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_ANNUAL_PANEL = (
    REPO_ROOT
    / "data/processed/panel/canonical/ever_speaker_panel_2016_2025_hybrid_api_a_conf49_v1.parquet"
)
DEFAULT_TEST_ROOT = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_2/test_runs/test_25_exec_incentive_mismatch"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated/v3_2"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_aiw_v3_2_test_25_exec_incentive_mismatch_main_v1"
TEST_ID = "test_25_exec_incentive_mismatch"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.test_25_exec_incentive_mismatch"

SUBSET_SPECS: list[tuple[str, str]] = [
    ("all", "Panel A. ExecuComp-linked AI-talking sample"),
    ("big", "Panel B. Big-firm ExecuComp sample"),
    ("post", "Panel C. Post-ChatGPT ExecuComp sample"),
]
PREDICTOR_SPECS: list[tuple[str, str]] = [
    ("equity_award_share_lag1", "CEO equity-award share (t-1)"),
    ("ownership_pct_lag1", "CEO ownership pct (t-1)"),
    ("log_tdc1_lag1", "Log CEO total pay (t-1)"),
]
OUTCOME_SPECS: list[tuple[str, str]] = [
    ("PatentMismatch", "PatentMismatch"),
    ("LowCredibility", "LowCredibility"),
    ("A_S", "A/S ratio"),
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
    panel["gvkey"] = panel["gvkey"].astype(str).str.strip()
    panel["year"] = pd.to_numeric(panel["year"], errors="coerce").astype("Int64")
    if "sic2" not in panel.columns and "sic" in panel.columns:
        sic = pd.to_numeric(panel["sic"], errors="coerce")
        panel["sic2"] = (sic // 100).astype("Int64")
    for column in [*CONTROL_SPECS, "A_S", "PatentMismatch", "LowCredibility", "AI_Focus", "market_cap_year_end"]:
        if column in panel.columns:
            panel[column] = pd.to_numeric(panel[column], errors="coerce")
    panel = panel.loc[panel["year"].between(2016, 2024, inclusive="both")].copy()
    panel = panel.loc[panel["any_ai_talk"].fillna(0).astype(int).eq(1)].copy()
    yearly_median_market_cap = panel.groupby("year")["market_cap_year_end"].transform("median")
    panel["big"] = (
        panel["market_cap_year_end"].notna()
        & yearly_median_market_cap.notna()
        & panel["market_cap_year_end"].gt(yearly_median_market_cap)
    )
    panel["post_chatgpt"] = panel["year"].ge(2023).astype(int)
    return panel


def _pull_execucomp(dotenv_path: Path) -> pd.DataFrame:
    query = """
        with ceo_rows as (
            select
                gvkey,
                year,
                execid,
                exec_fullname,
                ceoann,
                pceo,
                titleann,
                title,
                salary,
                bonus,
                stock_awards_fv,
                option_awards_fv,
                noneq_incent,
                total_curr,
                tdc1,
                shrown_excl_opts,
                shrown_excl_opts_pct,
                opt_unex_exer_est_val,
                opt_unex_unexer_est_val,
                row_number() over (
                    partition by gvkey, year
                    order by coalesce(tdc1, 0) desc, execid
                ) as rn,
                count(*) over (partition by gvkey, year) as n_ceo_rows
            from execcomp.anncomp
            where year between 2015 and 2024
              and (ceoann = 'CEO' or pceo = 'CEO')
        )
        select
            gvkey,
            year,
            execid,
            exec_fullname,
            ceoann,
            pceo,
            titleann,
            title,
            salary,
            bonus,
            stock_awards_fv,
            option_awards_fv,
            noneq_incent,
            total_curr,
            tdc1,
            shrown_excl_opts,
            shrown_excl_opts_pct,
            opt_unex_exer_est_val,
            opt_unex_unexer_est_val,
            n_ceo_rows
        from ceo_rows
        where rn = 1
    """
    conn = _wrds_connection(dotenv_path)
    try:
        frame = pd.read_sql_query(query, conn)
    finally:
        conn.close()
    return frame


def _prepare_execucomp(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    if raw.empty:
        return raw.copy(), {"exec_rows": 0, "exec_firms": 0, "co_ceo_firmyears": 0}
    out = raw.copy()
    out["gvkey"] = out["gvkey"].astype(str).str.strip()
    out["year"] = pd.to_numeric(out["year"], errors="coerce").astype("Int64")
    numeric_cols = [
        "salary",
        "bonus",
        "stock_awards_fv",
        "option_awards_fv",
        "noneq_incent",
        "total_curr",
        "tdc1",
        "shrown_excl_opts",
        "shrown_excl_opts_pct",
        "opt_unex_exer_est_val",
        "opt_unex_unexer_est_val",
        "n_ceo_rows",
    ]
    for column in numeric_cols:
        out[column] = pd.to_numeric(out[column], errors="coerce")
    out["equity_award_share"] = (
        out["stock_awards_fv"].fillna(0) + out["option_awards_fv"].fillna(0)
    ) / out["tdc1"].where(out["tdc1"].gt(0))
    out["ownership_pct"] = out["shrown_excl_opts_pct"]
    out["unvested_option_value"] = (
        out["opt_unex_exer_est_val"].fillna(0) + out["opt_unex_unexer_est_val"].fillna(0)
    )
    out["log_unvested_option_value"] = np.log1p(out["unvested_option_value"].clip(lower=0))
    out["log_tdc1"] = np.log1p(out["tdc1"].clip(lower=0))
    summary = {
        "exec_rows": int(len(out)),
        "exec_firms": int(out["gvkey"].nunique()),
        "co_ceo_firmyears": int(out["n_ceo_rows"].gt(1).sum()),
    }
    return out, summary


def _prepare_sample(panel: pd.DataFrame, ceo: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    lag = ceo[
        [
            "gvkey",
            "year",
            "execid",
            "exec_fullname",
            "equity_award_share",
            "ownership_pct",
            "log_unvested_option_value",
            "log_tdc1",
            "n_ceo_rows",
        ]
    ].copy()
    lag["year"] = lag["year"] + 1
    lag = lag.rename(
        columns={
            "execid": "ceo_execid_lag1",
            "exec_fullname": "ceo_exec_fullname_lag1",
            "equity_award_share": "equity_award_share_lag1",
            "ownership_pct": "ownership_pct_lag1",
            "log_unvested_option_value": "log_unvested_option_value_lag1",
            "log_tdc1": "log_tdc1_lag1",
            "n_ceo_rows": "n_ceo_rows_lag1",
        }
    )
    sample = panel.merge(lag, on=["gvkey", "year"], how="left", validate="many_to_one")
    summary = {
        "ai_talking_rows": int(len(sample)),
        "ai_talking_firms": int(sample["gvkey"].nunique()),
        "lagged_ceo_match_rows": int(sample["equity_award_share_lag1"].notna().sum()),
        "lagged_ceo_match_firms": int(sample.loc[sample["equity_award_share_lag1"].notna(), "gvkey"].nunique()),
        "lagged_big_rows": int(
            sample.loc[sample["equity_award_share_lag1"].notna() & sample["big"].fillna(False)].shape[0]
        ),
        "lagged_post_rows": int(
            sample.loc[sample["equity_award_share_lag1"].notna() & sample["post_chatgpt"].eq(1)].shape[0]
        ),
        "years": [int(sample["year"].min()), int(sample["year"].max())],
    }
    return sample, summary


def _subset_sample(sample: pd.DataFrame, subset_key: str) -> pd.DataFrame:
    matched = sample.loc[sample["equity_award_share_lag1"].notna()].copy()
    if subset_key == "big":
        return matched.loc[matched["big"].fillna(False)].copy()
    if subset_key == "post":
        return matched.loc[matched["post_chatgpt"].eq(1)].copy()
    return matched


def _fit_rows(sample: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for subset_key, subset_label in SUBSET_SPECS:
        subset = _subset_sample(sample, subset_key)
        for outcome, outcome_label in OUTCOME_SPECS:
            for predictor, predictor_label in PREDICTOR_SPECS:
                needed = [outcome, predictor, "gvkey", "year", "sic2", *CONTROL_SPECS]
                use = subset.dropna(subset=needed).copy()
                if use.empty:
                    rows.append(
                        {
                            "subset_key": subset_key,
                            "subset_label": subset_label,
                            "outcome": outcome,
                            "outcome_label": outcome_label,
                            "predictor": predictor,
                            "predictor_label": predictor_label,
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
                    rhs_terms=[predictor],
                    absorb_col="gvkey",
                    include_year=True,
                    controls=CONTROL_SPECS,
                )
                rows.append(
                    {
                        "subset_key": subset_key,
                        "subset_label": subset_label,
                        "outcome": outcome,
                        "outcome_label": outcome_label,
                        "predictor": predictor,
                        "predictor_label": predictor_label,
                        "nobs": int(result.nobs),
                        "outcome_mean": float(est_sample[outcome].mean()),
                        "params": result.params.to_dict(),
                        "bse": result.bse.to_dict(),
                        "pvalues": result.pvalues.to_dict(),
                    }
                )
    return rows


def _build_table(rows: list[dict[str, object]]) -> tuple[pd.DataFrame, dict[tuple[str, str, str], dict[str, object]]]:
    keyed = {(row["subset_key"], row["outcome"], row["predictor"]): row for row in rows}
    table_rows: list[dict[str, object]] = []
    for subset_key, subset_label in SUBSET_SPECS:
        table_rows.append(
            {
                "Panel": subset_label,
                "Outcome": "",
                "CEO equity-award share (t-1)": "",
                "CEO ownership pct (t-1)": "",
                "Log CEO total pay (t-1)": "",
                "Outcome mean": "",
                "Observations": "",
            }
        )
        for outcome, outcome_label in OUTCOME_SPECS:
            row = {"Panel": "", "Outcome": outcome_label}
            for predictor, predictor_label in PREDICTOR_SPECS:
                result = keyed[(subset_key, outcome, predictor)]
                row[predictor_label] = _coef_cell(
                    result["params"].get(predictor),
                    result["bse"].get(predictor),
                    result["pvalues"].get(predictor),
                )
            base = keyed[(subset_key, outcome, PREDICTOR_SPECS[0][0])]
            row["Outcome mean"] = f"{base['outcome_mean']:.3f}" if math.isfinite(base["outcome_mean"]) else ""
            row["Observations"] = str(base["nobs"])
            table_rows.append(row)
    return pd.DataFrame(table_rows), keyed


def _render_markdown(table_df: pd.DataFrame) -> str:
    headers = table_df.columns.tolist()
    rows = [[str(value) for value in row] for row in table_df.values.tolist()]
    return to_markdown_table(headers, rows)


def _render_latex(table_df: pd.DataFrame) -> str:
    lines = [
        "\\begin{table}[!htbp]",
        "\\centering",
        "\\caption{Executive incentives and low-credibility AI disclosure}",
        "\\small",
        "\\begin{tabular}{llcccrr}",
        "\\hline",
        "Panel & Outcome & Equity-award share & Ownership pct & Log CEO pay & Outcome mean & Obs. \\\\",
        "\\hline",
    ]
    for _, row in table_df.iterrows():
        if row["Panel"]:
            lines.append("\\multicolumn{7}{l}{\\textit{" + str(row["Panel"]).replace("&", "\\&") + "}} \\\\")
            continue
        lines.append(
            " & ".join(
                [
                    "",
                    str(row["Outcome"]).replace("_", "\\_"),
                    str(row["CEO equity-award share (t-1)"]),
                    str(row["CEO ownership pct (t-1)"]),
                    str(row["Log CEO total pay (t-1)"]),
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
            "\\footnotesize Notes: The sample links the AI-talking annual panel to lagged CEO observations from ExecuComp, using the highest-TDC1 CEO row when multiple CEO-designated rows exist in a firm-year. Predictors are one-year lagged CEO equity-award share of total compensation, CEO ownership percentage excluding options, and log total CEO pay. Specifications absorb firm and year fixed effects, include current controls, and cluster standard errors by firm.",
            "\\end{flushleft}",
            "\\end{table}",
        ]
    )
    return "\n".join(lines) + "\n"


def _write_docx(path: Path, table_df: pd.DataFrame, sample_summary: dict[str, object], exec_summary: dict[str, object]) -> None:
    document = Document()
    _set_document_defaults(document)
    _set_landscape(document)
    _add_title(document, "Test 25. Executive incentives and low-credibility AI disclosure")
    _add_note(
        document,
        (
            "This table asks whether lagged CEO incentives predict low-credibility AI disclosure inside the "
            "AI-talking annual panel. The external source is ExecuComp annual compensation data."
        ),
    )
    _add_note(
        document,
        (
            f"ExecuComp CEO rows = {exec_summary['exec_rows']:,} across {exec_summary['exec_firms']:,} firms; "
            f"lagged CEO-linked AI-talking rows = {sample_summary['lagged_ceo_match_rows']:,} across "
            f"{sample_summary['lagged_ceo_match_firms']:,} firms."
        ),
    )
    headers = table_df.columns.tolist()
    rows = [[(str(value), False) for value in row] for row in table_df.values.tolist()]
    _build_panel_table(document, headers, rows)
    document.save(path)


def _write_figure(rows: list[dict[str, object]], *, png_path: Path, pdf_path: Path) -> None:
    _base_style()
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.8), sharey=False)
    if len(axes) == 1:
        axes = [axes]
    subset_order = [label for _key, label in SUBSET_SPECS]
    for ax, (predictor, predictor_label) in zip(axes, PREDICTOR_SPECS, strict=True):
        subset_rows = [
            row
            for row in rows
            if row["predictor"] == predictor and row["outcome"] == "PatentMismatch"
        ]
        subset_rows = sorted(subset_rows, key=lambda row: subset_order.index(row["subset_label"]))
        x = list(range(len(subset_rows)))
        coef = [row["params"].get(predictor, math.nan) for row in subset_rows]
        err = [1.96 * row["bse"].get(predictor, math.nan) for row in subset_rows]
        ax.errorbar(x, coef, yerr=err, fmt="o", capsize=3, color="#1f4e79")
        ax.axhline(0, color="black", linewidth=0.9, linestyle="--")
        ax.set_xticks(x, [row["subset_label"].replace("Panel ", "") for row in subset_rows], rotation=20, ha="right")
        ax.set_title(predictor_label)
        ax.set_ylabel("PatentMismatch coefficient")
    fig.tight_layout()
    fig.savefig(png_path, dpi=220)
    fig.savefig(pdf_path)
    plt.close(fig)


def _write_writer_packet(path: Path, sample_summary: dict[str, object], exec_summary: dict[str, object], keyed: dict[tuple[str, str, str], dict[str, object]]) -> None:
    post_eq = keyed[("post", "PatentMismatch", "equity_award_share_lag1")]
    post_own = keyed[("post", "PatentMismatch", "ownership_pct_lag1")]
    big_own = keyed[("big", "PatentMismatch", "ownership_pct_lag1")]
    lines = [
        "# Writer Packet: Test 25 executive incentives and low-credibility AI disclosure",
        "",
        "## Setup",
        "",
        "- Sample: AI-talking annual panel linked to lagged CEO observations from ExecuComp.",
        "- CEO row rule: use the highest-TDC1 CEO-designated row in each firm-year when multiple CEO rows appear.",
        "- Predictors: lagged CEO equity-award share, lagged CEO ownership pct, lagged log CEO total pay.",
        "",
        "## Density",
        "",
        f"- ExecuComp CEO rows: `{exec_summary['exec_rows']:,}` across `{exec_summary['exec_firms']:,}` firms.",
        f"- Co-CEO firm-years collapsed by highest-TDC1 rule: `{exec_summary['co_ceo_firmyears']:,}`.",
        f"- Lagged CEO-linked AI-talking rows: `{sample_summary['lagged_ceo_match_rows']:,}` across `{sample_summary['lagged_ceo_match_firms']:,}` firms.",
        f"- Big matched rows: `{sample_summary['lagged_big_rows']:,}`; post-ChatGPT matched rows: `{sample_summary['lagged_post_rows']:,}`.",
        "",
        "## Main read",
        "",
        f"- Post-ChatGPT PatentMismatch on lagged CEO equity-award share: `{post_eq['params'].get('equity_award_share_lag1', math.nan):.4f}{_stars(post_eq['pvalues'].get('equity_award_share_lag1'))}` (p=`{post_eq['pvalues'].get('equity_award_share_lag1', math.nan):.3f}`).",
        f"- Post-ChatGPT PatentMismatch on lagged CEO ownership pct: `{post_own['params'].get('ownership_pct_lag1', math.nan):.4f}{_stars(post_own['pvalues'].get('ownership_pct_lag1'))}` (p=`{post_own['pvalues'].get('ownership_pct_lag1', math.nan):.3f}`).",
        f"- Big-firm PatentMismatch on lagged CEO ownership pct: `{big_own['params'].get('ownership_pct_lag1', math.nan):.4f}{_stars(big_own['pvalues'].get('ownership_pct_lag1'))}` (p=`{big_own['pvalues'].get('ownership_pct_lag1', math.nan):.3f}`).",
        "",
        "## Placement",
        "",
        "- Best use: Packet F determinants table, probably main text if the incentive lane remains one of the cleanest explanations for mismatch.",
        "- Suggested framing: stronger equity-oriented CEO incentives and higher CEO ownership are associated with more low-credibility AI disclosure where the incentive channel is most salient, especially in the covered large-firm / post-ChatGPT slice.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_result_notes(path: Path, rows: list[dict[str, object]]) -> None:
    lines = [
        "# Result Notes: Test 25 executive incentives and low-credibility AI disclosure",
        "",
        "This packet links lagged CEO incentive structure to later low-credibility AI disclosure in the AI-talking sample.",
        "",
    ]
    for subset_key, subset_label in SUBSET_SPECS:
        lines.append(f"## {subset_label}")
        for outcome, outcome_label in OUTCOME_SPECS:
            lines.append(f"### {outcome_label}")
            for predictor, predictor_label in PREDICTOR_SPECS:
                row = next(
                    item
                    for item in rows
                    if item["subset_key"] == subset_key and item["outcome"] == outcome and item["predictor"] == predictor
                )
                coef = row["params"].get(predictor, math.nan)
                se = row["bse"].get(predictor, math.nan)
                p_value = row["pvalues"].get(predictor, math.nan)
                if math.isfinite(coef):
                    lines.append(
                        f"- {predictor_label}: {coef:.4f}{_stars(p_value)} "
                        f"(SE {se:.4f}, p={p_value:.3f}, n={row['nobs']:,})."
                    )
                else:
                    lines.append(f"- {predictor_label}: insufficient sample.")
            lines.append("")
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def main() -> None:
    args = _parse_args()
    run_root = args.test_root / args.run_id
    if run_root.exists():
        shutil.rmtree(run_root)
    run_root.mkdir(parents=True, exist_ok=True)
    args.paper_root.mkdir(parents=True, exist_ok=True)
    for subdir in ["docx", "latex", "tables", "figures", "writer_packets", "snippets"]:
        (args.paper_root / subdir).mkdir(parents=True, exist_ok=True)

    panel = _load_panel(args.annual_panel)
    raw = _pull_execucomp(args.dotenv_path)
    ceo, exec_summary = _prepare_execucomp(raw)
    sample, sample_summary = _prepare_sample(panel, ceo)
    rows = _fit_rows(sample)
    table_df, keyed = _build_table(rows)
    markdown = _render_markdown(table_df)
    latex = _render_latex(table_df)

    stem = f"{TEST_ID}_{args.run_id}"
    docx_path = run_root / f"{stem}.docx"
    tex_path = run_root / f"{stem}.tex"
    csv_path = run_root / f"{stem}.csv"
    png_path = run_root / f"{stem}.png"
    pdf_path = run_root / f"{stem}.pdf"
    md_path = run_root / f"{stem}.md"
    writer_path = run_root / f"{stem}_writer_packet.md"
    notes_path = run_root / f"{stem}_result_notes.md"
    raw_path = run_root / "execucomp_ceo_rows.parquet"
    sample_path = run_root / "exec_incentive_sample.parquet"

    _write_docx(docx_path, table_df, sample_summary, exec_summary)
    tex_path.write_text(latex, encoding="utf-8")
    csv_path.write_text(table_df.to_csv(index=False), encoding="utf-8")
    md_path.write_text(markdown, encoding="utf-8")
    _write_figure(rows, png_path=png_path, pdf_path=pdf_path)
    _write_writer_packet(writer_path, sample_summary, exec_summary, keyed)
    _write_result_notes(notes_path, rows)
    ceo.to_parquet(raw_path, index=False)
    sample.to_parquet(sample_path, index=False)

    for subdir, path in {
        "docx": docx_path,
        "latex": tex_path,
        "tables": csv_path,
        "figures": png_path,
        "writer_packets": writer_path,
        "snippets": notes_path,
    }.items():
        shutil.copy2(path, args.paper_root / subdir / path.name)

    manifest = {
        "test_id": TEST_ID,
        "module_path": MODULE_PATH,
        "run_id": args.run_id,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "sample_summary": sample_summary,
        "exec_summary": exec_summary,
        "outputs": {
            "docx": str(docx_path),
            "tex": str(tex_path),
            "csv": str(csv_path),
            "png": str(png_path),
            "pdf": str(pdf_path),
            "markdown": str(md_path),
            "writer_packet": str(writer_path),
            "result_notes": str(notes_path),
            "ceo_rows": str(raw_path),
            "sample": str(sample_path),
        },
    }
    (run_root / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
