"""Publication run driver for Test 29: SEC AI-washing enforcement DID."""

from __future__ import annotations

import argparse
import json
import math
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

from docx import Document
import matplotlib.pyplot as plt
import pandas as pd

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
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_2/test_runs/test_29_sec_ai_washing_enforcement_did"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated/v3_2"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_aiw_v3_2_test_29_sec_ai_washing_enforcement_did_main_v1"
TEST_ID = "test_29_sec_ai_washing_enforcement_did"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.test_29_sec_ai_washing_enforcement_did"

TREATMENT_YEAR = 2022
PLACEBO_YEAR = 2023
POST_START = 2024
ANALYSIS_YEARS = (2021, 2025)
PRELOAD_START = 2020
EVENT_YEARS = [2021, 2023, 2024, 2025]  # 2022 omitted as baseline
CONTROL_SPECS = ["ln_assets_l1", "cash_l1", "leverage_l1", "roa_l1"]
MAIN_TREATMENT = ("treat_patent_mismatch_2022", "Mismatch in 2022")
ALT_TREATMENTS: list[tuple[str, str]] = [
    ("treat_low_credibility_2022", "LowCredibility in 2022"),
    ("treat_application_mismatch_2022", "ApplicationMismatch in 2022"),
]
MAIN_OUTCOMES: list[tuple[str, str]] = [
    ("SpecShare", "Speculative share"),
    ("A_S", "A/S ratio"),
    ("PatentMismatch", "PatentMismatch"),
    ("AI_Focus", "AI Focus"),
]
ALT_PANEL_OUTCOMES: list[tuple[str, str]] = [
    ("SpecShare", "SpecShare DID"),
    ("A_S", "A/S DID"),
    ("PatentMismatch", "PatentMismatch DID"),
]
FIGURE_OUTCOMES: list[tuple[str, str]] = [
    ("SpecShare", "Speculative share"),
    ("A_S", "A/S ratio"),
    ("PatentMismatch", "PatentMismatch"),
]


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


def _load_panel(path: Path) -> pd.DataFrame:
    panel = pd.read_parquet(path).copy()
    panel = _add_construct_variants(panel)
    panel["cik"] = panel["cik"].astype(str)
    panel["year"] = pd.to_numeric(panel["year"], errors="coerce").astype("Int64")
    for column in [
        "any_ai_talk",
        "AI_Focus",
        "A_S",
        "SpecShare",
        "PatentMismatch",
        "LowCredibility",
        "ApplicationMismatch",
        "ln_assets",
        "cash",
        "leverage",
        "roa",
    ]:
        if column in panel.columns:
            panel[column] = pd.to_numeric(panel[column], errors="coerce")
    panel = panel.sort_values(["cik", "year"]).reset_index(drop=True)
    for control in ["ln_assets", "cash", "leverage", "roa"]:
        panel[f"{control}_l1"] = panel.groupby("cik")[control].shift(1)
    panel = panel.loc[panel["year"].between(PRELOAD_START, ANALYSIS_YEARS[1], inclusive="both")].copy()
    panel["post_enforcement"] = panel["year"].ge(POST_START).astype(int)
    return panel


def _build_treatment_panel(panel: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    base = panel.loc[
        panel["year"].eq(TREATMENT_YEAR) & panel["any_ai_talk"].fillna(0).astype(int).eq(1)
    ].copy()
    base = base.loc[
        :,
        [
            "cik",
            "PatentMismatch",
            "LowCredibility",
            "ApplicationMismatch",
            "AI_Focus",
            "SpecShare",
            "A_S",
        ],
    ].copy()
    base["treat_patent_mismatch_2022"] = base["PatentMismatch"].fillna(0).astype(int)
    base["treat_low_credibility_2022"] = base["LowCredibility"].fillna(0).astype(int)
    base["treat_application_mismatch_2022"] = base["ApplicationMismatch"].fillna(0).astype(int)
    treat_cols = [MAIN_TREATMENT[0], *[item[0] for item in ALT_TREATMENTS]]
    treat_frame = base[["cik", *treat_cols]].drop_duplicates(subset=["cik"])

    sample = panel.merge(treat_frame, on="cik", how="inner", validate="many_to_one")
    sample = sample.loc[sample["year"].between(*ANALYSIS_YEARS, inclusive="both")].copy()
    sample = sample.sort_values(["cik", "year"]).reset_index(drop=True)
    sample["event_year"] = pd.to_numeric(sample["year"], errors="coerce").astype(int)

    summary = {
        "treatment_year": TREATMENT_YEAR,
        "placebo_year": PLACEBO_YEAR,
        "post_start": POST_START,
        "treated_firms_main": int(treat_frame[MAIN_TREATMENT[0]].sum()),
        "treated_firms_low_cred": int(treat_frame[ALT_TREATMENTS[0][0]].sum()),
        "treated_firms_application": int(treat_frame[ALT_TREATMENTS[1][0]].sum()),
        "analysis_firms": int(sample["cik"].nunique()),
        "analysis_rows": int(len(sample)),
        "analysis_years": [int(sample["year"].min()), int(sample["year"].max())],
    }
    return sample, summary


def _fit_did_row(sample: pd.DataFrame, outcome: str, treatment_col: str) -> dict[str, object]:
    term = f"{treatment_col}_x_post"
    use = sample.copy()
    use[term] = pd.to_numeric(use[treatment_col], errors="coerce").astype(int) * pd.to_numeric(
        use["post_enforcement"], errors="coerce"
    ).astype(int)
    needed = [outcome, treatment_col, term, "cik", "year", *CONTROL_SPECS]
    use = use.dropna(subset=needed).copy()
    if use.empty or use[term].nunique(dropna=True) < 2:
        return {
            "outcome": outcome,
            "nobs": 0,
            "outcome_mean": math.nan,
            "params": {},
            "bse": {},
            "pvalues": {},
        }
    result, est_sample, adj_r2 = _fit_absorbed_ols(
        use,
        dependent=outcome,
        rhs_terms=[term],
        absorb_col="cik",
        include_year=True,
        controls=CONTROL_SPECS,
    )
    return {
        "outcome": outcome,
        "nobs": int(result.nobs),
        "outcome_mean": float(est_sample[outcome].mean()),
        "params": result.params.to_dict(),
        "bse": result.bse.to_dict(),
        "pvalues": result.pvalues.to_dict(),
        "adj_r2": adj_r2,
    }


def _fit_event_study_row(sample: pd.DataFrame, outcome: str, treatment_col: str) -> dict[str, object]:
    use = sample.dropna(subset=[outcome, treatment_col, "cik", "year", *CONTROL_SPECS]).copy()
    use[treatment_col] = pd.to_numeric(use[treatment_col], errors="coerce").astype(int)
    rhs_terms: list[str] = []
    for year in EVENT_YEARS:
        term = f"{treatment_col}_x_{year}"
        use[term] = use[treatment_col] * use["year"].eq(year).astype(int)
        rhs_terms.append(term)
    if use.empty or not any(use[term].nunique(dropna=True) > 1 for term in rhs_terms):
        return {
            "outcome": outcome,
            "nobs": 0,
            "params": {},
            "bse": {},
            "pvalues": {},
        }
    result, _est_sample, _adj_r2 = _fit_absorbed_ols(
        use,
        dependent=outcome,
        rhs_terms=rhs_terms,
        absorb_col="cik",
        include_year=True,
        controls=CONTROL_SPECS,
    )
    return {
        "outcome": outcome,
        "nobs": int(result.nobs),
        "params": result.params.to_dict(),
        "bse": result.bse.to_dict(),
        "pvalues": result.pvalues.to_dict(),
    }


def _build_results(sample: pd.DataFrame) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    did_rows: list[dict[str, object]] = []
    event_rows: list[dict[str, object]] = []
    for outcome, outcome_label in MAIN_OUTCOMES:
        did = _fit_did_row(sample, outcome, MAIN_TREATMENT[0])
        did["outcome_label"] = outcome_label
        did["treatment_col"] = MAIN_TREATMENT[0]
        did_rows.append(did)

        event = _fit_event_study_row(sample, outcome, MAIN_TREATMENT[0])
        event["outcome_label"] = outcome_label
        event_rows.append(event)
    for treatment_col, treatment_label in ALT_TREATMENTS:
        for outcome, outcome_label in ALT_PANEL_OUTCOMES:
            did = _fit_did_row(sample, outcome, treatment_col)
            did["outcome_label"] = outcome_label
            did["treatment_col"] = treatment_col
            did["treatment_label"] = treatment_label
            did_rows.append(did)
    return did_rows, event_rows


def _build_table(
    did_rows: list[dict[str, object]],
    event_rows: list[dict[str, object]],
    sample_summary: dict[str, object],
) -> tuple[pd.DataFrame, dict[tuple[str, str], dict[str, object]], dict[str, dict[str, object]]]:
    did_keyed = {(row["treatment_col"], row["outcome"]): row for row in did_rows}
    event_keyed = {row["outcome"]: row for row in event_rows}
    table_rows: list[dict[str, object]] = [
        {
            "Panel": "Panel A. Enforcement-salience DID using mismatch exposure in 2022",
            "Outcome / treatment": "",
            "Post-2024 DID": "",
            "2023 placebo": "",
            "Outcome mean": "",
            "Observations": "",
        }
    ]
    for outcome, outcome_label in MAIN_OUTCOMES:
        did_row = did_keyed[(MAIN_TREATMENT[0], outcome)]
        event_row = event_keyed[outcome]
        placebo_term = f"{MAIN_TREATMENT[0]}_x_{PLACEBO_YEAR}"
        post_term = f"{MAIN_TREATMENT[0]}_x_post"
        table_rows.append(
            {
                "Panel": "",
                "Outcome / treatment": outcome_label,
                "Post-2024 DID": _coef_cell(
                    did_row["params"].get(post_term),
                    did_row["bse"].get(post_term),
                    did_row["pvalues"].get(post_term),
                ),
                "2023 placebo": _coef_cell(
                    event_row["params"].get(placebo_term),
                    event_row["bse"].get(placebo_term),
                    event_row["pvalues"].get(placebo_term),
                ),
                "Outcome mean": (
                    f"{did_row['outcome_mean']:.3f}" if math.isfinite(did_row["outcome_mean"]) else ""
                ),
                "Observations": str(did_row["nobs"]),
            }
        )
    table_rows.append(
        {
            "Panel": "Panel B. Alternative exposure definitions on core disclosure outcomes",
            "Outcome / treatment": "",
            "Post-2024 DID": "",
            "2023 placebo": "",
            "Outcome mean": "",
            "Observations": "",
        }
    )
    for treatment_col, treatment_label in ALT_TREATMENTS:
        spec_row = did_keyed[(treatment_col, "SpecShare")]
        as_row = did_keyed[(treatment_col, "A_S")]
        mismatch_row = did_keyed[(treatment_col, "PatentMismatch")]
        table_rows.append(
            {
                "Panel": "",
                "Outcome / treatment": treatment_label,
                "Post-2024 DID": _coef_cell(
                    spec_row["params"].get(f"{treatment_col}_x_post"),
                    spec_row["bse"].get(f"{treatment_col}_x_post"),
                    spec_row["pvalues"].get(f"{treatment_col}_x_post"),
                ),
                "2023 placebo": _coef_cell(
                    as_row["params"].get(f"{treatment_col}_x_post"),
                    as_row["bse"].get(f"{treatment_col}_x_post"),
                    as_row["pvalues"].get(f"{treatment_col}_x_post"),
                ),
                "Outcome mean": _coef_cell(
                    mismatch_row["params"].get(f"{treatment_col}_x_post"),
                    mismatch_row["bse"].get(f"{treatment_col}_x_post"),
                    mismatch_row["pvalues"].get(f"{treatment_col}_x_post"),
                ),
                "Observations": str(sample_summary[f"treated_firms_{'low_cred' if 'low_credibility' in treatment_col else 'application'}"]),
            }
        )
    table_df = pd.DataFrame(table_rows)
    return table_df, did_keyed, event_keyed


def _render_markdown(table_df: pd.DataFrame) -> str:
    headers = table_df.columns.tolist()
    rows = [[str(value) for value in row] for row in table_df.values.tolist()]
    return to_markdown_table(headers, rows)


def _render_latex(table_df: pd.DataFrame) -> str:
    lines = [
        "\\begin{table}[!htbp]",
        "\\centering",
        "\\caption{SEC AI-washing enforcement salience and disclosure cleanup}",
        "\\small",
        "\\begin{tabular}{llccc}",
        "\\hline",
        "Panel & Outcome / treatment & Post-2024 DID & 2023 placebo & Mean / treated \\\\",
        "\\hline",
    ]
    for _, row in table_df.iterrows():
        if row["Panel"]:
            lines.append("\\multicolumn{5}{l}{\\textit{" + str(row["Panel"]).replace("&", "\\&") + "}} \\\\")
            continue
        lines.append(
            " & ".join(
                [
                    "",
                    str(row["Outcome / treatment"]).replace("_", "\\_"),
                    str(row["Post-2024 DID"]),
                    str(row["2023 placebo"]),
                    str(row["Outcome mean"]),
                ]
            )
            + " \\\\",
        )
    lines.extend(
        [
            "\\hline",
            "\\end{tabular}",
            "\\begin{flushleft}",
            "\\footnotesize Notes: Treatment is fixed using firms that talk about AI in 2022 and are flagged as mismatch, low-credibility, or application-mismatch in that year. The post period is 2024--2025, after the SEC's March 18, 2024 AI-washing enforcement actions. Panel A reports the main treatment's post-2024 DID and the 2023 placebo coefficient from the event-time specification. Panel B reports post-2024 DID coefficients for alternative treatment definitions on speculative share, A/S, and PatentMismatch, in that order. All specifications absorb firm and year fixed effects, include lagged controls, and cluster standard errors by firm.",
            "\\end{flushleft}",
            "\\end{table}",
        ]
    )
    return "\n".join(lines) + "\n"


def _write_docx(path: Path, table_df: pd.DataFrame, sample_summary: dict[str, object]) -> None:
    document = Document()
    _set_document_defaults(document)
    _set_landscape(document)
    _add_title(document, "Test 29. SEC AI-washing enforcement salience DID")
    _add_note(
        document,
        (
            "This table asks whether firms already exposed to low-credibility AI disclosure risk before 2024 "
            "shift their disclosure composition after the SEC's March 18, 2024 AI-washing enforcement actions and related public statements."
        ),
    )
    _add_note(
        document,
        (
            f"Treatment is fixed using 2022 AI-talking firms. Main treated firms = {sample_summary['treated_firms_main']:,}; "
            f"low-credibility treated firms = {sample_summary['treated_firms_low_cred']:,}; "
            f"application-mismatch treated firms = {sample_summary['treated_firms_application']:,}."
        ),
    )
    _add_note(
        document,
        (
            f"Analysis sample = {sample_summary['analysis_rows']:,} firm-years across {sample_summary['analysis_firms']:,} firms over "
            f"{sample_summary['analysis_years'][0]}-{sample_summary['analysis_years'][1]}."
        ),
    )
    headers = table_df.columns.tolist()
    rows = [[(str(value), False) for value in row] for row in table_df.values.tolist()]
    _build_panel_table(document, headers, rows)
    document.save(path)


def _write_figure(event_rows: list[dict[str, object]], *, png_path: Path, pdf_path: Path) -> None:
    _base_style()
    fig, axes = plt.subplots(1, len(FIGURE_OUTCOMES), figsize=(11.6, 3.8), sharex=True)
    if len(FIGURE_OUTCOMES) == 1:
        axes = [axes]
    for ax, (outcome, outcome_label) in zip(axes, FIGURE_OUTCOMES, strict=True):
        row = next(item for item in event_rows if item["outcome"] == outcome)
        x = EVENT_YEARS
        coef = [row["params"].get(f"{MAIN_TREATMENT[0]}_x_{year}", math.nan) for year in x]
        err = [1.96 * row["bse"].get(f"{MAIN_TREATMENT[0]}_x_{year}", math.nan) for year in x]
        ax.errorbar(x, coef, yerr=err, fmt="o-", capsize=3, color="#1f4e79")
        ax.axhline(0, color="black", linewidth=0.9, linestyle="--")
        ax.axvline(2023.5, color="#8b0000", linewidth=1.0, linestyle=":")
        ax.set_xticks(EVENT_YEARS)
        ax.set_title(outcome_label)
        ax.set_ylabel("Treated-control gap vs. 2022")
    fig.suptitle("SEC AI-washing enforcement salience event path", y=1.02, fontsize=12)
    fig.tight_layout()
    fig.savefig(png_path, dpi=220, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)


def _write_writer_packet(
    path: Path,
    sample_summary: dict[str, object],
    did_keyed: dict[tuple[str, str], dict[str, object]],
    event_keyed: dict[str, dict[str, object]],
) -> None:
    main_spec = did_keyed[(MAIN_TREATMENT[0], "SpecShare")]
    main_as = did_keyed[(MAIN_TREATMENT[0], "A_S")]
    main_mismatch = did_keyed[(MAIN_TREATMENT[0], "PatentMismatch")]
    placebo_spec = event_keyed["SpecShare"]
    lines = [
        "# Writer Packet: Test 29 SEC AI-washing enforcement salience DID",
        "",
        "## Setup",
        "",
        "- Event anchor: SEC AI-washing enforcement actions and related public salience on March 18, 2024.",
        f"- Treatment is fixed in {TREATMENT_YEAR} using firms that talk about AI and are flagged as mismatch before the enforcement shock.",
        "- Main outcomes: SpecShare, A/S ratio, PatentMismatch, and AI Focus.",
        "",
        "## Density",
        "",
        f"- Analysis rows: `{sample_summary['analysis_rows']:,}` across `{sample_summary['analysis_firms']:,}` firms.",
        f"- Main treated firms: `{sample_summary['treated_firms_main']:,}`.",
        f"- Alternative-treatment firms: low-credibility=`{sample_summary['treated_firms_low_cred']:,}`, application-mismatch=`{sample_summary['treated_firms_application']:,}`.",
        "",
        "## Main read",
        "",
        f"- Post-2024 DID on SpecShare: `{main_spec['params'].get(MAIN_TREATMENT[0] + '_x_post', math.nan):.4f}{_stars(main_spec['pvalues'].get(MAIN_TREATMENT[0] + '_x_post'))}` (p=`{main_spec['pvalues'].get(MAIN_TREATMENT[0] + '_x_post', math.nan):.3f}`).",
        f"- Post-2024 DID on A/S ratio: `{main_as['params'].get(MAIN_TREATMENT[0] + '_x_post', math.nan):.4f}{_stars(main_as['pvalues'].get(MAIN_TREATMENT[0] + '_x_post'))}` (p=`{main_as['pvalues'].get(MAIN_TREATMENT[0] + '_x_post', math.nan):.3f}`).",
        f"- Post-2024 DID on PatentMismatch: `{main_mismatch['params'].get(MAIN_TREATMENT[0] + '_x_post', math.nan):.4f}{_stars(main_mismatch['pvalues'].get(MAIN_TREATMENT[0] + '_x_post'))}` (p=`{main_mismatch['pvalues'].get(MAIN_TREATMENT[0] + '_x_post', math.nan):.3f}`).",
        f"- 2023 placebo on SpecShare from the event path: `{placebo_spec['params'].get(MAIN_TREATMENT[0] + '_x_2023', math.nan):.4f}{_stars(placebo_spec['pvalues'].get(MAIN_TREATMENT[0] + '_x_2023'))}` (p=`{placebo_spec['pvalues'].get(MAIN_TREATMENT[0] + '_x_2023', math.nan):.3f}`).",
        "",
        "## Interpretation discipline",
        "",
        "- Best reading: the 2024 SEC enforcement salience is followed by further cleanup in disclosure composition among pre-exposed firms.",
        "- Important caveat: the 2023 placebo year is already directional for some outcomes, so this is better framed as a policy-salience or acceleration result than as a clean causal enforcement estimate.",
        "",
        "## Placement",
        "",
        "- Best use: high appendix or supporting regulatory-salience extension in the main text if Packet D remains important to the paper's external-discipline story.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_result_notes(
    path: Path,
    did_keyed: dict[tuple[str, str], dict[str, object]],
    event_keyed: dict[str, dict[str, object]],
) -> None:
    lines = [
        "# Result Notes: Test 29 SEC AI-washing enforcement salience DID",
        "",
        "This packet uses the SEC's March 18, 2024 AI-washing enforcement actions as a public-salience shock and fixes treatment using 2022 pre-shock exposure.",
        "",
        "## Panel A. Main treatment DID",
    ]
    for outcome, outcome_label in MAIN_OUTCOMES:
        did = did_keyed[(MAIN_TREATMENT[0], outcome)]
        event = event_keyed[outcome]
        post_term = f"{MAIN_TREATMENT[0]}_x_post"
        placebo_term = f"{MAIN_TREATMENT[0]}_x_{PLACEBO_YEAR}"
        lines.extend(
            [
                f"### {outcome_label}",
                f"- Post-2024 DID: `{did['params'].get(post_term, math.nan):.4f}` (SE `{did['bse'].get(post_term, math.nan):.4f}`, p=`{did['pvalues'].get(post_term, math.nan):.3f}`, n=`{did['nobs']}`).",
                f"- 2023 placebo: `{event['params'].get(placebo_term, math.nan):.4f}` (SE `{event['bse'].get(placebo_term, math.nan):.4f}`, p=`{event['pvalues'].get(placebo_term, math.nan):.3f}`).",
            ]
        )
    lines.extend(["", "## Panel B. Alternative treatments"])
    for treatment_col, treatment_label in ALT_TREATMENTS:
        lines.append(f"### {treatment_label}")
        for outcome, outcome_label in ALT_PANEL_OUTCOMES:
            did = did_keyed[(treatment_col, outcome)]
            term = f"{treatment_col}_x_post"
            lines.append(
                f"- {outcome_label}: `{did['params'].get(term, math.nan):.4f}` (SE `{did['bse'].get(term, math.nan):.4f}`, p=`{did['pvalues'].get(term, math.nan):.3f}`, n=`{did['nobs']}`)."
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = _parse_args()
    run_root = args.test_root / args.run_id
    run_root.mkdir(parents=True, exist_ok=True)
    for subdir in ["docx", "latex", "tables", "figures", "writer_packets", "snippets"]:
        (args.paper_root / subdir).mkdir(parents=True, exist_ok=True)

    panel = _load_panel(args.annual_panel)
    sample, sample_summary = _build_treatment_panel(panel)
    did_rows, event_rows = _build_results(sample)
    table_df, did_keyed, event_keyed = _build_table(did_rows, event_rows, sample_summary)

    stem = f"{TEST_ID}_{args.run_id}"
    docx_path = run_root / f"{stem}.docx"
    latex_path = run_root / f"{stem}.tex"
    csv_path = run_root / f"{stem}.csv"
    png_path = run_root / f"{stem}.png"
    pdf_path = run_root / f"{stem}.pdf"
    writer_packet_path = run_root / f"{stem}_writer_packet.md"
    result_notes_path = run_root / f"{stem}_result_notes.md"
    event_csv_path = run_root / f"{stem}_event_series.csv"

    markdown = _render_markdown(table_df)
    latex = _render_latex(table_df)
    table_df.to_csv(csv_path, index=False)
    latex_path.write_text(latex, encoding="utf-8")
    _write_docx(docx_path, table_df, sample_summary)
    _write_figure(event_rows, png_path=png_path, pdf_path=pdf_path)
    _write_writer_packet(writer_packet_path, sample_summary, did_keyed, event_keyed)
    _write_result_notes(result_notes_path, did_keyed, event_keyed)

    event_export_rows: list[dict[str, object]] = []
    for row in event_rows:
        for year in EVENT_YEARS:
            term = f"{MAIN_TREATMENT[0]}_x_{year}"
            event_export_rows.append(
                {
                    "outcome": row["outcome"],
                    "outcome_label": row["outcome_label"],
                    "year": year,
                    "coef": row["params"].get(term),
                    "se": row["bse"].get(term),
                    "p_value": row["pvalues"].get(term),
                    "nobs": row["nobs"],
                }
            )
    pd.DataFrame(event_export_rows).to_csv(event_csv_path, index=False)

    copy_map = {
        docx_path: "docx",
        latex_path: "latex",
        csv_path: "tables",
        png_path: "figures",
        writer_packet_path: "writer_packets",
        result_notes_path: "snippets",
    }
    for source_path, subdir in copy_map.items():
        shutil.copy2(source_path, args.paper_root / subdir / source_path.name)

    manifest = {
        "test_id": TEST_ID,
        "module_path": MODULE_PATH,
        "run_id": args.run_id,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "inputs": {
            "annual_panel": str(args.annual_panel),
            "sec_event_date": "2024-03-18",
            "sec_event_release": "https://www.sec.gov/newsroom/press-releases/2024-36",
            "sec_event_speech": "https://www.sec.gov/newsroom/speeches-statements/sec-chair-gary-gensler-ai-washing",
        },
        "sample_summary": sample_summary,
        "did_rows": did_rows,
        "event_rows": event_rows,
        "outputs": {
            "docx": str(docx_path),
            "latex": str(latex_path),
            "csv": str(csv_path),
            "figure_png": str(png_path),
            "figure_pdf": str(pdf_path),
            "writer_packet": str(writer_packet_path),
            "result_notes": str(result_notes_path),
            "event_series_csv": str(event_csv_path),
            "markdown_preview": markdown,
        },
    }
    (run_root / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
