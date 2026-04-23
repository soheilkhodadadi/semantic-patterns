"""Publication run driver for Test 27: board technical human capital and low-credibility AI disclosure."""

from __future__ import annotations

import argparse
import json
import math
import re
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
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_2/test_runs/test_27_board_tech_human_capital"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated/v3_2"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_aiw_v3_2_test_27_board_tech_human_capital_main_v1"
TEST_ID = "test_27_board_tech_human_capital"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.test_27_board_tech_human_capital"

SUBSET_SPECS: list[tuple[str, str]] = [
    ("all", "Panel A. Matched board-tech sample"),
    ("big", "Panel B. Big-firm board-tech sample"),
    ("post", "Panel C. Post-ChatGPT board-tech sample"),
]
PREDICTOR_SPECS: list[tuple[str, str]] = [
    ("tech_lead_share_lag1", "Tech leadership share (t-1)"),
    ("tech_hc_share_lag1", "Tech human-capital share (t-1)"),
    ("any_tech_hc_lag1", "Any tech human capital (t-1)"),
]
OUTCOME_SPECS: list[tuple[str, str]] = [
    ("PatentMismatch", "PatentMismatch"),
    ("LowCredibility", "LowCredibility"),
    ("A_S", "A/S ratio"),
]
CONTROL_SPECS = ["AI_Focus", "ln_assets", "cash", "leverage", "roa"]
TECH_LEAD_PATTERN = re.compile(
    r"(?:^|\W)cto(?:$|\W)|chief technology officer|(?:^|\W)cio(?:$|\W)|"
    r"chief information officer|chief digital officer|chief data officer|"
    r"chief science officer|head of engineering|vice president\s*-\s*engineering|"
    r"chief software architect|chief ai officer|artificial intelligence|"
    r"head of data science|vice president\s*-\s*data science",
    re.IGNORECASE,
)
STEM_PATTERN = re.compile(
    r"computer science|engineering|electrical|mechanical|physics|mathematics|"
    r"statistics|data science|information systems|operations research|"
    r"artificial intelligence|machine learning",
    re.IGNORECASE,
)


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


def _pull_company_map(dotenv_path: Path, tickers: list[str]) -> pd.DataFrame:
    conn = _wrds_connection(dotenv_path)
    try:
        frame = pd.read_sql_query(
            """
            select distinct
                n.companyid,
                upper(s.ticker) as ticker
            from boardex.na_wrds_company_names n
            join boardex.na_company_profile_stocks s
              on n.boardid = s.boardid
            where s.ticker is not null
              and s.primarystock = 'Yes'
            """,
            conn,
        )
    finally:
        conn.close()
    frame["ticker"] = frame["ticker"].astype(str).str.upper().str.strip()
    frame = frame.loc[frame["ticker"].isin(tickers)].drop_duplicates().copy()
    return frame


def _pull_board_roles(dotenv_path: Path, company_ids: list[int]) -> pd.DataFrame:
    conn = _wrds_connection(dotenv_path)
    try:
        frame = pd.read_sql_query(
            """
            select
                companyid,
                directorid,
                datestartrole,
                dateendrole
            from boardex.na_wrds_org_composition
            where companyid = any(%s)
              and seniority in ('Supervisory Director', 'Executive Director')
              and datestartrole <= '2024-12-31'
              and dateendrole >= '2015-01-01'
            """,
            conn,
            params=(company_ids,),
        )
    finally:
        conn.close()
    return frame


def _pull_director_emp(dotenv_path: Path, director_ids: list[int]) -> pd.DataFrame:
    conn = _wrds_connection(dotenv_path)
    try:
        frame = pd.read_sql_query(
            """
            select
                directorid,
                coalesce(rolename, '') as rolename
            from boardex.na_dir_profile_emp
            where directorid = any(%s)
            """,
            conn,
            params=(director_ids,),
        )
    finally:
        conn.close()
    return frame


def _pull_director_education(dotenv_path: Path, director_ids: list[int]) -> pd.DataFrame:
    conn = _wrds_connection(dotenv_path)
    try:
        frame = pd.read_sql_query(
            """
            select
                directorid,
                coalesce(qualification, '') as qualification,
                coalesce(fulltextdescription, '') as fulltextdescription
            from boardex.na_dir_profile_education
            where directorid = any(%s)
            """,
            conn,
            params=(director_ids,),
        )
    finally:
        conn.close()
    return frame


def _prepare_active_board(
    panel: pd.DataFrame,
    company_map: pd.DataFrame,
    board_roles: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, object]]:
    roles = board_roles.merge(company_map[["companyid", "ticker"]], on="companyid", how="left")
    roles = roles.dropna(subset=["ticker", "directorid"]).copy()
    roles["year_start"] = pd.to_datetime(roles["datestartrole"], errors="coerce").dt.year.fillna(1900)
    roles["year_end"] = (
        pd.to_datetime(roles["dateendrole"], errors="coerce").dt.year.fillna(2025).clip(upper=2025)
    )
    active_rows: list[pd.DataFrame] = []
    for year in range(2016, 2025):
        active = roles.loc[
            (roles["year_start"] <= year) & (roles["year_end"] >= year),
            ["ticker", "directorid"],
        ].drop_duplicates()
        active["year"] = year
        active_rows.append(active)
    active = pd.concat(active_rows, ignore_index=True)
    matched = panel.merge(active, on=["ticker", "year"], how="inner")
    summary = {
        "company_map_rows": int(len(company_map)),
        "company_count": int(company_map["companyid"].nunique()),
        "active_board_rows": int(len(active)),
        "active_board_tickers": int(active["ticker"].nunique()),
        "active_directors": int(active["directorid"].nunique()),
        "matched_board_rows": int(len(matched)),
        "matched_firms": int(matched["gvkey"].nunique()),
    }
    return active, summary


def _prepare_human_capital(
    emp: pd.DataFrame,
    education: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, object]]:
    emp = emp.copy()
    emp["rolename"] = emp["rolename"].fillna("").astype(str).str.strip()
    emp["tech_lead_flag"] = emp["rolename"].str.contains(TECH_LEAD_PATTERN, regex=True)
    tech = emp.groupby("directorid", as_index=False)["tech_lead_flag"].max()

    education = education.copy()
    education["text"] = (
        education["qualification"].fillna("").astype(str).str.strip()
        + " "
        + education["fulltextdescription"].fillna("").astype(str).str.strip()
    ).str.strip()
    education["stem_flag"] = education["text"].str.contains(STEM_PATTERN, regex=True)
    stem = education.groupby("directorid", as_index=False)["stem_flag"].max()

    human_cap = tech.merge(stem, on="directorid", how="outer")
    for column in ["tech_lead_flag", "stem_flag"]:
        human_cap[column] = human_cap[column].astype("boolean").fillna(False).astype(bool)
    human_cap["tech_hc_flag"] = human_cap[["tech_lead_flag", "stem_flag"]].max(axis=1)
    summary = {
        "emp_rows": int(len(emp)),
        "tech_lead_directors": int(human_cap["tech_lead_flag"].sum()),
        "stem_directors": int(human_cap["stem_flag"].sum()),
        "tech_hc_directors": int(human_cap["tech_hc_flag"].sum()),
    }
    return human_cap, summary


def _prepare_sample(
    panel: pd.DataFrame,
    active_board: pd.DataFrame,
    human_cap: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, object]]:
    active = active_board.merge(human_cap, on="directorid", how="left").copy()
    for column in ["tech_lead_flag", "stem_flag", "tech_hc_flag"]:
        active[column] = active[column].astype("boolean").fillna(False).astype(float)
    board_year = active.groupby(["ticker", "year"], as_index=False).agg(
        board_size=("directorid", "nunique"),
        tech_lead_share=("tech_lead_flag", "mean"),
        stem_share=("stem_flag", "mean"),
        tech_hc_share=("tech_hc_flag", "mean"),
        any_tech_hc=("tech_hc_flag", "max"),
    )
    lag = board_year.copy()
    lag["year"] = lag["year"] + 1
    lag = lag.rename(
        columns={
            "board_size": "board_size_lag1",
            "tech_lead_share": "tech_lead_share_lag1",
            "stem_share": "stem_share_lag1",
            "tech_hc_share": "tech_hc_share_lag1",
            "any_tech_hc": "any_tech_hc_lag1",
        }
    )
    sample = panel.merge(lag, on=["ticker", "year"], how="left", validate="many_to_one")
    summary = {
        "lagged_boardtech_rows": int(sample["tech_hc_share_lag1"].notna().sum()),
        "lagged_boardtech_firms": int(sample.loc[sample["tech_hc_share_lag1"].notna(), "gvkey"].nunique()),
        "lagged_big_rows": int(
            sample.loc[sample["tech_hc_share_lag1"].notna() & sample["big"].fillna(False)].shape[0]
        ),
        "lagged_post_rows": int(
            sample.loc[sample["tech_hc_share_lag1"].notna() & sample["post_chatgpt"].eq(1)].shape[0]
        ),
    }
    return sample, summary


def _subset_sample(sample: pd.DataFrame, subset_key: str) -> pd.DataFrame:
    matched = sample.loc[sample["tech_hc_share_lag1"].notna()].copy()
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
                needed = [outcome, predictor, "gvkey", "year", *CONTROL_SPECS]
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
                "Tech leadership share (t-1)": "",
                "Tech human-capital share (t-1)": "",
                "Any tech human capital (t-1)": "",
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
        "\\caption{Board technical human capital and low-credibility AI disclosure}",
        "\\small",
        "\\begin{tabular}{llcccrr}",
        "\\hline",
        "Panel & Outcome & Tech leadership share & Tech HC share & Any tech HC & Outcome mean & Obs. \\\\",
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
                    str(row["Tech leadership share (t-1)"]),
                    str(row["Tech human-capital share (t-1)"]),
                    str(row["Any tech human capital (t-1)"]),
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
            "\\footnotesize Notes: The sample links the AI-talking annual panel to lagged BoardEx-based board technical human-capital measures. Active board seats come from `na_wrds_org_composition`, filtered to supervisory and executive directors only. Technical-human-capital flags are built from directors' prior technical leadership role titles and a sparse STEM-education overlay. Specifications absorb firm and year fixed effects, include current controls, and cluster standard errors by firm.",
            "\\end{flushleft}",
            "\\end{table}",
        ]
    )
    return "\n".join(lines) + "\n"


def _write_docx(
    path: Path,
    table_df: pd.DataFrame,
    active_summary: dict[str, object],
    hc_summary: dict[str, object],
    sample_summary: dict[str, object],
) -> None:
    document = Document()
    _set_document_defaults(document)
    _set_landscape(document)
    _add_title(document, "Test 27. Board technical human capital and low-credibility AI disclosure")
    _add_note(
        document,
        (
            "This table asks whether lagged board technical human capital predicts lower low-credibility AI disclosure "
            "inside the AI-talking annual panel. The external source is BoardEx."
        ),
    )
    _add_note(
        document,
        (
            f"Matched active board rows = {active_summary['active_board_rows']:,}; "
            f"matched AI-talking firms = {active_summary['matched_firms']:,}; "
            f"lagged board-tech linked rows = {sample_summary['lagged_boardtech_rows']:,} across "
            f"{sample_summary['lagged_boardtech_firms']:,} firms."
        ),
    )
    _add_note(
        document,
        (
            f"Technical-lead directors = {hc_summary['tech_lead_directors']:,}; "
            f"STEM-education directors = {hc_summary['stem_directors']:,}; "
            f"combined tech-human-capital directors = {hc_summary['tech_hc_directors']:,}."
        ),
    )
    headers = table_df.columns.tolist()
    rows = [[(str(value), False) for value in row] for row in table_df.values.tolist()]
    _build_panel_table(document, headers, rows)
    document.save(path)


def _write_figure(rows: list[dict[str, object]], *, png_path: Path, pdf_path: Path) -> None:
    _base_style()
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.8), sharey=False)
    subset_order = [label for _key, label in SUBSET_SPECS]
    for ax, (predictor, predictor_label) in zip(axes, PREDICTOR_SPECS, strict=True):
        subset_rows = [
            row for row in rows if row["predictor"] == predictor and row["outcome"] == "PatentMismatch"
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


def _write_writer_packet(
    path: Path,
    sample_summary: dict[str, object],
    hc_summary: dict[str, object],
    keyed: dict[tuple[str, str, str], dict[str, object]],
) -> None:
    all_tech = keyed[("all", "PatentMismatch", "tech_hc_share_lag1")]
    all_lead = keyed[("all", "PatentMismatch", "tech_lead_share_lag1")]
    big_lead = keyed[("big", "LowCredibility", "tech_lead_share_lag1")]
    lines = [
        "# Writer Packet: Test 27 board technical human capital and low-credibility AI disclosure",
        "",
        "## Setup",
        "",
        "- Sample: AI-talking annual panel linked to lagged BoardEx board-level technical human-capital measures.",
        "- Board seat filter: supervisory and executive directors only.",
        "- Narrow proxy: prior technical-leadership role titles.",
        "- Broad proxy: technical-leadership role titles plus a sparse STEM-education overlay.",
        "",
        "## Density",
        "",
        f"- Lagged board-tech linked rows: `{sample_summary['lagged_boardtech_rows']:,}` across `{sample_summary['lagged_boardtech_firms']:,}` firms.",
        f"- Big matched rows: `{sample_summary['lagged_big_rows']:,}`; post-ChatGPT matched rows: `{sample_summary['lagged_post_rows']:,}`.",
        f"- Technical-lead directors: `{hc_summary['tech_lead_directors']:,}`; combined tech-human-capital directors: `{hc_summary['tech_hc_directors']:,}`.",
        "",
        "## Main read",
        "",
        f"- All-sample `PatentMismatch` on tech human-capital share: `{all_tech['params'].get('tech_hc_share_lag1', math.nan):.4f}{_stars(all_tech['pvalues'].get('tech_hc_share_lag1'))}` (p=`{all_tech['pvalues'].get('tech_hc_share_lag1', math.nan):.3f}`).",
        f"- All-sample `PatentMismatch` on tech leadership share: `{all_lead['params'].get('tech_lead_share_lag1', math.nan):.4f}{_stars(all_lead['pvalues'].get('tech_lead_share_lag1'))}` (p=`{all_lead['pvalues'].get('tech_lead_share_lag1', math.nan):.3f}`).",
        f"- Big-firm `LowCredibility` on tech leadership share: `{big_lead['params'].get('tech_lead_share_lag1', math.nan):.4f}{_stars(big_lead['pvalues'].get('tech_lead_share_lag1'))}` (p=`{big_lead['pvalues'].get('tech_lead_share_lag1', math.nan):.3f}`).",
        "",
        "## Placement",
        "",
        "- Best use: governance-capability appendix table or internet-appendix robustness result.",
        "- Suggested framing: boards with more genuine technical human capital are directionally less likely to oversee low-credibility AI disclosure, but the result is supportive rather than decisive.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_result_notes(path: Path, rows: list[dict[str, object]]) -> None:
    lines = [
        "# Result Notes: Test 27 board technical human capital and low-credibility AI disclosure",
        "",
        "This packet links lagged BoardEx-derived board technical human capital to later low-credibility AI disclosure in the AI-talking sample.",
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
    company_map = _pull_company_map(args.dotenv_path, sorted(panel["ticker"].dropna().unique().tolist()))
    board_roles = _pull_board_roles(
        args.dotenv_path,
        sorted(company_map["companyid"].dropna().astype(int).unique().tolist()),
    )
    active_board, active_summary = _prepare_active_board(panel, company_map, board_roles)
    director_ids = sorted(active_board["directorid"].dropna().astype(int).unique().tolist())
    emp = _pull_director_emp(args.dotenv_path, director_ids)
    education = _pull_director_education(args.dotenv_path, director_ids)
    human_cap, hc_summary = _prepare_human_capital(emp, education)
    sample, sample_summary = _prepare_sample(panel, active_board, human_cap)
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

    _write_docx(docx_path, table_df, active_summary, hc_summary, sample_summary)
    _write_figure(rows, png_path=png_path, pdf_path=pdf_path)
    _write_writer_packet(writer_path, sample_summary, hc_summary, keyed)
    _write_result_notes(notes_path, rows)
    tex_path.write_text(latex, encoding="utf-8")
    csv_path.write_text(table_df.to_csv(index=False), encoding="utf-8")
    md_path.write_text(markdown, encoding="utf-8")

    for source_path, subdir in [
        (docx_path, "docx"),
        (tex_path, "latex"),
        (csv_path, "tables"),
        (png_path, "figures"),
        (writer_path, "writer_packets"),
        (notes_path, "snippets"),
    ]:
        shutil.copy2(source_path, args.paper_root / subdir / source_path.name)

    manifest = {
        "test_id": TEST_ID,
        "module_path": MODULE_PATH,
        "run_id": args.run_id,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "inputs": {
            "annual_panel": str(args.annual_panel),
            "boardex_source": [
                "boardex.na_wrds_company_names",
                "boardex.na_company_profile_stocks",
                "boardex.na_wrds_org_composition",
                "boardex.na_dir_profile_emp",
                "boardex.na_dir_profile_education",
            ],
        },
        "sample_summary": {**active_summary, **hc_summary, **sample_summary},
        "outputs": {
            "docx": str(docx_path),
            "latex": str(tex_path),
            "csv": str(csv_path),
            "figure_png": str(png_path),
            "figure_pdf": str(pdf_path),
            "writer_packet": str(writer_path),
            "result_notes": str(notes_path),
        },
    }
    (run_root / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
