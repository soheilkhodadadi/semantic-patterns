"""Generate standalone delivery-phase table artifacts."""

from __future__ import annotations

import argparse
import csv
import math
import os
from pathlib import Path

from semantic_ai_washing.analysis.delivery_table_payloads import (
    fmt_num,
    sig_stars,
    summarize_table_1,
    summarize_table_2_timing_focus,
    summarize_table_2_timing_focus_counts,
    summarize_table_3_timing_composition,
    summarize_table_3_timing_composition_counts,
    summarize_table_4_spec_ladder_tplus1,
    summarize_table_4b_spec_ladder_t,
    to_markdown_table,
)

DEFAULT_PANEL = "data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv"
DEFAULT_PORTFOLIO_COEFFS = (
    "results/01_baseline/tables_2016_2024_applied_v2_legalnorm_unique/portfolio_coefficients.csv"
)
DEFAULT_OUTPUT_DIR = "paper/generated/tables"


def _write_text(path: str | Path, text: str) -> None:
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    payload = text.rstrip() + "\n"
    temp_path = resolved.with_suffix(resolved.suffix + ".tmp")
    temp_path.write_text(payload, encoding="utf-8")
    os.replace(temp_path, resolved)


def _split_csv_arg(raw_value: str) -> set[str]:
    return {item.strip().lower() for item in raw_value.split(",") if item.strip()}


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


def _render_table_1_markdown(payload: dict[str, object]) -> str:
    headers: list[str] = payload["headers"]  # type: ignore[assignment]
    rows: list[dict[str, str]] = payload["rows"]  # type: ignore[assignment]
    body = [[row[header] for header in headers] for row in rows]
    return to_markdown_table(headers, body) + "\nNotes: " + str(payload["note"]) + "\n"


def _render_conditional_appendix_table(coeff_path: str | Path) -> str:
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
                f"{coef:.3f}{sig_stars(pvalue)}" if not math.isnan(coef) else "",
                fmt_num(pvalue),
                f"{nobs:,}" if nobs is not None else "",
            ]
        )
    table = to_markdown_table(
        ["Outcome", "Focal variable", "FE", "Sample", "Coef.", "p-value", "N"], rows
    )
    note = (
        "Notes: Each row is a separate regression estimated on the narrower AI-speaking panel. "
        "The dependent variable is an indicator for whether the firm has any AI patent in t+1. "
        "All rows use the same control set and firm-clustered standard errors. "
        "Constants are omitted from the displayed table. This table now belongs in the appendix as a conditional validation check."
    )
    return table + "\n" + note + "\n"


def _render_timing_payload_markdown(payload: dict[str, object]) -> str:
    models: list[dict[str, str]] = payload["models"]  # type: ignore[assignment]
    panels: list[dict[str, object]] = payload["panels"]  # type: ignore[assignment]
    sections: list[str] = [f"## {payload['title']}\n", str(payload["note"]), ""]

    headers = ["Variable", *[model["label"] for model in models]]
    for panel in panels:
        heading = panel.get("heading")
        if heading:
            sections.append(f"### {heading}\n")
        rows = [
            [str(panel["label"]), *list(panel["coef_cells"])],
            ["", *list(panel["se_cells"])],
        ]
        for footer in panel["footer_rows"]:  # type: ignore[index]
            rows.append([str(footer["label"]), *[str(cell) for cell in footer["cells"]]])
        sections.append(to_markdown_table(headers, rows))
    return "\n".join(sections).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", default=DEFAULT_PANEL)
    parser.add_argument("--portfolio-coeffs", default=DEFAULT_PORTFOLIO_COEFFS)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--tables",
        default="table1,table2_timing_focus,table3_timing_composition",
        help=(
            "Comma-separated list of tables to generate: table1, table2_timing_focus, "
            "table2_timing_focus_count, table3_timing_composition, "
            "table3_timing_composition_count, table4_spec_ladder_tplus1, "
            "table4b_spec_ladder_t, table2_conditional_appendix"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    selected = _split_csv_arg(args.tables)
    output_dir = Path(args.output_dir)

    if "table1" in selected:
        _write_text(
            output_dir / "table_1_summary_statistics_prelim_v1.md",
            _render_table_1_markdown(summarize_table_1(args.panel)),
        )

    if "table2_timing_focus" in selected:
        _write_text(
            output_dir / "table_2_ai_focus_timing_prelim_v1.md",
            _render_timing_payload_markdown(summarize_table_2_timing_focus(args.panel)),
        )

    if "table2_timing_focus_count" in selected:
        _write_text(
            output_dir / "table_2b_ai_focus_timing_counts_prelim_v1.md",
            _render_timing_payload_markdown(summarize_table_2_timing_focus_counts(args.panel)),
        )

    if "table3_timing_composition" in selected:
        _write_text(
            output_dir / "table_3_disclosure_composition_timing_prelim_v1.md",
            _render_timing_payload_markdown(summarize_table_3_timing_composition(args.panel)),
        )

    if "table3_timing_composition_count" in selected:
        _write_text(
            output_dir / "table_3b_disclosure_composition_timing_counts_prelim_v1.md",
            _render_timing_payload_markdown(summarize_table_3_timing_composition_counts(args.panel)),
        )

    if "table4_spec_ladder_tplus1" in selected:
        _write_text(
            output_dir / "table_4_spec_ladder_tplus1_prelim_v1.md",
            _render_timing_payload_markdown(summarize_table_4_spec_ladder_tplus1(args.panel)),
        )

    if "table4b_spec_ladder_t" in selected:
        _write_text(
            output_dir / "table_4b_spec_ladder_t_prelim_v1.md",
            _render_timing_payload_markdown(summarize_table_4b_spec_ladder_t(args.panel)),
        )

    if "table2_conditional_appendix" in selected:
        _write_text(
            output_dir / "table_2_core_patent_validation_prelim_v1.md",
            _render_conditional_appendix_table(args.portfolio_coeffs),
        )

    print(f"[delivery-tables] wrote selected tables under {args.output_dir}")


if __name__ == "__main__":
    main()
