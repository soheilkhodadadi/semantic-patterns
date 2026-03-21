"""Generate standalone delivery-phase table artifacts.

This module keeps preliminary delivery tables modular so they can be regenerated
independently of the full paper build.
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import statistics
from pathlib import Path


TABLE1_VARS: list[tuple[str, str]] = [
    ("n_A", "Actionable AI sentences"),
    ("n_S", "Speculative AI sentences"),
    ("n_I", "Irrelevant AI sentences"),
    ("AI_Focus", "AI disclosure intensity, log(1 + AI sentences)"),
    ("share_A", "Actionable share of AI sentences"),
    ("share_S", "Speculative share of AI sentences"),
    ("CredAI", "Credibility index, z(A) - z(S)"),
    ("A_S", "Actionable-to-speculative ratio, log(1 + A / (1 + S))"),
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


def _write_text(path: str | Path, text: str) -> None:
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    payload = text.rstrip() + "\n"
    temp_path = resolved.with_suffix(resolved.suffix + ".tmp")
    temp_path.write_text(payload, encoding="utf-8")
    os.replace(temp_path, resolved)


def _split_csv_arg(raw_value: str) -> set[str]:
    return {item.strip().lower() for item in raw_value.split(",") if item.strip()}


def _fmt_num(value: float | None, digits: int = 3) -> str:
    if value is None or math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def _sig_band(pvalue: float | None) -> str:
    if pvalue is None or math.isnan(pvalue):
        return "unstable"
    if pvalue < 0.01:
        return "1%"
    if pvalue < 0.05:
        return "5%"
    if pvalue < 0.10:
        return "10%"
    return "n.s."


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


def _to_markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


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


def build_table_1(panel_path: str | Path) -> str:
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

    rows: list[list[str]] = []
    for column, definition in TABLE1_VARS:
        arr = values[column]
        arr.sort()
        nobs = len(arr)
        mean = sum(arr) / nobs if nobs else float("nan")
        sd = statistics.stdev(arr) if nobs > 1 else float("nan")
        rows.append(
            [
                column,
                definition,
                f"{nobs:,}",
                _fmt_num(mean),
                _fmt_num(sd),
                _fmt_num(_quantile(arr, 0.25)),
                _fmt_num(_quantile(arr, 0.50)),
                _fmt_num(_quantile(arr, 0.75)),
            ]
        )

    table = _to_markdown_table(
        ["Variable", "Definition", "N", "Mean", "SD", "P25", "Median", "P75"],
        rows,
    )
    note = (
        "\nNotes: Summary statistics are computed on the regression-ready `2016–2024` firm-year sample. "
        "Variable-specific `N` varies because some control variables have missing values. "
        "This table is intended for the main text.\n"
    )
    return table + note


def _load_coeff_lookup(coeff_path: str | Path) -> dict[tuple[str, str], tuple[float, float | None, int | None]]:
    lookup: dict[tuple[str, str], tuple[float, float | None, int | None]] = {}
    with Path(coeff_path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            model = row.get("model", "")
            term = row.get("term", "")
            try:
                coef = float(row["coef"])
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
            lookup[(model, term)] = (coef, pvalue, nobs)
    return lookup


def build_table_2(coeff_path: str | Path) -> str:
    lookup = _load_coeff_lookup(coeff_path)
    row_specs = [
        (
            "Any AI patent in t+1",
            "Actionable disclosure (dummy)",
            "portfolio_lpm_anypat_k1_actionable_only_fe",
            "has_actionable",
            "Firm + year FE",
            "full",
        ),
        (
            "Any AI patent in t+1",
            "Speculative-only disclosure (dummy)",
            "portfolio_lpm_anypat_k1_speculative_only_fe",
            "has_spec_only",
            "Firm + year FE",
            "full",
        ),
        (
            "Any AI patent in t+1",
            "Speculative share",
            "portfolio_lpm_anypat_k1_shares_fe",
            "SpecShare",
            "Firm + year FE",
            "full",
        ),
    ]

    rows: list[list[str]] = []
    for outcome, focal, model_id, term, fe_label, sample in row_specs:
        coef, pvalue, nobs = lookup.get((model_id, term), (float("nan"), None, None))
        rows.append(
            [
                outcome,
                focal,
                fe_label,
                sample,
                f"{coef:.3f}{_sig_stars(pvalue)}" if not math.isnan(coef) else "",
                _fmt_num(pvalue),
                _sig_band(pvalue),
                f"{nobs:,}" if nobs is not None else "",
            ]
        )

    table = _to_markdown_table(
        ["Outcome", "Focal variable", "FE", "Sample", "Coef.", "p-value", "Sig.", "N"],
        rows,
    )
    note = (
        "\nNotes: Each row is a separate regression. The dependent variable is an indicator for whether the firm has any AI patent in `t+1`. "
        "All rows use the same control set: `ln_assets`, `leverage`, `cash`, `rd_intensity`, `capx_at`, `roa`, `sales_growth`, and `emp`. "
        "Standard errors are clustered at the firm level. Constants are omitted from the displayed table. "
        "This table is intended for the main text as the first patent-validation table.\n"
    )
    return table + note


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--panel",
        default="data/processed/panel/panel_reg_ready_2016_2024_applied_v2_legalnorm_unique.csv",
    )
    parser.add_argument(
        "--portfolio-coeffs",
        default="results/01_baseline/tables_2016_2024_applied_v2_legalnorm_unique/portfolio_coefficients.csv",
    )
    parser.add_argument("--output-dir", default="paper/generated/tables")
    parser.add_argument(
        "--tables",
        default="table1,table2",
        help="Comma-separated list of tables to generate: table1, table2",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    selected = _split_csv_arg(args.tables)

    if "table1" in selected:
        _write_text(
            Path(args.output_dir) / "table_1_summary_statistics_prelim_v1.md",
            build_table_1(args.panel),
        )

    if "table2" in selected:
        _write_text(
            Path(args.output_dir) / "table_2_core_patent_validation_prelim_v1.md",
            build_table_2(args.portfolio_coeffs),
        )

    print(f"[delivery-tables] wrote selected tables under {args.output_dir}")


if __name__ == "__main__":
    main()
