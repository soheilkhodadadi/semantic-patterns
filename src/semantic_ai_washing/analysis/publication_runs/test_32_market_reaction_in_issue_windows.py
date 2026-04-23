"""Publication run driver for Test 32: market reactions in capital-raising windows."""

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
import statsmodels.formula.api as smf

from semantic_ai_washing.analysis.delivery_table_payloads import to_markdown_table
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
DEFAULT_EVENT_PANEL = (
    REPO_ROOT
    / "data/processed/panel/filing_event_estimation_sample_hybrid_api_a_conf49_v1.parquet"
)
DEFAULT_TEST_ROOT = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_2/test_runs/test_32_market_reaction_in_issue_windows"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated/v3_2"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_aiw_v3_2_test_32_market_reaction_in_issue_windows_main_v1"
TEST_ID = "test_32_market_reaction_in_issue_windows"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.test_32_market_reaction_in_issue_windows"

SUBSET_SPECS: list[tuple[str, str]] = [
    ("all", "Panel A. Filing-year market reactions in all issue-eligible firms"),
    ("nonbig", "Panel B. Filing-year market reactions in non-big firms"),
]
PREDICTOR_SPECS: list[tuple[str, str]] = [
    ("PatentMismatch", "PatentMismatch × IssueWindow"),
    ("LowCredibility", "LowCredibility × IssueWindow"),
    ("ApplicationMismatch", "ApplicationMismatch × IssueWindow"),
]
OUTCOME_SPECS: list[tuple[str, str]] = [
    ("car_m1_p1", "CAR[-1,+1]"),
    ("bhar_3m", "BHAR[+2,+63]"),
    ("bhar_12m", "BHAR[+2,+252]"),
]
CONTROL_SPECS = ["AI_Focus", "ln_assets", "cash", "leverage", "roa"]
VALID_ISSUE_YEARS = (2016, 2023)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annual-panel", type=Path, default=DEFAULT_ANNUAL_PANEL)
    parser.add_argument("--event-panel", type=Path, default=DEFAULT_EVENT_PANEL)
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


def _load_annual_issue_panel(path: Path) -> tuple[pd.DataFrame, dict[str, object]]:
    panel = pd.read_parquet(path).copy()
    panel = _add_construct_variants(panel)
    panel["cik"] = panel["cik"].astype(str)
    panel["year"] = pd.to_numeric(panel["year"], errors="coerce").astype(int)
    for column in [
        "PatentMismatch",
        "LowCredibility",
        "ApplicationMismatch",
        "A_S",
        "AI_Focus",
        "ln_assets",
        "cash",
        "leverage",
        "roa",
        "market_cap_year_end",
        "shrout",
    ]:
        if column in panel.columns:
            panel[column] = pd.to_numeric(panel[column], errors="coerce")
    yearly_median_market_cap = panel.groupby("year")["market_cap_year_end"].transform("median")
    panel["nonbig"] = panel["market_cap_year_end"].le(yearly_median_market_cap)
    panel = panel.sort_values(["permno", "year", "cik"]).reset_index(drop=True)
    shrout_lead1 = panel.groupby("permno", sort=False)["shrout"].shift(-1)
    panel["share_growth_lead1"] = shrout_lead1 / panel["shrout"] - 1.0
    panel["equity_issue_lead1"] = np.where(
        panel["share_growth_lead1"].notna(), (panel["share_growth_lead1"] > 0.05).astype(int), np.nan
    )
    keep = [
        "cik",
        "year",
        "equity_issue_lead1",
        "PatentMismatch",
        "LowCredibility",
        "ApplicationMismatch",
        "A_S",
        "AI_Focus",
        "ln_assets",
        "cash",
        "leverage",
        "roa",
        "nonbig",
    ]
    panel = panel[keep].drop_duplicates(subset=["cik", "year"])
    panel = panel.loc[panel["year"].between(*VALID_ISSUE_YEARS, inclusive="both")].copy()
    summary = {
        "issue_rule": "IssueWindow equals one when next-year CRSP shrout growth exceeds 5%.",
        "annual_issue_rows": int(panel["equity_issue_lead1"].notna().sum()),
        "annual_issue_firms": int(panel.loc[panel["equity_issue_lead1"].eq(1), "cik"].nunique()),
    }
    return panel, summary


def _load_event_panel(path: Path) -> pd.DataFrame:
    events = pd.read_parquet(path).copy()
    events["cik"] = events["cik"].astype(str)
    events["filing_year"] = pd.to_numeric(events["filing_year"], errors="coerce").astype(int)
    agg = (
        events.groupby(["cik", "filing_year"], as_index=False)
        .agg(
            car_m1_p1=("car_m1_p1", "mean"),
            bhar_3m=("bhar_3m", "mean"),
            bhar_12m=("bhar_12m", "mean"),
            filing_events=("filing_id", "count"),
        )
        .sort_values(["cik", "filing_year"])
        .reset_index(drop=True)
    )
    return agg


def _prepare_sample(event_panel: pd.DataFrame, annual_panel: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    sample = event_panel.merge(
        annual_panel,
        left_on=["cik", "filing_year"],
        right_on=["cik", "year"],
        how="inner",
        validate="many_to_one",
    )
    sample = sample.loc[sample["equity_issue_lead1"].notna()].copy()
    summary = {
        "filing_year_rows": int(len(sample)),
        "filing_year_firms": int(sample["cik"].nunique()),
        "issue_window_rows": int(sample["equity_issue_lead1"].eq(1).sum()),
        "issue_window_firms": int(sample.loc[sample["equity_issue_lead1"].eq(1), "cik"].nunique()),
        "nonbig_rows": int(sample["nonbig"].eq(True).sum()),
    }
    return sample, summary


def _subset_sample(sample: pd.DataFrame, subset_key: str) -> pd.DataFrame:
    if subset_key == "all":
        return sample.copy()
    if subset_key == "nonbig":
        return sample.loc[sample["nonbig"].eq(True)].copy()
    raise ValueError(f"Unknown subset: {subset_key}")


def _fit_model(sample: pd.DataFrame, subset_key: str, outcome: str, predictor: str) -> dict[str, object]:
    subset = _subset_sample(sample, subset_key).copy()
    needed = [outcome, predictor, "equity_issue_lead1", "filing_year", "cik", *CONTROL_SPECS]
    use = subset.dropna(subset=needed).copy()
    if use.empty:
        return {
            "subset": subset_key,
            "outcome": outcome,
            "predictor": predictor,
            "nobs": 0,
            "outcome_mean": math.nan,
            "params": {},
            "bse": {},
            "pvalues": {},
        }
    formula = (
        f"{outcome} ~ {predictor} * equity_issue_lead1 + AI_Focus + ln_assets + cash + leverage + roa + C(filing_year)"
    )
    result = smf.ols(formula, data=use).fit(cov_type="cluster", cov_kwds={"groups": use["cik"]})
    return {
        "subset": subset_key,
        "outcome": outcome,
        "predictor": predictor,
        "nobs": int(result.nobs),
        "outcome_mean": float(use[outcome].mean()),
        "params": result.params.to_dict(),
        "bse": result.bse.to_dict(),
        "pvalues": result.pvalues.to_dict(),
    }


def _build_table(rows: list[dict[str, object]]) -> tuple[pd.DataFrame, dict[tuple[str, str, str], dict[str, object]]]:
    keyed = {(row["subset"], row["outcome"], row["predictor"]): row for row in rows}
    table_rows: list[dict[str, object]] = []
    for subset_key, panel_label in SUBSET_SPECS:
        table_rows.append(
            {
                "Panel": panel_label,
                "Outcome": "",
                "PatentMismatch × IssueWindow": "",
                "LowCredibility × IssueWindow": "",
                "ApplicationMismatch × IssueWindow": "",
                "Baseline mismatch": "",
                "IssueWindow": "",
                "Outcome mean": "",
                "Obs.": "",
            }
        )
        for outcome, outcome_label in OUTCOME_SPECS:
            row = {"Panel": "", "Outcome": outcome_label}
            for predictor, predictor_label in PREDICTOR_SPECS:
                result = keyed[(subset_key, outcome, predictor)]
                interaction_term = f"{predictor}:equity_issue_lead1"
                if interaction_term not in result["params"]:
                    interaction_term = f"equity_issue_lead1:{predictor}"
                row[predictor_label] = _coef_cell(
                    result["params"].get(interaction_term),
                    result["bse"].get(interaction_term),
                    result["pvalues"].get(interaction_term),
                )
            base = keyed[(subset_key, outcome, "PatentMismatch")]
            row["Baseline mismatch"] = _coef_cell(
                base["params"].get("PatentMismatch"),
                base["bse"].get("PatentMismatch"),
                base["pvalues"].get("PatentMismatch"),
            )
            row["IssueWindow"] = _coef_cell(
                base["params"].get("equity_issue_lead1"),
                base["bse"].get("equity_issue_lead1"),
                base["pvalues"].get("equity_issue_lead1"),
            )
            row["Outcome mean"] = f"{base['outcome_mean']:.3f}" if math.isfinite(base["outcome_mean"]) else ""
            row["Obs."] = str(base["nobs"])
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
        "\\caption{Market reactions in capital-raising windows}",
        "\\small",
        "\\begin{tabular}{llccccrrr}",
        "\\hline",
        "Panel & Outcome & PM $\\times$ Issue & LowCred $\\times$ Issue & AppMismatch $\\times$ Issue & Baseline PM & IssueWindow & Mean & Obs. \\\\",
        "\\hline",
    ]
    for _, row in table_df.iterrows():
        if row["Panel"]:
            lines.append("\\multicolumn{9}{l}{\\textit{" + str(row["Panel"]).replace("&", "\\&") + "}} \\\\")
            continue
        lines.append(
            " & ".join(
                [
                    "",
                    str(row["Outcome"]).replace("_", "\\_"),
                    str(row["PatentMismatch × IssueWindow"]),
                    str(row["LowCredibility × IssueWindow"]),
                    str(row["ApplicationMismatch × IssueWindow"]),
                    str(row["Baseline mismatch"]),
                    str(row["IssueWindow"]),
                    str(row["Outcome mean"]),
                    str(row["Obs."]),
                ]
            )
            + " \\\\",
        )
    lines.extend(
        [
            "\\hline",
            "\\end{tabular}",
            "\\begin{flushleft}",
            "\\footnotesize Notes: The event sample is collapsed to one filing-year return observation per firm-year and linked to the annual issue-window flag from Test 30. IssueWindow equals one when next-year CRSP shares-outstanding growth exceeds 5\\%. Coefficients shown for the three main construct columns are the interaction terms between the disclosure metric and IssueWindow. The Baseline PM column reports the PatentMismatch coefficient outside issue windows, and the IssueWindow column reports the level issue-window coefficient in the canonical specification. All regressions include filing-year fixed effects, annual controls, and firm-clustered standard errors.",
            "\\end{flushleft}",
            "\\end{table}",
        ]
    )
    return "\n".join(lines) + "\n"


def _write_docx(path: Path, table_df: pd.DataFrame, annual_summary: dict[str, object], sample_summary: dict[str, object]) -> None:
    document = Document()
    _set_document_defaults(document)
    _set_landscape(document)
    _add_title(document, "Test 32. Market reactions in capital-raising windows")
    _add_note(
        document,
        (
            "This table asks whether filing-year market reactions look different when firms are in capital-raising windows. "
            "The issue-window flag is imported from the annual panel and linked to the filing-event sample at the firm-year level."
        ),
    )
    _add_note(
        document,
        (
            f"Issue-window rule: {annual_summary['issue_rule']} Issue-eligible filing-year rows = {sample_summary['filing_year_rows']:,}; "
            f"issue-window rows = {sample_summary['issue_window_rows']:,}."
        ),
    )
    headers = table_df.columns.tolist()
    rows = [[(str(value), False) for value in row] for row in table_df.values.tolist()]
    _build_panel_table(document, headers, rows)
    document.save(path)


def _write_figure(rows: list[dict[str, object]], *, png_path: Path, pdf_path: Path) -> None:
    _base_style()
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.0), sharey=True)
    outcome_order = [label for _outcome, label in OUTCOME_SPECS]
    for ax, (predictor, predictor_label) in zip(axes, PREDICTOR_SPECS[:2], strict=True):
        plot_rows = [row for row in rows if row['predictor'] == predictor]
        for subset_key, subset_label in SUBSET_SPECS:
            subset_rows = [row for row in plot_rows if row['subset'] == subset_key]
            subset_rows = sorted(subset_rows, key=lambda row: outcome_order.index(dict(OUTCOME_SPECS)[row['outcome']]))
            x = np.arange(len(subset_rows))
            term = f"{predictor}:equity_issue_lead1"
            if term not in subset_rows[0]['params']:
                term = f"equity_issue_lead1:{predictor}"
            coef = [row['params'].get(term, math.nan) for row in subset_rows]
            err = [1.96 * row['bse'].get(term, math.nan) for row in subset_rows]
            ax.errorbar(x, coef, yerr=err, fmt='o-', capsize=3, label=subset_label.replace('Panel ', ''))
        ax.axhline(0, color='black', linewidth=0.9, linestyle='--')
        ax.set_xticks(x, outcome_order, rotation=20, ha='right')
        ax.set_title(predictor_label)
        ax.set_ylabel('Interaction coefficient')
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc='upper center', ncol=2, frameon=False)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(png_path, dpi=220, bbox_inches='tight')
    fig.savefig(pdf_path, bbox_inches='tight')
    plt.close(fig)


def _write_writer_packet(
    path: Path,
    annual_summary: dict[str, object],
    sample_summary: dict[str, object],
    keyed: dict[tuple[str, str, str], dict[str, object]],
) -> None:
    all_bhar = keyed[("all", "bhar_3m", "PatentMismatch")]
    nonbig_bhar = keyed[("nonbig", "bhar_3m", "PatentMismatch")]
    lines = [
        "# Writer Packet: Test 32 market reactions in capital-raising windows",
        "",
        "## Setup",
        "",
        f"- Issue-window rule: {annual_summary['issue_rule']}",
        "- The filing-event sample is collapsed to one firm-year return observation and merged to the annual issue-window flag.",
        "- The key question is whether the return relation for low-credibility AI disclosure changes when financing incentives are salient.",
        "",
        "## Density",
        "",
        f"- Filing-year rows in the merged sample: `{sample_summary['filing_year_rows']:,}` across `{sample_summary['filing_year_firms']:,}` firms.",
        f"- Issue-window rows: `{sample_summary['issue_window_rows']:,}` across `{sample_summary['issue_window_firms']:,}` firms.",
        f"- Non-big rows: `{sample_summary['nonbig_rows']:,}`.",
        "",
        "## Main read",
        "",
        f"- In the full sample, baseline `PatentMismatch` predicts weaker `BHAR[+2,+63]`: `{all_bhar['params'].get('PatentMismatch', math.nan):.4f}` (p=`{all_bhar['pvalues'].get('PatentMismatch', math.nan):.3f}`).",
        f"- But the `PatentMismatch × IssueWindow` interaction for `BHAR[+2,+63]` is positive: `{all_bhar['params'].get('PatentMismatch:equity_issue_lead1', all_bhar['params'].get('equity_issue_lead1:PatentMismatch', math.nan)):.4f}` (p=`{all_bhar['pvalues'].get('PatentMismatch:equity_issue_lead1', all_bhar['pvalues'].get('equity_issue_lead1:PatentMismatch', math.nan)):.3f}`).",
        f"- The same interaction is directionally stronger in non-big firms: `{nonbig_bhar['params'].get('PatentMismatch:equity_issue_lead1', nonbig_bhar['params'].get('equity_issue_lead1:PatentMismatch', math.nan)):.4f}` (p=`{nonbig_bhar['pvalues'].get('PatentMismatch:equity_issue_lead1', nonbig_bhar['pvalues'].get('equity_issue_lead1:PatentMismatch', math.nan)):.3f}`).",
        "",
        "## Interpretation",
        "",
        "- Best reading: the weak post-filing return pattern attached to mismatch is less negative inside financing windows than outside them.",
        "- That is consistent with financing-salience muting or offsetting the broad negative pricing pattern we saw in the full sample.",
        "- This gives the market section a narrower and more defensible interpretation than the earlier broad portfolio tests.",
        "",
        "## Placement",
        "",
        "- Best use: supporting market table if we keep a market section, especially alongside Test 30.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_result_notes(path: Path, rows: list[dict[str, object]]) -> None:
    lines = [
        "# Result Notes: Test 32 market reactions in capital-raising windows",
        "",
        "This packet re-opens the market lane only inside financing-salience windows, using filing-year return outcomes merged to the issue-window indicator from Test 30.",
        "",
    ]
    for subset_key, subset_label in SUBSET_SPECS:
        lines.append(f"## {subset_label}")
        subset_rows = [row for row in rows if row['subset'] == subset_key]
        for outcome, outcome_label in OUTCOME_SPECS:
            lines.append(f"### {outcome_label}")
            for predictor, predictor_label in PREDICTOR_SPECS:
                row = next(item for item in subset_rows if item['outcome'] == outcome and item['predictor'] == predictor)
                term = f"{predictor}:equity_issue_lead1"
                if term not in row['params']:
                    term = f"equity_issue_lead1:{predictor}"
                lines.append(
                    f"- {predictor_label}: `{row['params'].get(term, math.nan):.4f}` (SE `{row['bse'].get(term, math.nan):.4f}`, p=`{row['pvalues'].get(term, math.nan):.3f}`, n=`{row['nobs']}`)."
                )
            base = next(item for item in subset_rows if item['outcome'] == outcome and item['predictor'] == 'PatentMismatch')
            lines.append(
                f"- Baseline PatentMismatch outside issue windows: `{base['params'].get('PatentMismatch', math.nan):.4f}` (p=`{base['pvalues'].get('PatentMismatch', math.nan):.3f}`)."
            )
        lines.append("")
    path.write_text("\n".join(lines), encoding='utf-8')


def main() -> None:
    args = _parse_args()
    run_root = args.test_root / args.run_id
    run_root.mkdir(parents=True, exist_ok=True)
    for subdir in ["docx", "latex", "tables", "figures", "writer_packets", "snippets"]:
        (args.paper_root / subdir).mkdir(parents=True, exist_ok=True)

    annual_panel, annual_summary = _load_annual_issue_panel(args.annual_panel)
    event_panel = _load_event_panel(args.event_panel)
    sample, sample_summary = _prepare_sample(event_panel, annual_panel)

    rows: list[dict[str, object]] = []
    for subset_key, _subset_label in SUBSET_SPECS:
        for outcome, _outcome_label in OUTCOME_SPECS:
            for predictor, _predictor_label in PREDICTOR_SPECS:
                rows.append(_fit_model(sample, subset_key, outcome, predictor))

    table_df, keyed = _build_table(rows)
    stem = f"{TEST_ID}_{args.run_id}"
    docx_path = run_root / f"{stem}.docx"
    latex_path = run_root / f"{stem}.tex"
    csv_path = run_root / f"{stem}.csv"
    png_path = run_root / f"{stem}.png"
    pdf_path = run_root / f"{stem}.pdf"
    writer_packet_path = run_root / f"{stem}_writer_packet.md"
    result_notes_path = run_root / f"{stem}_result_notes.md"

    markdown = _render_markdown(table_df)
    latex = _render_latex(table_df)
    table_df.to_csv(csv_path, index=False)
    latex_path.write_text(latex, encoding='utf-8')
    _write_docx(docx_path, table_df, annual_summary, sample_summary)
    _write_figure(rows, png_path=png_path, pdf_path=pdf_path)
    _write_writer_packet(writer_packet_path, annual_summary, sample_summary, keyed)
    _write_result_notes(result_notes_path, rows)

    copy_map = {
        docx_path: 'docx',
        latex_path: 'latex',
        csv_path: 'tables',
        png_path: 'figures',
        writer_packet_path: 'writer_packets',
        result_notes_path: 'snippets',
    }
    for source_path, subdir in copy_map.items():
        shutil.copy2(source_path, args.paper_root / subdir / source_path.name)

    manifest = {
        'test_id': TEST_ID,
        'module_path': MODULE_PATH,
        'run_id': args.run_id,
        'generated_at_utc': datetime.now(UTC).isoformat(),
        'inputs': {
            'annual_panel': str(args.annual_panel),
            'event_panel': str(args.event_panel),
        },
        'annual_summary': annual_summary,
        'sample_summary': sample_summary,
        'model_rows': rows,
        'outputs': {
            'docx': str(docx_path),
            'latex': str(latex_path),
            'csv': str(csv_path),
            'figure_png': str(png_path),
            'figure_pdf': str(pdf_path),
            'writer_packet': str(writer_packet_path),
            'result_notes': str(result_notes_path),
            'markdown_preview': markdown,
        },
    }
    (run_root / 'run_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
