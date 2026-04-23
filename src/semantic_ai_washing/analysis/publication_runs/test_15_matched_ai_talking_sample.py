"""Publication run driver for Test 15: matched AI-talking comparison sample."""

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
from scipy import stats
from scipy.spatial.distance import cdist

from semantic_ai_washing.analysis.delivery_table_payloads import _add_patent_mismatch
from semantic_ai_washing.analysis.publication_runs.test_03_post_filing_drift import (
    _add_note,
    _add_title,
    _build_panel_table,
    _set_document_defaults,
    _set_landscape,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_EVENT_PANEL = (
    REPO_ROOT
    / "data/processed/panel/filing_event_estimation_sample_hybrid_api_a_conf49_v1.parquet"
)
DEFAULT_ANNUAL_PANEL = (
    REPO_ROOT
    / "data/processed/panel/canonical/ever_speaker_panel_2016_2025_hybrid_api_a_conf49_v1.parquet"
)
DEFAULT_TEST_ROOT = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_1/test_runs/test_15_matched_ai_talking_sample"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated/v3_1"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_aiw_v3_1_test_15_matched_ai_talking_sample_main_v1"
TEST_ID = "test_15_matched_ai_talking_sample"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.test_15_matched_ai_talking_sample"
MATCH_VARS = [
    "log_mcap_l1",
    "annual_bhar_vw_l1",
    "annual_ret_l1",
    "ln_assets",
    "leverage",
    "cash",
    "roa",
]
MATCH_CALIPER = 1.5
BALANCE_VARS = [
    ("log_mcap_l1", "log(Market Cap, t-1)"),
    ("annual_bhar_vw_l1", "Annual BHAR, t-1"),
    ("annual_ret_l1", "Annual Return, t-1"),
    ("ln_assets", "ln(Assets)"),
    ("leverage", "Leverage"),
    ("cash", "Cash/Assets"),
    ("roa", "ROA"),
]
OUTCOME_VARS = [
    ("car_m1_p1", "CAR[-1,+1]"),
    ("bhar_1m", "BHAR[+2,+21]"),
    ("bhar_3m", "BHAR[+2,+63]"),
    ("bhar_6m", "BHAR[+2,+126]"),
    ("bhar_12m", "BHAR[+2,+252]"),
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-panel", type=Path, default=DEFAULT_EVENT_PANEL)
    parser.add_argument("--annual-panel", type=Path, default=DEFAULT_ANNUAL_PANEL)
    parser.add_argument("--test-root", type=Path, default=DEFAULT_TEST_ROOT)
    parser.add_argument("--paper-root", type=Path, default=DEFAULT_PAPER_ROOT)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    return parser.parse_args()


def _normalize_id(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
        .replace({"nan": "", "None": ""})
    )


def _ensure_sic2(panel: pd.DataFrame) -> pd.DataFrame:
    out = panel.copy()
    if "sic2" not in out.columns or out["sic2"].isna().all():
        if "sic" in out.columns:
            sic_raw = pd.to_numeric(out["sic"], errors="coerce")
            out["sic2"] = (sic_raw // 100).astype("Int64")
        else:
            out["sic2"] = pd.Series(pd.NA, index=out.index, dtype="Int64")
    return out


def _base_style() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 9,
        }
    )


def _load_annual_backbone(path: Path) -> pd.DataFrame:
    annual = pd.read_parquet(path).copy()
    annual = _ensure_sic2(annual)
    annual = _add_patent_mismatch(annual)
    annual["cik"] = _normalize_id(annual["cik"])
    annual["year"] = pd.to_numeric(annual["year"], errors="coerce").astype("Int64")
    return annual


def _build_analysis_sample(event_panel: Path, annual_panel: Path) -> tuple[pd.DataFrame, dict[str, object]]:
    event = pd.read_parquet(event_panel).copy()
    event["cik"] = _normalize_id(event["cik"])
    event["gvkey"] = _normalize_id(event["gvkey"])
    event["filing_year"] = pd.to_numeric(event["filing_year"], errors="coerce").astype("Int64")
    event["n_ai_total"] = pd.to_numeric(event["n_ai_total"], errors="coerce")
    event = event.loc[event["n_ai_total"].fillna(0).gt(0)].copy()

    annual = _load_annual_backbone(annual_panel)
    current = annual[["cik", "year", "sic2", "PatentMismatch", "A_S", "AI_Focus"]].copy()
    lagged = annual[["cik", "year", "market_cap_year_end", "annual_bhar_vw", "annual_ret"]].copy()
    lagged["year"] = lagged["year"] + 1
    lagged = lagged.rename(
        columns={
            "market_cap_year_end": "market_cap_lag1",
            "annual_bhar_vw": "annual_bhar_vw_l1",
            "annual_ret": "annual_ret_l1",
        }
    )

    sample = event.merge(
        current,
        left_on=["cik", "filing_year"],
        right_on=["cik", "year"],
        how="left",
        validate="many_to_one",
    )
    sample = sample.merge(
        lagged,
        left_on=["cik", "filing_year"],
        right_on=["cik", "year"],
        how="left",
        validate="many_to_one",
        suffixes=("", "_lag1"),
    )
    sample["PatentMismatch"] = pd.to_numeric(sample["PatentMismatch"], errors="coerce")
    sample["sic2"] = pd.to_numeric(sample["sic2"], errors="coerce").astype("Int64")
    sample["log_mcap_l1"] = np.log1p(pd.to_numeric(sample["market_cap_lag1"], errors="coerce"))
    for column in ["annual_bhar_vw_l1", "annual_ret_l1", "ln_assets", "leverage", "cash", "roa"]:
        sample[column] = pd.to_numeric(sample[column], errors="coerce")

    sample = sample.dropna(subset=["PatentMismatch", "sic2", *MATCH_VARS]).copy()
    sample["PatentMismatch"] = sample["PatentMismatch"].astype(int)

    summary = {
        "ai_filing_rows": int(len(sample)),
        "unique_firms": int(sample["gvkey"].replace("", pd.NA).dropna().nunique()),
        "filing_year_min": int(sample["filing_year"].min()),
        "filing_year_max": int(sample["filing_year"].max()),
        "mismatch_share": float(sample["PatentMismatch"].mean()),
    }
    return sample, summary


def _match_pairs(sample: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    pairs: list[dict[str, object]] = []
    cell_counts: list[dict[str, object]] = []
    for (filing_year, sic2), sub in sample.groupby(["filing_year", "sic2"], dropna=True):
        treated = sub.loc[sub["PatentMismatch"].eq(1)].copy()
        control = sub.loc[sub["PatentMismatch"].eq(0)].copy()
        if treated.empty or control.empty:
            continue
        t_x = treated[MATCH_VARS].to_numpy(dtype=float)
        c_x = control[MATCH_VARS].to_numpy(dtype=float)
        combined = np.vstack([t_x, c_x])
        mu = np.nanmean(combined, axis=0)
        sigma = np.nanstd(combined, axis=0)
        sigma[sigma == 0] = 1.0
        t_z = (t_x - mu) / sigma
        c_z = (c_x - mu) / sigma
        distance = cdist(t_z, c_z)
        available = np.ones(len(control), dtype=bool)
        matched_in_cell = 0
        for i in range(len(treated)):
            j = np.argmin(np.where(available, distance[i], np.inf))
            if not np.isfinite(distance[i, j]) or distance[i, j] > MATCH_CALIPER:
                continue
            available[j] = False
            matched_in_cell += 1
            pairs.append(
                {
                    "treated_id": treated.iloc[i]["filing_id"],
                    "control_id": control.iloc[j]["filing_id"],
                    "filing_year": int(filing_year),
                    "sic2": int(sic2),
                    "match_distance": float(distance[i, j]),
                }
            )
        cell_counts.append(
            {
                "filing_year": int(filing_year),
                "sic2": int(sic2),
                "treated_count": int(len(treated)),
                "control_count": int(len(control)),
                "matched_count": int(matched_in_cell),
            }
        )
    pairs_df = pd.DataFrame(pairs)
    cell_df = pd.DataFrame(cell_counts)
    summary = {
        "matched_pairs": int(len(pairs_df)),
        "matched_treated_share": float(len(pairs_df) / sample["PatentMismatch"].sum()) if sample["PatentMismatch"].sum() else math.nan,
        "median_match_distance": float(pairs_df["match_distance"].median()) if not pairs_df.empty else math.nan,
        "median_matches_per_cell": float(cell_df["matched_count"].median()) if not cell_df.empty else math.nan,
        "match_caliper": MATCH_CALIPER,
    }
    return pairs_df, summary


def _standardized_mean_diff(treated: pd.Series, control: pd.Series) -> float:
    treated = pd.to_numeric(treated, errors="coerce").dropna()
    control = pd.to_numeric(control, errors="coerce").dropna()
    if treated.empty or control.empty:
        return math.nan
    pooled = np.sqrt((treated.var(ddof=1) + control.var(ddof=1)) / 2)
    if pooled == 0 or pd.isna(pooled):
        return 0.0
    return float((treated.mean() - control.mean()) / pooled)


def _build_balance_table(sample: pd.DataFrame, pairs_df: pd.DataFrame) -> pd.DataFrame:
    sample_indexed = sample.set_index("filing_id")
    pre_treated = sample.loc[sample["PatentMismatch"].eq(1)].copy()
    pre_control = sample.loc[sample["PatentMismatch"].eq(0)].copy()

    matched_treated = sample_indexed.loc[pairs_df["treated_id"]].copy()
    matched_control = sample_indexed.loc[pairs_df["control_id"]].copy()

    rows = []
    for variable, label in BALANCE_VARS:
        rows.append(
            {
                "row_label": label,
                "pre_treated_mean": float(pd.to_numeric(pre_treated[variable], errors="coerce").mean()),
                "pre_control_mean": float(pd.to_numeric(pre_control[variable], errors="coerce").mean()),
                "pre_smd": _standardized_mean_diff(pre_treated[variable], pre_control[variable]),
                "matched_treated_mean": float(pd.to_numeric(matched_treated[variable], errors="coerce").mean()),
                "matched_control_mean": float(pd.to_numeric(matched_control[variable], errors="coerce").mean()),
                "matched_smd": _standardized_mean_diff(matched_treated[variable], matched_control[variable]),
            }
        )
    return pd.DataFrame(rows)


def _build_outcome_table(sample: pd.DataFrame, pairs_df: pd.DataFrame) -> pd.DataFrame:
    sample_indexed = sample.set_index("filing_id")
    rows = []
    for variable, label in OUTCOME_VARS:
        pairs = pairs_df.copy()
        pairs["treated_outcome"] = pd.to_numeric(sample_indexed.loc[pairs["treated_id"], variable], errors="coerce").to_numpy()
        pairs["control_outcome"] = pd.to_numeric(sample_indexed.loc[pairs["control_id"], variable], errors="coerce").to_numpy()
        pairs = pairs.dropna(subset=["treated_outcome", "control_outcome"]).copy()
        diff = pairs["treated_outcome"] - pairs["control_outcome"]
        t_stat, p_value = stats.ttest_1samp(diff, 0, nan_policy="omit")
        se_diff = float(diff.std(ddof=1) / np.sqrt(len(diff))) if len(diff) > 1 else math.nan
        rows.append(
            {
                "row_label": label,
                "treated_mean": float(pairs["treated_outcome"].mean()),
                "control_mean": float(pairs["control_outcome"].mean()),
                "diff_treat_minus_control": float(diff.mean()),
                "p_value": float(p_value),
                "se_diff": se_diff,
                "n_pairs": int(len(pairs)),
            }
        )
    return pd.DataFrame(rows)


def _markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return "\n".join(lines)


def _render_table_outputs(balance_df: pd.DataFrame, outcome_df: pd.DataFrame) -> tuple[str, str]:
    balance_headers = ["Row", "Pre treated", "Pre control", "Pre SMD", "Matched treated", "Matched control", "Matched SMD"]
    balance_rows = []
    for row in balance_df.itertuples(index=False):
        balance_rows.append(
            [
                row.row_label,
                f"{row.pre_treated_mean:.4f}",
                f"{row.pre_control_mean:.4f}",
                f"{row.pre_smd:.3f}",
                f"{row.matched_treated_mean:.4f}",
                f"{row.matched_control_mean:.4f}",
                f"{row.matched_smd:.3f}",
            ]
        )

    outcome_headers = ["Row", "Treated mean", "Control mean", "Diff", "p-value", "N pairs"]
    outcome_rows = []
    for row in outcome_df.itertuples(index=False):
        outcome_rows.append(
            [
                row.row_label,
                f"{100 * row.treated_mean:.3f}",
                f"{100 * row.control_mean:.3f}",
                f"{100 * row.diff_treat_minus_control:.3f}",
                f"{row.p_value:.3f}",
                row.n_pairs,
            ]
        )

    md = "\n".join(
        [
            "# Table Main",
            "",
            "## Panel A. Covariate balance",
            _markdown_table(balance_headers, balance_rows),
            "",
            "## Panel B. Matched outcome differences",
            _markdown_table(outcome_headers, outcome_rows),
            "",
        ]
    )

    latex_lines = [
        "\\begin{table}[!htbp]",
        "\\centering",
        "\\caption{Matched AI-talking comparison sample}",
        "\\begin{tabular}{l" + "c" * (len(outcome_headers) - 1) + "}",
        "\\hline",
        " & " + " & ".join(outcome_headers[1:]) + " \\\\",
        "\\hline",
    ]
    for row in outcome_rows:
        latex_lines.append(str(row[0]) + " & " + " & ".join(str(item) for item in row[1:]) + " \\\\")
    latex_lines.extend(["\\hline", "\\end{tabular}", "\\end{table}"])
    return md, "\n".join(latex_lines) + "\n"


def _docx_balance_rows(balance_df: pd.DataFrame) -> list[list[tuple[str, bool]]]:
    rows = []
    for row in balance_df.itertuples(index=False):
        rows.append(
            [
                (row.row_label, True),
                (f"{row.pre_treated_mean:.4f}", False),
                (f"{row.pre_control_mean:.4f}", False),
                (f"{row.pre_smd:.3f}", False),
                (f"{row.matched_treated_mean:.4f}", False),
                (f"{row.matched_control_mean:.4f}", False),
                (f"{row.matched_smd:.3f}", False),
            ]
        )
    return rows


def _docx_outcome_rows(outcome_df: pd.DataFrame) -> list[list[tuple[str, bool]]]:
    rows = []
    for row in outcome_df.itertuples(index=False):
        rows.append(
            [
                (row.row_label, True),
                (f"{100 * row.treated_mean:.3f}", False),
                (f"{100 * row.control_mean:.3f}", False),
                (f"{100 * row.diff_treat_minus_control:.3f}", False),
                (f"{row.p_value:.3f}", False),
                (str(row.n_pairs), False),
            ]
        )
    return rows


def _build_table_docx(balance_df: pd.DataFrame, outcome_df: pd.DataFrame, output_path: Path) -> None:
    document = Document()
    _set_document_defaults(document)
    _set_landscape(document)
    _add_title(document, "Table 15. Matched AI-Talking Comparison Sample")
    note = (
        "Panel A reports covariate balance before and after one-to-one nearest-neighbor matching without replacement. Matches are exact on filing year and SIC2 industry and nearest on lagged size, lagged return history, and core balance-sheet characteristics, subject to a standardized-distance caliper. Panel B reports paired outcome differences between mismatch filings and matched non-mismatch filings."
    )
    _add_note(document, note)
    p = document.add_paragraph()
    p.add_run("Panel A. Covariate balance").bold = True
    _build_panel_table(
        document,
        ["", "Pre treated", "Pre control", "Pre SMD", "Matched treated", "Matched control", "Matched SMD"],
        _docx_balance_rows(balance_df),
    )
    p = document.add_paragraph()
    p.add_run("Panel B. Matched outcome differences").bold = True
    _build_panel_table(
        document,
        ["", "Treated mean", "Control mean", "Diff", "p-value", "N pairs"],
        _docx_outcome_rows(outcome_df),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.save(str(output_path))


def _plot_outcomes(outcome_df: pd.DataFrame, output_base: Path) -> tuple[Path, Path]:
    _base_style()
    fig, ax = plt.subplots(figsize=(8.4, 4.8), constrained_layout=True)
    order = {label: i for i, (_, label) in enumerate(OUTCOME_VARS)}
    plotted = outcome_df.copy()
    plotted["sort_key"] = plotted["row_label"].map(order)
    plotted = plotted.sort_values("sort_key")
    x = np.arange(len(plotted))
    ax.errorbar(
        x,
        100 * plotted["diff_treat_minus_control"],
        yerr=1.96 * 100 * plotted["se_diff"],
        fmt="o-",
        color="#1d3557",
        linewidth=2.0,
        capsize=4,
    )
    ax.axhline(0, color="#6c757d", linewidth=0.8)
    ax.set_xticks(x, plotted["row_label"], rotation=0)
    ax.set_ylabel("Matched treated-control difference (pct)")
    ax.set_title("Matched Outcome Differences for Mismatch Filings")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    png_path = output_base.with_suffix(".png")
    pdf_path = output_base.with_suffix(".pdf")
    fig.savefig(png_path, dpi=220, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    return png_path, pdf_path


def _result_notes(balance_df: pd.DataFrame, outcome_df: pd.DataFrame, sample_summary: dict[str, object], match_summary: dict[str, object]) -> str:
    car_row = outcome_df.loc[outcome_df["row_label"].eq("CAR[-1,+1]")].iloc[0]
    bhar_3m_row = outcome_df.loc[outcome_df["row_label"].eq("BHAR[+2,+63]")].iloc[0]
    max_pre = balance_df["pre_smd"].abs().max()
    max_post = balance_df["matched_smd"].abs().max()
    return "\n".join(
        [
            f"# Result Notes: {TEST_ID}",
            "",
            f"- AI-filing sample available for matching: `{sample_summary['ai_filing_rows']}` rows across `{sample_summary['unique_firms']}` firms.",
            f"- Matched pairs: `{match_summary['matched_pairs']}` with median match distance `{match_summary['median_match_distance']:.3f}` under a caliper of `{match_summary['match_caliper']:.2f}`.",
            f"- Max absolute SMD before matching: `{max_pre:.3f}`; after matching: `{max_post:.3f}`.",
            f"- Matched CAR[-1,+1] difference: `{100 * car_row['diff_treat_minus_control']:.3f}` pct (p=`{car_row['p_value']:.3f}`).",
            f"- Matched BHAR[+2,+63] difference: `{100 * bhar_3m_row['diff_treat_minus_control']:.3f}` pct (p=`{bhar_3m_row['p_value']:.3f}`).",
            "- Interpretation discipline: in the tightened matched sample, the filing-date CAR difference does not survive. That pushes the market-results block away from a robust pricing interpretation and toward the view that the earlier signal was sensitive to observable composition.",
            "",
        ]
    )


def _writer_packet(args: argparse.Namespace, balance_df: pd.DataFrame, outcome_df: pd.DataFrame, sample_summary: dict[str, object], match_summary: dict[str, object]) -> str:
    car_row = outcome_df.loc[outcome_df["row_label"].eq("CAR[-1,+1]")].iloc[0]
    return "\n".join(
        [
            f"# Writer Packet: {TEST_ID}",
            "",
            "## Purpose",
            "- This run asks whether mismatch filings still differ from non-mismatch filings after comparing them to observationally similar AI-talking peers.",
            "- The matching layer is intended to address the obvious cross-sectional-composition critique more directly than the raw portfolio sorts.",
            "",
            "## Matching Design",
            "- Exact match dimensions: `filing_year`, `sic2`",
            "- Nearest-neighbor dimensions: `log(Market Cap, t-1)`, `annual BHAR, t-1`, `annual return, t-1`, `ln(Assets)`, `leverage`, `cash`, `ROA`",
            "- Matching: one-to-one without replacement",
            f"- Standardized-distance caliper: `{match_summary['match_caliper']:.2f}`",
            "",
            "## Sample Counts",
            f"- AI-filing rows available for matching: `{sample_summary['ai_filing_rows']}`",
            f"- Unique firms: `{sample_summary['unique_firms']}`",
            f"- Matched pairs: `{match_summary['matched_pairs']}`",
            "",
            "## Balance",
            f"- Median match distance: `{match_summary['median_match_distance']:.3f}`",
            f"- Max absolute matched SMD: `{balance_df['matched_smd'].abs().max():.3f}`",
            "",
            "## Main Read",
            f"- Matched CAR[-1,+1] difference: `{100 * car_row['diff_treat_minus_control']:.3f}` pct (p=`{car_row['p_value']:.3f}`)",
            "",
            "## Caption Draft",
            "This table and figure compare mismatch filings to matched non-mismatch AI-talking filings. Matches are exact on filing year and industry and nearest on lagged size, lagged return history, and core balance-sheet characteristics, subject to a standardized-distance caliper. If the filing-date CAR difference does not survive in the tightened matched sample, the market-results block should not be presented as robust to richer observable balancing.",
            "",
        ]
    )


def _dataset_summary(
    sample_summary: dict[str, object],
    match_summary: dict[str, object],
    balance_df: pd.DataFrame,
    outcome_df: pd.DataFrame,
    pairs_df: pd.DataFrame,
    *,
    args: argparse.Namespace,
) -> dict[str, object]:
    return {
        "test_id": TEST_ID,
        "run_id": args.run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "inputs": {
            "event_panel": str(args.event_panel),
            "annual_panel": str(args.annual_panel),
        },
        "sample_summary": sample_summary,
        "match_summary": match_summary,
        "balance_rows": balance_df.to_dict(orient="records"),
        "outcome_rows": outcome_df.to_dict(orient="records"),
        "pairs_head": pairs_df.head(25).to_dict(orient="records"),
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
        run_dir / "main_figure.png": exports["figure_png"],
        run_dir / "main_figure.pdf": exports["figure_pdf"],
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

    sample, sample_summary = _build_analysis_sample(args.event_panel, args.annual_panel)
    pairs_df, match_summary = _match_pairs(sample)
    balance_df = _build_balance_table(sample, pairs_df)
    outcome_df = _build_outcome_table(sample, pairs_df)

    combined_table = pd.concat(
        [
            balance_df.assign(panel="Panel A. Covariate balance"),
            outcome_df.assign(panel="Panel B. Matched outcome differences"),
        ],
        ignore_index=True,
        sort=False,
    )
    combined_table.to_csv(run_dir / "table_main.csv", index=False)
    table_md, table_tex = _render_table_outputs(balance_df, outcome_df)
    (run_dir / "table_main.md").write_text(table_md, encoding="utf-8")
    (run_dir / "table_main.tex").write_text(table_tex, encoding="utf-8")
    _build_table_docx(balance_df, outcome_df, run_dir / "table_main.docx")
    outcome_df.to_csv(run_dir / "figure_series.csv", index=False)
    fig_png, fig_pdf = _plot_outcomes(outcome_df, run_dir / "main_figure")
    (run_dir / "result_notes.md").write_text(
        _result_notes(balance_df, outcome_df, sample_summary, match_summary), encoding="utf-8"
    )
    (run_dir / "writer_packet.md").write_text(
        _writer_packet(args, balance_df, outcome_df, sample_summary, match_summary),
        encoding="utf-8",
    )
    dataset_summary = _dataset_summary(
        sample_summary, match_summary, balance_df, outcome_df, pairs_df, args=args
    )
    (run_dir / "dataset_summary.json").write_text(json.dumps(dataset_summary, indent=2), encoding="utf-8")

    paper_exports = _copy_exports(run_dir, args.paper_root, args.run_id)
    manifest = {
        "test_id": TEST_ID,
        "run_id": args.run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "module_path": MODULE_PATH,
        "run_dir": str(run_dir),
        "inputs": {
            "event_panel": str(args.event_panel),
            "annual_panel": str(args.annual_panel),
        },
        "outputs": {
            "dataset_summary": str(run_dir / "dataset_summary.json"),
            "table_csv": str(run_dir / "table_main.csv"),
            "table_md": str(run_dir / "table_main.md"),
            "table_tex": str(run_dir / "table_main.tex"),
            "table_docx": str(run_dir / "table_main.docx"),
            "figure_png": str(fig_png),
            "figure_pdf": str(fig_pdf),
            "figure_series": str(run_dir / "figure_series.csv"),
            "writer_packet": str(run_dir / "writer_packet.md"),
            "result_notes": str(run_dir / "result_notes.md"),
        },
        "paper_exports": paper_exports,
    }
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"[{TEST_ID}] wrote run bundle to {run_dir}")
    print(f"[{TEST_ID}] paper table: {paper_exports['table_docx']}")
    print(f"[{TEST_ID}] paper figure: {paper_exports['figure_png']}")


if __name__ == "__main__":
    main()
