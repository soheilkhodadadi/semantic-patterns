"""Publication run driver for Test 26: board monitoring and low-credibility AI disclosure."""

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
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_2/test_runs/test_26_board_monitoring"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated/v3_2"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_aiw_v3_2_test_26_board_monitoring_main_v1"
TEST_ID = "test_26_board_monitoring"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.test_26_board_monitoring"

SUBSET_SPECS: list[tuple[str, str]] = [
    ("all", "Panel A. Matched board-monitoring sample"),
    ("big", "Panel B. Big-firm board-monitoring sample"),
    ("post", "Panel C. Post-ChatGPT board-monitoring sample"),
]
PREDICTOR_SPECS: list[tuple[str, str]] = [
    ("outside_public_boards_avg_lag1", "Avg outside public boards (t-1)"),
    ("cg_share_lag1", "Governance committee share (t-1)"),
    ("audit_share_lag1", "Audit committee share (t-1)"),
    ("board_size_lag1", "Board size (t-1)"),
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
    panel["ticker"] = panel["ticker"].astype(str).str.upper().str.strip()
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


def _pull_board(dotenv_path: Path) -> pd.DataFrame:
    query = """
        select
            year,
            upper(ticker) as ticker,
            female,
            audit_membership,
            comp_membership,
            cg_membership,
            nom_membership,
            outside_public_boards,
            financial_expert,
            non_ceo_leader,
            former_employee_yn
        from risk_directors.rmdirectors
        where year between 2015 and 2024
          and ticker is not null
    """
    conn = _wrds_connection(dotenv_path)
    try:
        frame = pd.read_sql_query(query, conn)
    finally:
        conn.close()
    return frame


def _prepare_board(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    if raw.empty:
        return raw.copy(), {"board_rows": 0, "board_ticker_years": 0}
    out = raw.copy()
    yes_no_vars = ["female", "financial_expert", "former_employee_yn"]
    for column in yes_no_vars:
        out[f"{column}_ind"] = out[column].astype(str).str.upper().eq("YES").astype(float)
    committee_vars = ["audit_membership", "comp_membership", "cg_membership", "nom_membership"]
    for column in committee_vars:
        out[f"{column}_ind"] = out[column].astype(str).str.upper().isin(["MEMBER", "CHAIR"]).astype(float)
    out["non_ceo_leader_ind"] = out["non_ceo_leader"].astype(str).str.upper().isin(
        ["NON EMP CHAIR", "LEAD DIR"]
    ).astype(float)
    out["outside_public_boards"] = pd.to_numeric(out["outside_public_boards"], errors="coerce")
    agg = out.groupby(["ticker", "year"], as_index=False).agg(
        female_share=("female_ind", "mean"),
        audit_share=("audit_membership_ind", "mean"),
        comp_share=("comp_membership_ind", "mean"),
        cg_share=("cg_membership_ind", "mean"),
        nom_share=("nom_membership_ind", "mean"),
        fin_expert_share=("financial_expert_ind", "mean"),
        non_ceo_leader_share=("non_ceo_leader_ind", "mean"),
        former_employee_share=("former_employee_yn_ind", "mean"),
        outside_public_boards_avg=("outside_public_boards", "mean"),
        board_size=("ticker", "size"),
    )
    summary = {
        "board_rows": int(len(out)),
        "board_ticker_years": int(len(agg)),
        "ticker_count": int(agg["ticker"].nunique()),
    }
    return agg, summary


def _prepare_sample(panel: pd.DataFrame, board: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    lag = board.copy()
    lag["year"] = lag["year"] + 1
    lag = lag.rename(
        columns={
            "female_share": "female_share_lag1",
            "audit_share": "audit_share_lag1",
            "comp_share": "comp_share_lag1",
            "cg_share": "cg_share_lag1",
            "nom_share": "nom_share_lag1",
            "fin_expert_share": "fin_expert_share_lag1",
            "non_ceo_leader_share": "non_ceo_leader_share_lag1",
            "former_employee_share": "former_employee_share_lag1",
            "outside_public_boards_avg": "outside_public_boards_avg_lag1",
            "board_size": "board_size_lag1",
        }
    )
    sample = panel.merge(lag, on=["ticker", "year"], how="left", validate="many_to_one")
    summary = {
        "ai_talking_rows": int(len(sample)),
        "ai_talking_firms": int(sample["gvkey"].nunique()),
        "lagged_board_match_rows": int(sample["outside_public_boards_avg_lag1"].notna().sum()),
        "lagged_board_match_firms": int(
            sample.loc[sample["outside_public_boards_avg_lag1"].notna(), "gvkey"].nunique()
        ),
        "lagged_big_rows": int(
            sample.loc[sample["outside_public_boards_avg_lag1"].notna() & sample["big"].fillna(False)].shape[0]
        ),
        "lagged_post_rows": int(
            sample.loc[sample["outside_public_boards_avg_lag1"].notna() & sample["post_chatgpt"].eq(1)].shape[0]
        ),
        "years": [int(sample["year"].min()), int(sample["year"].max())],
    }
    return sample, summary


def _subset_sample(sample: pd.DataFrame, subset_key: str) -> pd.DataFrame:
    matched = sample.loc[sample["outside_public_boards_avg_lag1"].notna()].copy()
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
                "Avg outside public boards (t-1)": "",
                "Governance committee share (t-1)": "",
                "Audit committee share (t-1)": "",
                "Board size (t-1)": "",
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
        "\\caption{Board monitoring and low-credibility AI disclosure}",
        "\\small",
        "\\begin{tabular}{llccccrr}",
        "\\hline",
        "Panel & Outcome & Outside boards & Gov. comm. share & Audit share & Board size & Outcome mean & Obs. \\\\",
        "\\hline",
    ]
    for _, row in table_df.iterrows():
        if row["Panel"]:
            lines.append("\\multicolumn{8}{l}{\\textit{" + str(row["Panel"]).replace("&", "\\&") + "}} \\\\")
            continue
        lines.append(
            " & ".join(
                [
                    "",
                    str(row["Outcome"]).replace("_", "\\_"),
                    str(row["Avg outside public boards (t-1)"]),
                    str(row["Governance committee share (t-1)"]),
                    str(row["Audit committee share (t-1)"]),
                    str(row["Board size (t-1)"]),
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
            "\\footnotesize Notes: The sample links the AI-talking annual panel to lagged board-monitoring aggregates from Risk Directors `rmdirectors`, merged on ticker-year. Predictors are the prior-year average number of outside public boards held by directors, governance committee share, audit committee share, and board size. Specifications absorb firm and year fixed effects, include current controls, and cluster standard errors by firm.",
            "\\end{flushleft}",
            "\\end{table}",
        ]
    )
    return "\n".join(lines) + "\n"


def _write_docx(path: Path, table_df: pd.DataFrame, sample_summary: dict[str, object], board_summary: dict[str, object]) -> None:
    document = Document()
    _set_document_defaults(document)
    _set_landscape(document)
    _add_title(document, "Test 26. Board monitoring and low-credibility AI disclosure")
    _add_note(
        document,
        (
            "This table asks whether lagged board-monitoring structure predicts low-credibility AI disclosure "
            "inside the AI-talking annual panel. The external source is Risk Directors `rmdirectors`."
        ),
    )
    _add_note(
        document,
        (
            f"Board raw rows = {board_summary['board_rows']:,}; ticker-years = {board_summary['board_ticker_years']:,}; "
            f"lagged board-linked AI-talking rows = {sample_summary['lagged_board_match_rows']:,} across "
            f"{sample_summary['lagged_board_match_firms']:,} firms."
        ),
    )
    headers = table_df.columns.tolist()
    rows = [[(str(value), False) for value in row] for row in table_df.values.tolist()]
    _build_panel_table(document, headers, rows)
    document.save(path)


def _write_figure(rows: list[dict[str, object]], *, png_path: Path, pdf_path: Path) -> None:
    _base_style()
    fig, axes = plt.subplots(1, 4, figsize=(12.0, 3.8), sharey=False)
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


def _write_writer_packet(path: Path, sample_summary: dict[str, object], board_summary: dict[str, object], keyed: dict[tuple[str, str, str], dict[str, object]]) -> None:
    post_outside = keyed[("post", "PatentMismatch", "outside_public_boards_avg_lag1")]
    post_board = keyed[("post", "PatentMismatch", "board_size_lag1")]
    all_cg = keyed[("all", "LowCredibility", "cg_share_lag1")]
    lines = [
        "# Writer Packet: Test 26 board monitoring and low-credibility AI disclosure",
        "",
        "## Setup",
        "",
        "- Sample: AI-talking annual panel linked to lagged Risk Directors board aggregates by ticker-year.",
        "- Predictors: lagged outside-board exposure, governance committee share, audit committee share, and board size.",
        "- Source note: the older `risk.directors` table ends in 2006, so the active lane uses `risk_directors.rmdirectors` instead.",
        "",
        "## Density",
        "",
        f"- Board ticker-years: `{board_summary['board_ticker_years']:,}` across `{board_summary['ticker_count']:,}` tickers.",
        f"- Lagged board-linked AI-talking rows: `{sample_summary['lagged_board_match_rows']:,}` across `{sample_summary['lagged_board_match_firms']:,}` firms.",
        f"- Big matched rows: `{sample_summary['lagged_big_rows']:,}`; post-ChatGPT matched rows: `{sample_summary['lagged_post_rows']:,}`.",
        "",
        "## Main read",
        "",
        f"- All-sample LowCredibility on lagged governance committee share: `{all_cg['params'].get('cg_share_lag1', math.nan):.4f}{_stars(all_cg['pvalues'].get('cg_share_lag1'))}` (p=`{all_cg['pvalues'].get('cg_share_lag1', math.nan):.3f}`).",
        f"- Post-ChatGPT PatentMismatch on lagged average outside public boards: `{post_outside['params'].get('outside_public_boards_avg_lag1', math.nan):.4f}{_stars(post_outside['pvalues'].get('outside_public_boards_avg_lag1'))}` (p=`{post_outside['pvalues'].get('outside_public_boards_avg_lag1', math.nan):.3f}`).",
        f"- Post-ChatGPT PatentMismatch on lagged board size: `{post_board['params'].get('board_size_lag1', math.nan):.4f}{_stars(post_board['pvalues'].get('board_size_lag1'))}` (p=`{post_board['pvalues'].get('board_size_lag1', math.nan):.3f}`).",
        "",
        "## Placement",
        "",
        "- Best use: Packet F governance explanation table or strong appendix candidate.",
        "- Suggested framing: some board-monitoring structures are associated with less low-credibility AI disclosure, especially in the post-ChatGPT period.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_result_notes(path: Path, rows: list[dict[str, object]]) -> None:
    lines = [
        "# Result Notes: Test 26 board monitoring and low-credibility AI disclosure",
        "",
        "This packet links lagged board-monitoring structure to later low-credibility AI disclosure in the AI-talking sample.",
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
    raw = _pull_board(args.dotenv_path)
    board, board_summary = _prepare_board(raw)
    sample, sample_summary = _prepare_sample(panel, board)
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
    board_path = run_root / "board_monitoring_agg.parquet"
    sample_path = run_root / "board_monitoring_sample.parquet"

    _write_docx(docx_path, table_df, sample_summary, board_summary)
    tex_path.write_text(latex, encoding="utf-8")
    csv_path.write_text(table_df.to_csv(index=False), encoding="utf-8")
    md_path.write_text(markdown, encoding="utf-8")
    _write_figure(rows, png_path=png_path, pdf_path=pdf_path)
    _write_writer_packet(writer_path, sample_summary, board_summary, keyed)
    _write_result_notes(notes_path, rows)
    board.to_parquet(board_path, index=False)
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
        "board_summary": board_summary,
        "outputs": {
            "docx": str(docx_path),
            "tex": str(tex_path),
            "csv": str(csv_path),
            "png": str(png_path),
            "pdf": str(pdf_path),
            "markdown": str(md_path),
            "writer_packet": str(writer_path),
            "result_notes": str(notes_path),
            "board_agg": str(board_path),
            "sample": str(sample_path),
        },
    }
    (run_root / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
