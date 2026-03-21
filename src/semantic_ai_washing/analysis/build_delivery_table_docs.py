"""Build standalone journal-style DOCX tables for preliminary delivery."""

from __future__ import annotations

import argparse
import csv
import math
import os
import statistics
from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


REPO_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_MERGED_PANEL = (
    "data/processed/panel/panel_ai_patents_controls_2016_2024_applied_v2_legalnorm_unique.csv"
)
DEFAULT_REG_READY_PANEL = (
    "data/processed/panel/panel_reg_ready_2016_2024_applied_v2_legalnorm_unique.csv"
)
DEFAULT_PORTFOLIO_COEFFS = (
    "results/01_baseline/tables_2016_2024_applied_v2_legalnorm_unique/portfolio_coefficients.csv"
)
DEFAULT_OUTPUT_DIR = "output/doc/delivery_tables_v1"

TABLE1_VARS: list[tuple[str, str]] = [
    ("n_A", "Actionable AI sentences"),
    ("n_S", "Speculative AI sentences"),
    ("n_I", "Irrelevant AI sentences"),
    ("AI_Focus", "AI focus"),
    ("share_A", "Actionable share"),
    ("share_S", "Speculative share"),
    ("CredAI", "CredAI"),
    ("A_S", "Actionable/speculative ratio"),
    ("patents_ai", "AI patents"),
    ("patents_total", "Total patents"),
    ("ln_assets", "Log assets"),
    ("leverage", "Leverage"),
    ("cash", "Cash/assets"),
    ("rd_intensity", "R&D/assets"),
    ("capx_at", "CAPX/assets"),
    ("roa", "Return on assets"),
    ("sales_growth", "Sales growth"),
    ("emp", "Employees"),
]


def _split_csv_arg(raw_value: str) -> set[str]:
    return {item.strip().lower() for item in raw_value.split(",") if item.strip()}


def _fmt_num(value: float | None, digits: int = 3) -> str:
    if value is None or math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def _sig_stars(pvalue: float | None) -> str:
    if pvalue is None or math.isnan(pvalue):
        return ""
    if pvalue < 0.01:
        return "***"
    if pvalue < 0.05:
        return "**"
    if pvalue < 0.10:
        return "*"
    return ""


def _quantile(values: list[float], p: float) -> float:
    if not values:
        return float("nan")
    n = len(values)
    k = (n - 1) * p
    floor_i = math.floor(k)
    ceil_i = math.ceil(k)
    if floor_i == ceil_i:
        return values[int(k)]
    return values[floor_i] * (ceil_i - k) + values[ceil_i] * (k - floor_i)


def _load_coeff_lookup(
    coeff_path: str | Path,
) -> dict[tuple[str, str], tuple[float, float, float | None, int | None]]:
    lookup: dict[tuple[str, str], tuple[float, float, float | None, int | None]] = {}
    with Path(coeff_path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            model = row.get("model", "")
            term = row.get("term", "")
            try:
                coef = float(row["coef"])
                se = float(row["se"])
            except (TypeError, ValueError):
                continue
            try:
                pvalue = float(row["p"]) if row.get("p", "") not in {"", None} else None
            except ValueError:
                pvalue = None
            try:
                nobs = int(float(row["N"])) if row.get("N", "") not in {"", None} else None
            except ValueError:
                nobs = None
            lookup[(model, term)] = (coef, se, pvalue, nobs)
    return lookup


def _summarize_table_1(panel_path: str | Path) -> dict[str, object]:
    values: dict[str, list[float]] = {column: [] for column, _ in TABLE1_VARS}
    with Path(panel_path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            for column, _ in TABLE1_VARS:
                raw = row.get(column, "")
                if raw in {"", None}:
                    continue
                try:
                    value = float(raw)
                except ValueError:
                    continue
                if math.isnan(value) or math.isinf(value):
                    continue
                values[column].append(value)

    rows: list[dict[str, str]] = []
    for column, label in TABLE1_VARS:
        arr = values[column]
        arr.sort()
        nobs = len(arr)
        mean = sum(arr) / nobs if nobs else float("nan")
        sd = statistics.stdev(arr) if nobs > 1 else float("nan")
        rows.append(
            {
                "Variable": label,
                "Mean": _fmt_num(mean),
                "Std. Dev.": _fmt_num(sd),
                "p5": _fmt_num(_quantile(arr, 0.05)),
                "p25": _fmt_num(_quantile(arr, 0.25)),
                "p50": _fmt_num(_quantile(arr, 0.50)),
                "p75": _fmt_num(_quantile(arr, 0.75)),
                "p95": _fmt_num(_quantile(arr, 0.95)),
                "N": f"{nobs:,}",
            }
        )

    note = (
        "This table presents summary statistics for the variables used in the analysis. "
        "It reports the mean, standard deviation, selected percentiles (p5, p25, p50, p75, and p95), "
        "and the number of observations (N) for the regression-ready 2016-2024 firm-year sample."
    )
    return {
        "title": "Table 1. Summary Statistics",
        "note": note,
        "rows": rows,
        "headers": ["Variable", "Mean", "Std. Dev.", "p5", "p25", "p50", "p75", "p95", "N"],
    }


def _summarize_table_2(coeff_path: str | Path) -> dict[str, object]:
    lookup = _load_coeff_lookup(coeff_path)
    models = [
        {
            "number": "(1)",
            "label": "Actionable-only",
            "model_id": "portfolio_lpm_anypat_k1_actionable_only_fe",
        },
        {
            "number": "(2)",
            "label": "Speculative-only",
            "model_id": "portfolio_lpm_anypat_k1_speculative_only_fe",
        },
        {
            "number": "(3)",
            "label": "Share model",
            "model_id": "portfolio_lpm_anypat_k1_shares_fe",
        },
    ]

    row_specs = [
        ("Actionable disclosure", ["has_actionable", None, None]),
        ("Speculative-only disclosure", [None, "has_spec_only", None]),
        ("Actionable share", [None, None, "ActShare"]),
        ("Speculative share", [None, None, "SpecShare"]),
    ]

    body_rows: list[dict[str, object]] = []
    footer_n: list[str] = []
    for label, terms in row_specs:
        coef_cells: list[str] = []
        se_cells: list[str] = []
        for model, term in zip(models, terms, strict=True):
            if term is None:
                coef_cells.append("")
                se_cells.append("")
                continue
            coef, se, pvalue, nobs = lookup.get(
                (model["model_id"], term), (float("nan"), float("nan"), None, None)
            )
            coef_cells.append(f"{coef:.3f}{_sig_stars(pvalue)}" if not math.isnan(coef) else "")
            se_cells.append(f"({se:.3f})" if not math.isnan(se) else "")
            footer_n.append(f"{nobs:,}" if nobs is not None else "")
        body_rows.append({"label": label, "cells": coef_cells, "kind": "coef"})
        body_rows.append({"label": "", "cells": se_cells, "kind": "se"})

    footer_rows = [
        {"label": "Controls", "cells": ["Y", "Y", "Y"]},
        {"label": "Firm FE", "cells": ["Y", "Y", "Y"]},
        {"label": "Year FE", "cells": ["Y", "Y", "Y"]},
        {"label": "Observations", "cells": footer_n[:3] if footer_n else ["", "", ""]},
    ]

    note = (
        "This table presents firm-year panel regressions analyzing whether AI disclosure composition predicts future AI patenting. "
        "The dependent variable is an indicator for whether the firm records any AI patent in t+1. "
        "Column (1) uses actionable disclosure, column (2) uses speculative-only disclosure, and column (3) uses the disclosure-share specification. "
        "Control variables include size, leverage, cash/assets, R&D/assets, CAPX/assets, ROA, sales growth, and employees. "
        "Firm and year fixed effects are included in all columns. Standard errors clustered at the firm level are shown in parentheses. "
        "Constants are omitted. (* p<0.1, ** p<0.05, *** p<0.01)."
    )
    return {
        "title": "Table 2. Disclosure Composition and Future AI Patenting",
        "note": note,
        "models": models,
        "dependent_label": "Any AI patent in t+1",
        "body_rows": body_rows,
        "footer_rows": footer_rows,
    }


def _set_run_font(run, *, size: float = 11, bold: bool = False, italic: bool = False) -> None:
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic


def _clear_cell(cell) -> None:
    cell.text = ""
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.space_before = Pt(0)


def _write_cell(cell, text: str, *, align: WD_ALIGN_PARAGRAPH, size: float = 10.5, bold: bool = False, italic: bool = False) -> None:
    _clear_cell(cell)
    paragraph = cell.paragraphs[0]
    paragraph.alignment = align
    run = paragraph.add_run(text)
    _set_run_font(run, size=size, bold=bold, italic=italic)
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


def _set_document_defaults(document: Document) -> None:
    section = document.sections[0]
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)
    normal = document.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    normal.font.size = Pt(11)


def _add_title(document: Document, title: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(8)
    run = paragraph.add_run(title)
    _set_run_font(run, size=16, bold=True)


def _add_note(document: Document, text: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.paragraph_format.space_after = Pt(10)
    run = paragraph.add_run(text)
    _set_run_font(run, size=11)


def _build_table_1_doc(panel_path: str | Path, output_path: str | Path) -> None:
    payload = _summarize_table_1(panel_path)
    document = Document()
    _set_document_defaults(document)
    _add_title(document, str(payload["title"]))
    _add_note(document, str(payload["note"]))

    headers: list[str] = payload["headers"]  # type: ignore[assignment]
    rows: list[dict[str, str]] = payload["rows"]  # type: ignore[assignment]
    table = document.add_table(rows=len(rows) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    _set_table_no_borders(table)

    widths = [2.6, 0.58, 0.72, 0.52, 0.52, 0.52, 0.52, 0.52, 0.58]
    for index, width in enumerate(widths):
        for row in table.rows:
            row.cells[index].width = Inches(width)

    for idx, header in enumerate(headers):
        _write_cell(
            table.rows[0].cells[idx],
            header,
            align=WD_ALIGN_PARAGRAPH.CENTER if idx > 0 else WD_ALIGN_PARAGRAPH.LEFT,
            size=10.5,
            bold=True,
        )
    _apply_row_rule(table.rows[0], top=True, bottom=True)

    for row_idx, row_payload in enumerate(rows, start=1):
        for col_idx, header in enumerate(headers):
            align = WD_ALIGN_PARAGRAPH.LEFT if col_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            _write_cell(
                table.rows[row_idx].cells[col_idx],
                row_payload[header],
                align=align,
                size=10.5,
            )
    _apply_row_rule(table.rows[-1], bottom=True)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    document.save(str(output_path))


def _build_table_2_doc(coeff_path: str | Path, output_path: str | Path) -> None:
    payload = _summarize_table_2(coeff_path)
    document = Document()
    _set_document_defaults(document)
    _add_title(document, str(payload["title"]))
    _add_note(document, str(payload["note"]))

    body_rows: list[dict[str, object]] = payload["body_rows"]  # type: ignore[assignment]
    footer_rows: list[dict[str, object]] = payload["footer_rows"]  # type: ignore[assignment]
    models: list[dict[str, str]] = payload["models"]  # type: ignore[assignment]

    total_rows = 2 + len(body_rows) + len(footer_rows)
    table = document.add_table(rows=total_rows, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    _set_table_no_borders(table)

    widths = [2.85, 1.05, 1.05, 1.05]
    for index, width in enumerate(widths):
        for row in table.rows:
            row.cells[index].width = Inches(width)

    _write_cell(
        table.rows[0].cells[0],
        "Variable",
        align=WD_ALIGN_PARAGRAPH.LEFT,
        size=10.5,
        bold=True,
    )
    merged = table.rows[0].cells[1].merge(table.rows[0].cells[3])
    _write_cell(
        merged,
        str(payload["dependent_label"]),
        align=WD_ALIGN_PARAGRAPH.CENTER,
        size=10.5,
        bold=True,
    )
    _apply_row_rule(table.rows[0], top=True)

    _write_cell(table.rows[1].cells[0], "", align=WD_ALIGN_PARAGRAPH.LEFT, size=10.5)
    for idx, model in enumerate(models, start=1):
        _write_cell(
            table.rows[1].cells[idx],
            model["number"],
            align=WD_ALIGN_PARAGRAPH.CENTER,
            size=10.5,
            bold=False,
        )
    _apply_row_rule(table.rows[1], bottom=True)

    cursor = 2
    for row_payload in body_rows:
        label = str(row_payload["label"])
        cells: list[str] = row_payload["cells"]  # type: ignore[assignment]
        is_se = row_payload.get("kind") == "se"
        _write_cell(
            table.rows[cursor].cells[0],
            label,
            align=WD_ALIGN_PARAGRAPH.LEFT,
            size=10.5,
            italic=is_se,
        )
        for idx, value in enumerate(cells, start=1):
            _write_cell(
                table.rows[cursor].cells[idx],
                value,
                align=WD_ALIGN_PARAGRAPH.CENTER,
                size=10.5,
                italic=is_se,
            )
        cursor += 1
    _apply_row_rule(table.rows[cursor - 1], bottom=True)

    for footer in footer_rows:
        _write_cell(
            table.rows[cursor].cells[0],
            str(footer["label"]),
            align=WD_ALIGN_PARAGRAPH.LEFT,
            size=10.5,
        )
        for idx, value in enumerate(footer["cells"], start=1):  # type: ignore[index]
            _write_cell(
                table.rows[cursor].cells[idx],
                str(value),
                align=WD_ALIGN_PARAGRAPH.CENTER,
                size=10.5,
            )
        cursor += 1
    _apply_row_rule(table.rows[cursor - 1], bottom=True)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    document.save(str(output_path))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--merged-panel", default=DEFAULT_MERGED_PANEL)
    parser.add_argument("--reg-ready-panel", default=DEFAULT_REG_READY_PANEL)
    parser.add_argument("--portfolio-coeffs", default=DEFAULT_PORTFOLIO_COEFFS)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--tables",
        default="table1,table2",
        help="Comma-separated list of standalone tables to build: table1, table2",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    selected = _split_csv_arg(args.tables)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if "table1" in selected:
        _build_table_1_doc(
            args.reg_ready_panel,
            output_dir / "table_1_summary_statistics_prelim_v1.docx",
        )

    if "table2" in selected:
        _build_table_2_doc(
            args.portfolio_coeffs,
            output_dir / "table_2_core_patent_validation_prelim_v1.docx",
        )

    print(f"[delivery-table-docs] wrote selected DOCX tables under {output_dir}")


if __name__ == "__main__":
    main()
