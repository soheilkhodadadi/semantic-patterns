"""Publication run driver for Test 02: filing-date CAR."""

from __future__ import annotations

import argparse
import json
import math
import shutil
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt
from scipy import stats
import statsmodels.formula.api as smf

from semantic_ai_washing.analysis.delivery_table_payloads import _add_patent_mismatch

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_EVENT_PANEL = (
    REPO_ROOT
    / "data/processed/panel/filing_event_estimation_sample_hybrid_api_a_conf49_v1.parquet"
)
DEFAULT_DAILY_RETURNS = (
    REPO_ROOT / "data/interim/market/filing_event_returns_daily_hybrid_api_a_conf49_v1.parquet"
)
DEFAULT_ANNUAL_PANEL = (
    REPO_ROOT
    / "data/processed/panel/canonical/ever_speaker_panel_2016_2025_hybrid_api_a_conf49_v1.parquet"
)
DEFAULT_TEST_ROOT = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/test_runs/test_02_filing_date_car"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_hybrid_api_a_conf49_main_v1"
TEST_ID = "test_02_filing_date_car"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.test_02_filing_date_car"
CONTROL_TERMS = ["ln_assets", "leverage", "cash", "roa"]
FOCAL_TERMS = ["PatentMismatch", "A_S", "AI_Focus"]
EVENT_FIGURE_DAYS = (-2, 2)


@dataclass(frozen=True)
class RegressionSpec:
    model_id: str
    dependent: str
    title: str


REGRESSION_SPECS = [
    RegressionSpec(
        model_id="car_m1_p1_market_adjusted_cluster",
        dependent="car_m1_p1",
        title="CAR[-1,+1]",
    ),
    RegressionSpec(
        model_id="car_m2_p2_market_adjusted_cluster",
        dependent="car_m2_p2",
        title="CAR[-2,+2]",
    ),
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-panel", type=Path, default=DEFAULT_EVENT_PANEL)
    parser.add_argument("--daily-returns", type=Path, default=DEFAULT_DAILY_RETURNS)
    parser.add_argument("--annual-panel", type=Path, default=DEFAULT_ANNUAL_PANEL)
    parser.add_argument("--test-root", type=Path, default=DEFAULT_TEST_ROOT)
    parser.add_argument("--paper-root", type=Path, default=DEFAULT_PAPER_ROOT)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    return parser.parse_args()


def _ensure_sic2(df: pd.DataFrame) -> pd.DataFrame:
    panel = df.copy()
    if "sic2" not in panel.columns or panel["sic2"].isna().all():
        if "sic" in panel.columns:
            sic_raw = pd.to_numeric(panel["sic"], errors="coerce")
            panel["sic2"] = (sic_raw // 100).astype("Int64")
        else:
            panel["sic2"] = pd.Series(pd.NA, index=panel.index, dtype="Int64")
    return panel


def _load_annual_backbone(path: Path) -> pd.DataFrame:
    annual = pd.read_parquet(path)
    annual = _ensure_sic2(annual)
    annual = _add_patent_mismatch(annual)
    keep = [
        "cik",
        "year",
        "PatentMismatch",
        "A_S",
        "AI_Focus",
        "CredAI",
        "SpecShare",
        "any_ai_talk",
        "sic2",
    ]
    annual = annual[keep].copy()
    annual["cik"] = annual["cik"].astype(str)
    annual["year"] = pd.to_numeric(annual["year"], errors="coerce").astype("Int64")
    return annual


def _build_analysis_sample(event_panel: Path, annual_panel: Path) -> pd.DataFrame:
    event = pd.read_parquet(event_panel).copy()
    event["cik"] = event["cik"].astype(str)
    event["filing_year"] = pd.to_numeric(event["filing_year"], errors="coerce").astype("Int64")

    annual = _load_annual_backbone(annual_panel)
    merged = event.merge(
        annual,
        left_on=["cik", "filing_year"],
        right_on=["cik", "year"],
        how="left",
        validate="many_to_one",
    )
    merged["is_ai_filing"] = pd.to_numeric(merged["n_ai_total"], errors="coerce").fillna(0).gt(0)
    return merged


def _difference_in_means(sample: pd.DataFrame, dependent: str) -> dict[str, float | int | None]:
    use = sample.loc[
        sample["is_ai_filing"] & sample[dependent].notna() & sample["PatentMismatch"].notna()
    ].copy()
    use["PatentMismatch"] = (
        pd.to_numeric(use["PatentMismatch"], errors="coerce").fillna(0).astype(int)
    )

    mismatch = use.loc[use["PatentMismatch"].eq(1), dependent].astype(float)
    non_mismatch = use.loc[use["PatentMismatch"].eq(0), dependent].astype(float)
    if len(mismatch) == 0 or len(non_mismatch) == 0:
        return {
            "n_total": int(len(use)),
            "n_mismatch": int(len(mismatch)),
            "n_non_mismatch": int(len(non_mismatch)),
            "mean_mismatch": None,
            "mean_non_mismatch": None,
            "diff_mismatch_minus_non": None,
            "t_stat": None,
            "p_value": None,
        }

    t_stat, p_value = stats.ttest_ind(mismatch, non_mismatch, equal_var=False, nan_policy="omit")
    return {
        "n_total": int(len(use)),
        "n_mismatch": int(len(mismatch)),
        "n_non_mismatch": int(len(non_mismatch)),
        "mean_mismatch": float(mismatch.mean()),
        "mean_non_mismatch": float(non_mismatch.mean()),
        "diff_mismatch_minus_non": float(mismatch.mean() - non_mismatch.mean()),
        "t_stat": float(t_stat),
        "p_value": float(p_value),
    }


def _fit_regression(sample: pd.DataFrame, spec: RegressionSpec) -> dict[str, object]:
    needed = [
        spec.dependent,
        "PatentMismatch",
        "A_S",
        "AI_Focus",
        "sic2",
        "filing_year",
        "gvkey",
        *CONTROL_TERMS,
    ]
    use = sample.loc[sample["is_ai_filing"]].copy()
    use = use.dropna(subset=needed)
    use = use.loc[use["gvkey"].astype(str).str.len().gt(0)].copy()
    use["PatentMismatch"] = pd.to_numeric(use["PatentMismatch"], errors="coerce").astype(float)
    use["A_S"] = pd.to_numeric(use["A_S"], errors="coerce").astype(float)
    use["AI_Focus"] = pd.to_numeric(use["AI_Focus"], errors="coerce").astype(float)
    use["sic2"] = pd.to_numeric(use["sic2"], errors="coerce").astype(int)
    use["filing_year"] = pd.to_numeric(use["filing_year"], errors="coerce").astype(int)
    for control in CONTROL_TERMS:
        use[control] = pd.to_numeric(use[control], errors="coerce").astype(float)
    formula = (
        f"{spec.dependent} ~ PatentMismatch + A_S + AI_Focus + "
        + " + ".join(CONTROL_TERMS)
        + " + C(sic2) + C(filing_year)"
    )
    model = smf.ols(formula=formula, data=use)
    result = model.fit(cov_type="cluster", cov_kwds={"groups": use["gvkey"].astype(str)})
    term_map: dict[str, dict[str, float | None]] = {}
    for term in FOCAL_TERMS:
        term_map[term] = {
            "coef": float(result.params.get(term, math.nan)),
            "se": float(result.bse.get(term, math.nan)),
            "t_stat": float(result.tvalues.get(term, math.nan)),
            "p_value": float(result.pvalues.get(term, math.nan)),
        }
    return {
        "model_id": spec.model_id,
        "title": spec.title,
        "dependent": spec.dependent,
        "nobs": int(result.nobs),
        "r_squared": float(result.rsquared),
        "adj_r_squared": float(result.rsquared_adj),
        "formula": formula,
        "covariance": "cluster(gvkey)",
        "focal_terms": term_map,
    }


def _event_window_summary(sample: pd.DataFrame, daily_returns: Path) -> pd.DataFrame:
    keep_ids = sample.loc[sample["is_ai_filing"], ["filing_id", "PatentMismatch"]].copy()
    keep_ids["PatentMismatch"] = (
        pd.to_numeric(keep_ids["PatentMismatch"], errors="coerce").fillna(0).astype(int)
    )

    daily = pd.read_parquet(
        daily_returns, columns=["filing_id", "relative_day", "abnormal_ret_vw"]
    ).copy()
    daily = daily.merge(keep_ids, on="filing_id", how="inner")
    daily = daily.loc[
        daily["relative_day"].between(EVENT_FIGURE_DAYS[0], EVENT_FIGURE_DAYS[1])
    ].copy()

    grouped = (
        daily.groupby(["PatentMismatch", "relative_day"], as_index=False)
        .agg(
            filing_count=("filing_id", "nunique"),
            mean_abnormal_ret=("abnormal_ret_vw", "mean"),
        )
        .sort_values(["PatentMismatch", "relative_day"])
        .reset_index(drop=True)
    )
    grouped["group_label"] = grouped["PatentMismatch"].map({0: "No mismatch", 1: "Mismatch"})
    grouped["cum_mean_abnormal_ret"] = grouped.groupby("PatentMismatch")[
        "mean_abnormal_ret"
    ].cumsum()
    return grouped


def _base_style() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "axes.titlesize": 14,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 10,
        }
    )


def _plot_event_figure(summary: pd.DataFrame, output_base: Path) -> tuple[Path, Path]:
    _base_style()
    fig, ax = plt.subplots(figsize=(8.2, 4.8), constrained_layout=True)
    color_map = {0: "#1d3557", 1: "#c46b48"}

    for mismatch_value in [0, 1]:
        sub = summary.loc[summary["PatentMismatch"].eq(mismatch_value)].copy()
        ax.plot(
            sub["relative_day"],
            100 * sub["cum_mean_abnormal_ret"],
            marker="o",
            linewidth=2.2,
            color=color_map[mismatch_value],
            label=sub["group_label"].iloc[0],
        )

    ax.axvline(0, color="#6c757d", linestyle="--", linewidth=1)
    ax.axhline(0, color="#6c757d", linewidth=0.8)
    ax.set_xlabel("Event day")
    ax.set_ylabel("Cumulative mean abnormal return (pct)")
    ax.set_title("Filing-Date Abnormal Returns Around 10-K Release")
    ax.legend(frameon=False, loc="best")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, axis="y", color="#d9d9d9", linewidth=0.7)
    ax.grid(False, axis="x")

    png_path = output_base.with_suffix(".png")
    pdf_path = output_base.with_suffix(".pdf")
    fig.savefig(png_path, dpi=220, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    return png_path, pdf_path


def _coef_cell(values: dict[str, float | None]) -> str:
    coef = values.get("coef")
    se = values.get("se")
    p_value = values.get("p_value")
    if coef is None or se is None or not math.isfinite(coef) or not math.isfinite(se):
        return ""
    stars = ""
    if p_value is not None and math.isfinite(p_value):
        if p_value < 0.01:
            stars = "***"
        elif p_value < 0.05:
            stars = "**"
        elif p_value < 0.10:
            stars = "*"
    return f"{coef:.4f}{stars} ({se:.4f})"


def _markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return "\n".join(lines)


def _render_table_outputs(
    diff_rows: list[dict[str, object]], regression_rows: list[dict[str, object]]
) -> tuple[str, str]:
    panel_a_headers = ["Window", "Mean mismatch", "Mean non-mismatch", "Diff", "p-value", "N"]
    panel_a_rows: list[list[object]] = []
    for row in diff_rows:
        panel_a_rows.append(
            [
                row["window_label"],
                f"{100 * row['mean_mismatch']:.3f}" if row["mean_mismatch"] is not None else "",
                f"{100 * row['mean_non_mismatch']:.3f}"
                if row["mean_non_mismatch"] is not None
                else "",
                f"{100 * row['diff_mismatch_minus_non']:.3f}"
                if row["diff_mismatch_minus_non"] is not None
                else "",
                f"{row['p_value']:.3f}" if row["p_value"] is not None else "",
                row["n_total"],
            ]
        )

    panel_b_headers = ["Row"] + [row["title"] for row in regression_rows]
    panel_b_rows = []
    for term in FOCAL_TERMS:
        display = {
            "PatentMismatch": "PatentMismatch",
            "A_S": "A/S ratio",
            "AI_Focus": "AI Focus",
        }[term]
        panel_b_rows.append(
            [display] + [_coef_cell(row["focal_terms"][term]) for row in regression_rows]
        )
    panel_b_rows.append(["Controls"] + ["Y"] * len(regression_rows))
    panel_b_rows.append(["Industry FE"] + ["Y"] * len(regression_rows))
    panel_b_rows.append(["Filing-year FE"] + ["Y"] * len(regression_rows))
    panel_b_rows.append(["SE"] + [row["covariance"] for row in regression_rows])
    panel_b_rows.append(["N"] + [row["nobs"] for row in regression_rows])
    panel_b_rows.append(["R^2"] + [f"{row['r_squared']:.3f}" for row in regression_rows])

    md = "\n".join(
        [
            "# Table Main",
            "",
            "## Panel A. Difference-in-means by PatentMismatch",
            _markdown_table(panel_a_headers, panel_a_rows),
            "",
            "## Panel B. Filing-date CAR regressions",
            _markdown_table(panel_b_headers, panel_b_rows),
            "",
        ]
    )

    latex_lines = [
        "\\begin{table}[!htbp]",
        "\\centering",
        "\\caption{Filing-date abnormal returns and PatentMismatch}",
        "\\begin{tabular}{l" + "c" * len(panel_b_headers[1:]) + "}",
        "\\hline",
        " & " + " & ".join(panel_b_headers[1:]) + " \\\\",
        "\\hline",
    ]
    for row in panel_b_rows:
        latex_lines.append(
            str(row[0]) + " & " + " & ".join(str(item) for item in row[1:]) + " \\\\"
        )
    latex_lines.extend(["\\hline", "\\end{tabular}", "\\end{table}"])
    return md, "\n".join(latex_lines) + "\n"


def _sig_stars(p_value: float | None) -> str:
    if p_value is None or not math.isfinite(p_value):
        return ""
    if p_value < 0.01:
        return "***"
    if p_value < 0.05:
        return "**"
    if p_value < 0.10:
        return "*"
    return ""


def _set_run_font(run, *, size: float = 11, bold: bool = False, italic: bool = False) -> None:
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic


def _set_document_defaults(document: Document) -> None:
    section = document.sections[0]
    section.top_margin = Inches(0.6)
    section.bottom_margin = Inches(0.6)
    section.left_margin = Inches(0.6)
    section.right_margin = Inches(0.6)
    normal = document.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    normal.font.size = Pt(11)


def _set_landscape(document: Document) -> None:
    section = document.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width, section.page_height = section.page_height, section.page_width


def _add_title(document: Document, title: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(6)
    run = paragraph.add_run(title)
    _set_run_font(run, size=15, bold=True)


def _add_note(document: Document, text: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.paragraph_format.space_after = Pt(8)
    run = paragraph.add_run(text)
    _set_run_font(run, size=10.5)


def _clear_cell(cell) -> None:
    cell.text = ""
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.space_before = Pt(0)


def _write_cell(
    cell,
    text: str,
    *,
    align: WD_ALIGN_PARAGRAPH,
    size: float = 10.5,
    bold: bool = False,
) -> None:
    _clear_cell(cell)
    paragraph = cell.paragraphs[0]
    paragraph.alignment = align
    run = paragraph.add_run(text)
    _set_run_font(run, size=size, bold=bold)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER


def _set_cell_border(cell, **kwargs: dict[str, str]) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_borders = tc_pr.first_child_found_in("w:tcBorders")
    if tc_borders is None:
        tc_borders = OxmlElement("w:tcBorders")
        tc_pr.append(tc_borders)
    for edge in ("left", "top", "right", "bottom"):
        edge_data = kwargs.get(edge)
        if edge_data is None:
            continue
        tag = f"w:{edge}"
        element = tc_borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            tc_borders.append(element)
        for key, value in edge_data.items():
            element.set(qn(f"w:{key}"), str(value))


def _set_table_no_borders(table) -> None:
    tbl_pr = table._tbl.tblPr
    tbl_borders = tbl_pr.first_child_found_in("w:tblBorders")
    if tbl_borders is None:
        tbl_borders = OxmlElement("w:tblBorders")
        tbl_pr.append(tbl_borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = tbl_borders.find(qn(f"w:{edge}"))
        if element is None:
            element = OxmlElement(f"w:{edge}")
            tbl_borders.append(element)
        element.set(qn("w:val"), "nil")


def _apply_row_rule(row, *, top: bool = False, bottom: bool = False, size: str = "8") -> None:
    border = {"val": "single", "sz": size, "space": "0", "color": "000000"}
    for cell in row.cells:
        kwargs: dict[str, dict[str, str]] = {}
        if top:
            kwargs["top"] = border
        if bottom:
            kwargs["bottom"] = border
        _set_cell_border(cell, **kwargs)


def _build_panel_table(
    document: Document, headers: list[str], rows: list[list[tuple[str, bool]]]
) -> None:
    table = document.add_table(rows=len(rows) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    _set_table_no_borders(table)

    widths = [Inches(2.9)] + [Inches(2.1)] * (len(headers) - 1)
    header_row = table.rows[0]
    for idx, header in enumerate(headers):
        header_row.cells[idx].width = widths[idx]
        _write_cell(
            header_row.cells[idx],
            header,
            align=WD_ALIGN_PARAGRAPH.CENTER if idx else WD_ALIGN_PARAGRAPH.LEFT,
            size=10.5,
            bold=True,
        )
    _apply_row_rule(header_row, top=True, bottom=True)

    for row_idx, row_values in enumerate(rows, start=1):
        row = table.rows[row_idx]
        for col_idx, (text, bold) in enumerate(row_values):
            row.cells[col_idx].width = widths[col_idx]
            _write_cell(
                row.cells[col_idx],
                text,
                align=WD_ALIGN_PARAGRAPH.CENTER if col_idx else WD_ALIGN_PARAGRAPH.LEFT,
                size=10.2,
                bold=bold,
            )
    _apply_row_rule(table.rows[-1], bottom=True)


def _build_table_docx(
    diff_rows: list[dict[str, object]],
    regression_rows: list[dict[str, object]],
    output_path: Path,
    *,
    has_m5: bool,
) -> None:
    document = Document()
    _set_document_defaults(document)
    _set_landscape(document)
    _add_title(document, "Table 1. Filing-Date Abnormal Returns Around Annual 10-K Releases")
    note = (
        "This table reports market-adjusted filing-date cumulative abnormal returns around annual 10-K releases. "
        "Panel A reports mean CARs by PatentMismatch status and the mismatch-minus-non-mismatch difference. "
        "Panel B reports filing-level regressions of CAR on PatentMismatch, the A/S ratio, and AI Focus with lagged controls, "
        "industry fixed effects, filing-year fixed effects, and standard errors clustered by firm. "
        "Statistical significance at the 1%, 5%, and 10% levels is indicated by ***, **, and *, respectively. "
        + (
            "A CAR[-5,+5] column is not included in this first run because the current daily event-return scaffold starts at event day -2."
            if not has_m5
            else ""
        )
    )
    _add_note(document, note)

    by_window = {row["window_label"]: row for row in diff_rows}
    reg_by_title = {row["title"]: row for row in regression_rows}
    windows = [row["title"] for row in regression_rows]

    panel_a = document.add_paragraph()
    panel_a.paragraph_format.space_after = Pt(4)
    run = panel_a.add_run("Panel A. Difference-in-means by PatentMismatch")
    _set_run_font(run, size=11, bold=True)
    panel_a_rows = [
        [("Mean mismatch", True)]
        + [
            (
                f"{100 * by_window[window]['mean_mismatch']:.3f}"
                if by_window[window]["mean_mismatch"] is not None
                else "",
                False,
            )
            for window in windows
        ],
        [("Mean non-mismatch", True)]
        + [
            (
                f"{100 * by_window[window]['mean_non_mismatch']:.3f}"
                if by_window[window]["mean_non_mismatch"] is not None
                else "",
                False,
            )
            for window in windows
        ],
        [("Difference", True)]
        + [
            (
                f"{100 * by_window[window]['diff_mismatch_minus_non']:.3f}"
                if by_window[window]["diff_mismatch_minus_non"] is not None
                else "",
                False,
            )
            for window in windows
        ],
        [("p-value", True)]
        + [
            (
                f"{by_window[window]['p_value']:.3f}"
                if by_window[window]["p_value"] is not None
                else "",
                False,
            )
            for window in windows
        ],
        [("Observations", True)]
        + [(f"{by_window[window]['n_total']:,}", False) for window in windows],
    ]
    _build_panel_table(document, [""] + windows, panel_a_rows)

    panel_b = document.add_paragraph()
    panel_b.paragraph_format.space_before = Pt(10)
    panel_b.paragraph_format.space_after = Pt(4)
    run = panel_b.add_run("Panel B. Filing-date CAR regressions")
    _set_run_font(run, size=11, bold=True)

    panel_b_rows: list[list[tuple[str, bool]]] = []
    for term, label in [
        ("PatentMismatch", "PatentMismatch"),
        ("A_S", "A/S ratio"),
        ("AI_Focus", "AI Focus"),
    ]:
        panel_b_rows.append(
            [(label, True)]
            + [
                (
                    f"{reg_by_title[window]['focal_terms'][term]['coef']:.4f}{_sig_stars(reg_by_title[window]['focal_terms'][term]['p_value'])}",
                    False,
                )
                for window in windows
            ]
        )
        panel_b_rows.append(
            [("", False)]
            + [
                (f"({reg_by_title[window]['focal_terms'][term]['se']:.4f})", False)
                for window in windows
            ]
        )
    panel_b_rows.extend(
        [
            [("Controls", True)] + [("Y", False) for _ in windows],
            [("Industry FE", True)] + [("Y", False) for _ in windows],
            [("Filing-year FE", True)] + [("Y", False) for _ in windows],
            [("SE", True)] + [("Clustered by firm", False) for _ in windows],
            [("Observations", True)]
            + [(f"{reg_by_title[window]['nobs']:,}", False) for window in windows],
            [("R-squared", True)]
            + [(f"{reg_by_title[window]['r_squared']:.3f}", False) for window in windows],
        ]
    )
    _build_panel_table(document, [""] + windows, panel_b_rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.save(str(output_path))


def _result_notes(
    diff_rows: list[dict[str, object]], regression_rows: list[dict[str, object]], has_m5: bool
) -> str:
    car_m1 = next(row for row in diff_rows if row["window_label"] == "CAR[-1,+1]")
    reg_m1 = next(row for row in regression_rows if row["dependent"] == "car_m1_p1")
    mismatch_term = reg_m1["focal_terms"]["PatentMismatch"]
    lines = [
        "# Result Notes",
        "",
        f"- CAR[-1,+1] mean difference (mismatch minus non-mismatch): `{100 * car_m1['diff_mismatch_minus_non']:.3f}` percentage points, p=`{car_m1['p_value']:.3f}`.",
        f"- Regression coefficient on `PatentMismatch` in CAR[-1,+1]: `{mismatch_term['coef']:.4f}` with p=`{mismatch_term['p_value']:.3f}`.",
        f"- Current daily return scaffold supports an event-time figure over `{EVENT_FIGURE_DAYS[0]}` to `+{EVENT_FIGURE_DAYS[1]}` trading days.",
    ]
    if not has_m5:
        lines.append(
            "- `CAR[-5,+5]` is not included in this first publication bundle because the current daily event-return file was built with `pre_days=2`; extending that window is straightforward but would require a refreshed daily return extraction."
        )
    return "\n".join(lines) + "\n"


def _writer_packet(
    args: argparse.Namespace,
    sample: pd.DataFrame,
    diff_rows: list[dict[str, object]],
    regression_rows: list[dict[str, object]],
    has_m5: bool,
) -> str:
    car_m1 = next(row for row in diff_rows if row["window_label"] == "CAR[-1,+1]")
    reg_m1 = next(row for row in regression_rows if row["dependent"] == "car_m1_p1")
    mismatch_term = reg_m1["focal_terms"]["PatentMismatch"]
    m5_note = (
        "A `CAR[-5,+5]` robustness is parked for the next pass because the current daily return scaffold begins at event day `-2`."
        if not has_m5
        else "A `CAR[-5,+5]` robustness is included in the current run."
    )
    return "\n".join(
        [
            "# Writer Packet",
            "",
            "## Metadata",
            f"- Test id: `{TEST_ID}`",
            f"- Run id: `{args.run_id}`",
            f"- Date run: `{date.today().isoformat()}`",
            f"- Script/module path: `{MODULE_PATH}`",
            f"- Input panel filename(s): `{args.event_panel}`, `{args.annual_panel}`, `{args.daily_returns}`",
            "- Unit of observation: `firm-filing event`",
            "- Sample filters: `AI-talking 10-K / 10-K-A filings with complete CAR window, annual PatentMismatch merge, controls, industry FE, and filing-year FE`",
            "- Date range: `2016-2024`",
            f"- Exact N: `{int(sample['is_ai_filing'].sum()):,}` AI filings in the event sample; `CAR[-1,+1]` regression N = `{reg_m1['nobs']:,}`",
            "",
            "## Variables",
            "- Dependent variable: `market-adjusted CAR around filing date`",
            "- Key regressor(s): `PatentMismatch`, `A_S`, `AI_Focus`",
            "- Treatment/event definition: `PatentMismatch` is the grant-based annual construct merged from the canonical ever-speaker panel for the same firm-year as the filing",
            "- Control set: `ln_assets`, `leverage`, `cash`, `roa`",
            "- Transformations: `industry FE via SIC2`, `filing-year FE`, `clustered standard errors at gvkey`",
            "",
            "## Estimation",
            "- Model equation: `CAR ~ PatentMismatch + A_S + AI_Focus + controls + Industry FE + Filing-year FE`",
            "- Fixed effects: `sic2` and `filing_year`",
            "- Clustering: `gvkey`",
            "- Weighting: `none`",
            "- Benchmark / abnormal return model: `market-adjusted abnormal returns using CRSP vwretd`",
            "",
            "## Results",
            f"- Key coefficient(s) or spread(s): `CAR[-1,+1]` mismatch-minus-non-mismatch mean difference = `{100 * car_m1['diff_mismatch_minus_non']:.3f}` pp; regression `PatentMismatch` coefficient = `{mismatch_term['coef']:.4f}`",
            f"- Standard error / t-stat / p-value: `PatentMismatch` SE = `{mismatch_term['se']:.4f}`, p = `{mismatch_term['p_value']:.3f}`",
            "- Economic magnitude: `Interpret filing-date CAR coefficients as percentage-point shifts in market-adjusted abnormal return around annual 10-K release.`",
            "- One-sentence interpretation: `This first filing-date CAR run tests whether mismatch-labeled AI disclosure is rewarded at the filing date once industry and filing-year structure are absorbed.`",
            "- Main text / appendix / discard: `main text candidate, pending read of coefficient pattern`",
            "",
            "## Caption Draft",
            "This table reports filing-date cumulative abnormal returns around annual 10-K releases. Panel A reports mean CARs by PatentMismatch status and the mismatch-minus-non-mismatch difference. Panel B reports filing-level regressions of CAR on PatentMismatch, the A/S ratio, and AI Focus with lagged controls, industry fixed effects, filing-year fixed effects, and standard errors clustered by firm. A supporting event-time figure is available separately for the short window currently supported by the daily return scaffold.",
            "",
            "## Notes",
            f"- Attrition / missingness note: `{m5_note}`",
            "- Any unusual diagnostics: `All filings in the matched event panel merge cleanly back to the annual AI panel on (cik, filing_year).`",
            "",
        ]
    )


def _dataset_summary(
    sample: pd.DataFrame,
    diff_rows: list[dict[str, object]],
    regression_rows: list[dict[str, object]],
    event_summary: pd.DataFrame,
    *,
    args: argparse.Namespace,
    has_m5: bool,
) -> dict[str, object]:
    return {
        "test_id": TEST_ID,
        "run_id": args.run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "event_panel": str(args.event_panel),
        "annual_panel": str(args.annual_panel),
        "daily_returns": str(args.daily_returns),
        "row_count_event_panel": int(len(sample)),
        "unique_gvkey": int(sample["gvkey"].nunique()),
        "unique_permno": int(sample["permno"].nunique()),
        "filing_year_min": int(sample["filing_year"].min()),
        "filing_year_max": int(sample["filing_year"].max()),
        "ai_filing_count": int(sample["is_ai_filing"].sum()),
        "mismatch_share_ai_filings": float(
            sample.loc[sample["is_ai_filing"], "PatentMismatch"].mean()
        ),
        "difference_in_means": diff_rows,
        "regressions": regression_rows,
        "event_summary_days": event_summary.to_dict(orient="records"),
        "car_m5_p5_available": has_m5,
    }


def _copy_exports(run_dir: Path, paper_root: Path, run_id: str) -> dict[str, str]:
    exports = {
        "figure_png": paper_root / "figures" / f"{TEST_ID}_{run_id}.png",
        "figure_pdf": paper_root / "figures" / f"{TEST_ID}_{run_id}.pdf",
        "table_csv": paper_root / "tables" / f"{TEST_ID}_{run_id}.csv",
        "table_md": paper_root / "tables" / f"{TEST_ID}_{run_id}.md",
        "table_tex": paper_root / "latex" / f"{TEST_ID}_{run_id}.tex",
        "table_docx": paper_root / "docx" / f"{TEST_ID}_{run_id}.docx",
        "event_window_summary": paper_root
        / "tables"
        / f"{TEST_ID}_{run_id}_event_window_summary.csv",
        "writer_packet": paper_root / "writer_packets" / f"{TEST_ID}_{run_id}.md",
        "result_notes": paper_root / "snippets" / f"{TEST_ID}_{run_id}_result_notes.md",
    }
    for path in exports.values():
        path.parent.mkdir(parents=True, exist_ok=True)

    mapping = {
        run_dir / "figure_main.png": exports["figure_png"],
        run_dir / "figure_main.pdf": exports["figure_pdf"],
        run_dir / "table_main.csv": exports["table_csv"],
        run_dir / "table_main.md": exports["table_md"],
        run_dir / "table_main.tex": exports["table_tex"],
        run_dir / "table_main.docx": exports["table_docx"],
        run_dir / "event_window_summary.csv": exports["event_window_summary"],
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

    sample = _build_analysis_sample(args.event_panel, args.annual_panel)
    diff_rows = []
    for dependent, label in [("car_m1_p1", "CAR[-1,+1]"), ("car_m2_p2", "CAR[-2,+2]")]:
        result = _difference_in_means(sample, dependent)
        result["window_label"] = label
        diff_rows.append(result)

    regression_rows = [_fit_regression(sample, spec) for spec in REGRESSION_SPECS]
    event_summary = _event_window_summary(sample, args.daily_returns)
    has_m5 = False

    table_rows = []
    for row in diff_rows:
        table_rows.append(
            {
                "panel": "A",
                "window": row["window_label"],
                "metric": "diff_mismatch_minus_non",
                "value": row["diff_mismatch_minus_non"],
                "p_value": row["p_value"],
                "n_total": row["n_total"],
            }
        )
    for row in regression_rows:
        for term in FOCAL_TERMS:
            values = row["focal_terms"][term]
            table_rows.append(
                {
                    "panel": "B",
                    "window": row["title"],
                    "metric": term,
                    "coef": values["coef"],
                    "se": values["se"],
                    "p_value": values["p_value"],
                    "nobs": row["nobs"],
                    "r_squared": row["r_squared"],
                }
            )
    pd.DataFrame(table_rows).to_csv(run_dir / "table_main.csv", index=False)

    table_md, table_tex = _render_table_outputs(diff_rows, regression_rows)
    (run_dir / "table_main.md").write_text(table_md, encoding="utf-8")
    (run_dir / "table_main.tex").write_text(table_tex, encoding="utf-8")
    _build_table_docx(diff_rows, regression_rows, run_dir / "table_main.docx", has_m5=has_m5)
    event_summary.to_csv(run_dir / "event_window_summary.csv", index=False)
    png_path, pdf_path = _plot_event_figure(event_summary, run_dir / "figure_main")

    (run_dir / "result_notes.md").write_text(
        _result_notes(diff_rows, regression_rows, has_m5), encoding="utf-8"
    )
    (run_dir / "writer_packet.md").write_text(
        _writer_packet(args, sample, diff_rows, regression_rows, has_m5), encoding="utf-8"
    )

    dataset_summary = _dataset_summary(
        sample,
        diff_rows,
        regression_rows,
        event_summary,
        args=args,
        has_m5=has_m5,
    )
    (run_dir / "dataset_summary.json").write_text(
        json.dumps(dataset_summary, indent=2), encoding="utf-8"
    )

    paper_exports = _copy_exports(run_dir, args.paper_root, args.run_id)
    manifest = {
        "test_id": TEST_ID,
        "run_id": args.run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "module_path": MODULE_PATH,
        "inputs": {
            "event_panel": str(args.event_panel),
            "annual_panel": str(args.annual_panel),
            "daily_returns": str(args.daily_returns),
        },
        "run_dir": str(run_dir),
        "outputs": {
            "dataset_summary": str(run_dir / "dataset_summary.json"),
            "table_csv": str(run_dir / "table_main.csv"),
            "table_md": str(run_dir / "table_main.md"),
            "table_tex": str(run_dir / "table_main.tex"),
            "table_docx": str(run_dir / "table_main.docx"),
            "event_window_summary": str(run_dir / "event_window_summary.csv"),
            "figure_png": str(png_path),
            "figure_pdf": str(pdf_path),
            "writer_packet": str(run_dir / "writer_packet.md"),
            "result_notes": str(run_dir / "result_notes.md"),
        },
        "paper_exports": paper_exports,
    }
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"[{TEST_ID}] wrote run bundle to {run_dir}")
    print(f"[{TEST_ID}] paper figure: {paper_exports['figure_png']}")


if __name__ == "__main__":
    main()
