"""Publication run driver for legacy Table R1: expanded summary statistics."""

from __future__ import annotations

import argparse
import json
import math
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

from semantic_ai_washing.analysis.delivery_table_payloads import _add_patent_mismatch
from semantic_ai_washing.analysis.publication_runs.test_03_post_filing_drift import (
    _add_note,
    _add_title,
    _apply_row_rule,
    _set_document_defaults,
    _set_landscape,
    _set_run_font,
    _set_table_no_borders,
    _write_cell,
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
DEFAULT_MARKET_FEATURES = (
    REPO_ROOT
    / "data/interim/market/annual_market_features_ever_speaker_2016_2025_hybrid_api_a_conf49_v1.csv"
)
DEFAULT_TEST_ROOT = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/test_runs/legacy_r1_summary_stats"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_hybrid_api_a_conf49_main_v2"
TEST_ID = "legacy_r1_summary_stats"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.legacy_r1_summary_stats"

ANNUAL_VAR_DEFS: list[tuple[str, str]] = [
    ("n_total", "Total AI sentences per firm-year"),
    ("n_A", "Actionable AI sentences per firm-year"),
    ("n_S", "Speculative AI sentences per firm-year"),
    ("n_I", "Irrelevant AI sentences per firm-year"),
    ("AI_Focus", "AI focus"),
    ("share_A", "Actionable share"),
    ("share_S", "Speculative share"),
    ("CredAI", "CredAI"),
    ("A_S", "A/S ratio"),
    ("PatentMismatch", "PatentMismatch"),
    ("patents_ai", "AI patents"),
    ("patents_total", "Total patents"),
    ("ln_assets", "Log assets"),
    ("leverage", "Leverage"),
    ("cash", "Cash/assets"),
    ("rd_intensity", "R&D/assets"),
    ("capx_at", "CAPX/assets"),
    ("roa", "ROA"),
    ("sales_growth", "Sales growth"),
    ("emp", "Employees"),
]

MARKET_VAR_DEFS: list[tuple[str, str]] = [
    ("log_mktcap_assets", "Log MktCap/assets"),
    ("log_q_proxy", "Log Q proxy"),
    ("delta_log_q_proxy_lead1", "Delta log Q t+1"),
    ("share_growth_lead1", "Delta shares t+1"),
    ("equity_issue_lead1", "Issue >5% t+1"),
]

EVENT_VAR_DEFS: list[tuple[str, str]] = [
    ("n_ai_total", "Total AI sentences per filing"),
    ("n_actionable", "Actionable AI sentences per filing"),
    ("n_speculative", "Speculative AI sentences per filing"),
    ("share_actionable", "Actionable share per filing"),
    ("share_speculative", "Speculative share per filing"),
    ("car_m1_p1", "CAR[-1,+1]"),
    ("bhar_1m", "BHAR[+2,+21]"),
    ("bhar_3m", "BHAR[+2,+63]"),
    ("bhar_6m", "BHAR[+2,+126]"),
    ("bhar_12m", "BHAR[+2,+252]"),
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annual-panel", type=Path, default=DEFAULT_ANNUAL_PANEL)
    parser.add_argument("--event-panel", type=Path, default=DEFAULT_EVENT_PANEL)
    parser.add_argument("--market-features", type=Path, default=DEFAULT_MARKET_FEATURES)
    parser.add_argument("--test-root", type=Path, default=DEFAULT_TEST_ROOT)
    parser.add_argument("--paper-root", type=Path, default=DEFAULT_PAPER_ROOT)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    return parser.parse_args()


def _fmt_num(value: float | int | None, digits: int = 3) -> str:
    if value is None:
        return ""
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return ""
    if not math.isfinite(numeric):
        return ""
    return f"{numeric:.{digits}f}"


def _normalize_id(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
        .replace({"nan": "", "None": ""})
    )


def _finite_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan)


def _ensure_sic2(df: pd.DataFrame) -> pd.DataFrame:
    panel = df.copy()
    if "sic2" not in panel.columns or panel["sic2"].isna().all():
        if "sic" in panel.columns:
            sic_raw = pd.to_numeric(panel["sic"], errors="coerce")
            panel["sic2"] = (sic_raw // 100).astype("Int64")
        else:
            panel["sic2"] = pd.Series(pd.NA, index=panel.index, dtype="Int64")
    return panel


def _winsorize(series: pd.Series, lower_q: float = 0.01, upper_q: float = 0.99) -> pd.Series:
    valid = _finite_numeric(series)
    if valid.notna().sum() == 0:
        return valid
    lower = valid.quantile(lower_q)
    upper = valid.quantile(upper_q)
    return valid.clip(lower=lower, upper=upper)


def _coverage_rows(
    annual: pd.DataFrame, annual_market: pd.DataFrame, event: pd.DataFrame
) -> tuple[pd.DataFrame, dict[str, object]]:
    ai_talk_rows = int(_finite_numeric(annual["any_ai_talk"]).fillna(0).sum())
    n_total = _finite_numeric(annual["n_total"]).fillna(0)
    n_actionable = _finite_numeric(annual["n_A"]).fillna(0)
    n_speculative = _finite_numeric(annual["n_S"]).fillna(0)
    n_irrelevant = _finite_numeric(annual["n_I"]).fillna(0)
    firm_year_rows = int(len(annual))
    unique_firms = int(annual["cik"].astype(str).nunique())
    year_min = int(_finite_numeric(annual["year"]).min())
    year_max = int(_finite_numeric(annual["year"]).max())
    filing_rows = int(len(event))
    filing_firms = int(event["cik"].astype(str).nunique()) if "cik" in event.columns else 0

    rows = [
        {
            "Metric": "Ever-speaker firms",
            "Value": f"{unique_firms:,}",
            "Notes": "Unique CIKs in the canonical annual panel.",
        },
        {
            "Metric": "Firm-year observations",
            "Value": f"{firm_year_rows:,}",
            "Notes": f"Annual panel coverage for {year_min}-{year_max}.",
        },
        {
            "Metric": "AI-talking firm-years",
            "Value": f"{ai_talk_rows:,}",
            "Notes": "Firm-years with at least one classified AI sentence.",
        },
        {
            "Metric": "Total classified AI sentences",
            "Value": f"{int(n_total.sum()):,}",
            "Notes": "Corpus total across the 2016-2025 ever-speaker panel.",
        },
        {
            "Metric": "Actionable AI sentences",
            "Value": f"{int(n_actionable.sum()):,}",
            "Notes": "Corpus total.",
        },
        {
            "Metric": "Speculative AI sentences",
            "Value": f"{int(n_speculative.sum()):,}",
            "Notes": "Corpus total.",
        },
        {
            "Metric": "Irrelevant AI sentences",
            "Value": f"{int(n_irrelevant.sum()):,}",
            "Notes": "Corpus total.",
        },
        {
            "Metric": "Firm-years with Compustat controls",
            "Value": f"{int(_finite_numeric(annual['ln_assets']).notna().sum()):,}",
            "Notes": "Non-missing log assets in the annual panel.",
        },
        {
            "Metric": "Firm-years with matched market cap",
            "Value": f"{int(_finite_numeric(annual_market['market_cap_year_end']).notna().sum()):,}",
            "Notes": "Annual rows with merged CRSP market-cap data.",
        },
        {
            "Metric": "Filing-event observations",
            "Value": f"{filing_rows:,}",
            "Notes": f"Distinct filing events across {filing_firms:,} firms.",
        },
        {
            "Metric": "Filing events with CAR[-1,+1]",
            "Value": f"{int(_finite_numeric(event['car_m1_p1']).notna().sum()):,}",
            "Notes": "Usable immediate-return events.",
        },
        {
            "Metric": "Filing events with BHAR[+2,+63]",
            "Value": f"{int(_finite_numeric(event['bhar_3m']).notna().sum()):,}",
            "Notes": "Usable 3-month drift events.",
        },
        {
            "Metric": "Filing events with BHAR[+2,+252]",
            "Value": f"{int(_finite_numeric(event['bhar_12m']).notna().sum()):,}",
            "Notes": "Usable 12-month drift events.",
        },
    ]
    metadata = {
        "panel_rows": firm_year_rows,
        "unique_firms": unique_firms,
        "year_min": year_min,
        "year_max": year_max,
        "ai_talk_rows": ai_talk_rows,
        "corpus_total_sentences": int(n_total.sum()),
        "corpus_actionable_sentences": int(n_actionable.sum()),
        "corpus_speculative_sentences": int(n_speculative.sum()),
        "corpus_irrelevant_sentences": int(n_irrelevant.sum()),
        "event_rows": filing_rows,
        "event_unique_firms": filing_firms,
        "fundamentals_rows": int(_finite_numeric(annual["ln_assets"]).notna().sum()),
        "marketcap_rows": int(_finite_numeric(annual_market["market_cap_year_end"]).notna().sum()),
        "car_rows": int(_finite_numeric(event["car_m1_p1"]).notna().sum()),
        "bhar_3m_rows": int(_finite_numeric(event["bhar_3m"]).notna().sum()),
        "bhar_12m_rows": int(_finite_numeric(event["bhar_12m"]).notna().sum()),
    }
    return pd.DataFrame(rows), metadata


def _summary_table(
    df: pd.DataFrame, variable_defs: list[tuple[str, str]]
) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    rows: list[dict[str, str]] = []
    stats_payload: list[dict[str, object]] = []
    for column, label in variable_defs:
        if column not in df.columns:
            continue
        valid = _finite_numeric(df[column]).dropna().astype(float)
        nobs = int(valid.shape[0])
        rows.append(
            {
                "Variable": label,
                "Mean": _fmt_num(valid.mean() if nobs else None),
                "Std. Dev.": _fmt_num(valid.std(ddof=1) if nobs > 1 else None),
                "p5": _fmt_num(valid.quantile(0.05) if nobs else None),
                "p25": _fmt_num(valid.quantile(0.25) if nobs else None),
                "p50": _fmt_num(valid.quantile(0.50) if nobs else None),
                "p75": _fmt_num(valid.quantile(0.75) if nobs else None),
                "p95": _fmt_num(valid.quantile(0.95) if nobs else None),
                "N": f"{nobs:,}",
            }
        )
        stats_payload.append(
            {
                "variable": column,
                "label": label,
                "n": nobs,
                "mean": valid.mean() if nobs else None,
                "std": valid.std(ddof=1) if nobs > 1 else None,
                "p5": valid.quantile(0.05) if nobs else None,
                "p25": valid.quantile(0.25) if nobs else None,
                "p50": valid.quantile(0.50) if nobs else None,
                "p75": valid.quantile(0.75) if nobs else None,
                "p95": valid.quantile(0.95) if nobs else None,
            }
        )
    return pd.DataFrame(rows), stats_payload


def _load_annual_panel(annual_panel: Path, market_features: Path) -> pd.DataFrame:
    annual = pd.read_parquet(annual_panel).copy()
    annual = _ensure_sic2(annual)
    annual = _add_patent_mismatch(annual)
    annual["cik"] = _normalize_id(annual["cik"])
    annual["year"] = pd.to_numeric(annual["year"], errors="coerce").astype("Int64")
    annual["permno"] = _normalize_id(annual.get("permno", pd.Series("", index=annual.index)))

    market = pd.read_csv(market_features).copy()
    market["permno"] = _normalize_id(market["permno"])
    market["year"] = pd.to_numeric(market["year"], errors="coerce").astype("Int64")
    for column in ["shrout", "market_cap_year_end"]:
        market[column] = _finite_numeric(market[column])
    keep = ["permno", "year", "shrout", "market_cap_year_end"]
    annual = annual.merge(
        market[keep], on=["permno", "year"], how="left", suffixes=("", "_market")
    )

    annual["assets_proxy"] = np.exp(_finite_numeric(annual["ln_assets"]))
    annual.loc[
        ~np.isfinite(annual["assets_proxy"]) | annual["assets_proxy"].le(0), "assets_proxy"
    ] = np.nan
    annual["mktcap_assets"] = (
        _finite_numeric(annual["market_cap_year_end"]) / annual["assets_proxy"]
    )
    annual["q_proxy"] = annual["mktcap_assets"] + _finite_numeric(annual["leverage"])
    annual["log_mktcap_assets"] = np.log1p(annual["mktcap_assets"].clip(lower=0))
    annual["log_q_proxy"] = np.log1p(annual["q_proxy"].clip(lower=0))

    annual = annual.sort_values(["permno", "year", "cik"]).reset_index(drop=True)
    group_key = "permno" if annual["permno"].astype(str).str.len().gt(0).any() else "cik"
    shrout_lead1 = annual.groupby(group_key, sort=False)["shrout"].shift(-1)
    log_q_proxy_lead1 = annual.groupby("cik", sort=False)["log_q_proxy"].shift(-1)
    annual["share_growth_lead1"] = shrout_lead1 / annual["shrout"] - 1.0
    annual["equity_issue_lead1"] = np.where(
        annual["share_growth_lead1"].notna(),
        (annual["share_growth_lead1"] > 0.05).astype(float),
        np.nan,
    )
    annual["delta_log_q_proxy_lead1"] = log_q_proxy_lead1 - annual["log_q_proxy"]

    for column in [
        "log_mktcap_assets",
        "log_q_proxy",
        "delta_log_q_proxy_lead1",
        "share_growth_lead1",
    ]:
        annual[column] = _winsorize(annual[column])
    return annual


def _load_event_panel(event_panel: Path) -> pd.DataFrame:
    event = pd.read_parquet(event_panel).copy()
    if "cik" in event.columns:
        event["cik"] = _normalize_id(event["cik"])
    for column in [field for field, _ in EVENT_VAR_DEFS]:
        if column in event.columns:
            event[column] = _finite_numeric(event[column])
    return event


def _markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def _escape_tex(text: str) -> str:
    return (
        text.replace("\\", "\\textbackslash{}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("_", "\\_")
        .replace("#", "\\#")
    )


def _render_table_outputs(
    coverage_df: pd.DataFrame, annual_df: pd.DataFrame, event_df: pd.DataFrame
) -> tuple[str, str, pd.DataFrame]:
    stats_headers = ["Variable", "Mean", "Std. Dev.", "p5", "p25", "p50", "p75", "p95", "N"]
    coverage_headers = ["Metric", "Value", "Notes"]
    combined_rows: list[dict[str, object]] = []

    for row in coverage_df.to_dict("records"):
        combined_rows.append({"panel": "A", "row_label": row["Metric"], **row})
    for row in annual_df.to_dict("records"):
        combined_rows.append({"panel": "B", "row_label": row["Variable"], **row})
    for row in event_df.to_dict("records"):
        combined_rows.append({"panel": "C", "row_label": row["Variable"], **row})
    combined_df = pd.DataFrame(combined_rows)

    md_parts = [
        "# Table Main",
        "",
        "## Panel A. Coverage and corpus totals",
        "",
        _markdown_table(coverage_headers, coverage_df[coverage_headers].values.tolist()),
        "",
        "## Panel B. Annual-panel variables",
        "",
        _markdown_table(stats_headers, annual_df[stats_headers].values.tolist()),
        "",
        "## Panel C. Event-study and market variables",
        "",
        _markdown_table(stats_headers, event_df[stats_headers].values.tolist()),
        "",
    ]

    latex_lines = [
        "\\begin{table}[!htbp]",
        "\\centering",
        "\\scriptsize",
        "\\caption{Expanded-panel summary statistics and sample coverage}",
        "\\textit{Panel A. Coverage and corpus totals}\\\\",
        "\\begin{tabular}{p{0.28\\textwidth}p{0.12\\textwidth}p{0.48\\textwidth}}",
        "\\hline",
        "Metric & Value & Notes \\\\",
        "\\hline",
    ]
    for row in coverage_df[coverage_headers].values.tolist():
        latex_lines.append(" & ".join(_escape_tex(str(value)) for value in row) + " \\\\")
    latex_lines.extend(
        [
            "\\hline",
            "\\end{tabular}",
            "\\vspace{0.4em}",
            "\\\\textit{Panel B. Annual-panel variables}\\\\",
            "\\begin{tabular}{lcccccccc}",
            "\\hline",
            "Variable & Mean & Std. Dev. & p5 & p25 & p50 & p75 & p95 & N \\\\",
            "\\hline",
        ]
    )
    for row in annual_df[stats_headers].values.tolist():
        latex_lines.append(" & ".join(_escape_tex(str(value)) for value in row) + " \\\\")
    latex_lines.extend(
        [
            "\\hline",
            "\\end{tabular}",
            "\\vspace{0.4em}",
            "\\\\textit{Panel C. Event-study and market variables}\\\\",
            "\\begin{tabular}{lcccccccc}",
            "\\hline",
            "Variable & Mean & Std. Dev. & p5 & p25 & p50 & p75 & p95 & N \\\\",
            "\\hline",
        ]
    )
    for row in event_df[stats_headers].values.tolist():
        latex_lines.append(" & ".join(_escape_tex(str(value)) for value in row) + " \\\\")
    latex_lines.extend(["\\hline", "\\end{tabular}", "\\end{table}"])

    return "\n".join(md_parts), "\n".join(latex_lines) + "\n", combined_df


def _table_rows(df: pd.DataFrame, headers: list[str]) -> list[list[tuple[str, bool]]]:
    rows: list[list[tuple[str, bool]]] = []
    for row in df[headers].itertuples(index=False):
        rows.append([(str(row[0]), True), *[(str(value), False) for value in row[1:]]])
    return rows


def _build_custom_table(
    document: Document,
    headers: list[str],
    rows: list[list[tuple[str, bool]]],
    widths: list[float],
) -> None:
    table = document.add_table(rows=len(rows) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    _set_table_no_borders(table)

    header_row = table.rows[0]
    for idx, header in enumerate(headers):
        header_row.cells[idx].width = Inches(widths[idx])
        _write_cell(
            header_row.cells[idx],
            header,
            align=WD_ALIGN_PARAGRAPH.CENTER if idx else WD_ALIGN_PARAGRAPH.LEFT,
            size=10.0,
            bold=True,
        )
    _apply_row_rule(header_row, top=True, bottom=True)

    for row_idx, row_values in enumerate(rows, start=1):
        row = table.rows[row_idx]
        for col_idx, (text, bold) in enumerate(row_values):
            row.cells[col_idx].width = Inches(widths[col_idx])
            _write_cell(
                row.cells[col_idx],
                text,
                align=WD_ALIGN_PARAGRAPH.CENTER
                if col_idx == 1 and len(headers) > 2
                else WD_ALIGN_PARAGRAPH.LEFT
                if col_idx == 0
                else WD_ALIGN_PARAGRAPH.CENTER,
                size=9.8,
                bold=bold,
            )
    _apply_row_rule(table.rows[-1], bottom=True)


def _add_panel_heading(document: Document, text: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(8)
    paragraph.paragraph_format.space_after = Pt(4)
    run = paragraph.add_run(text)
    _set_run_font(run, size=11, bold=True)


def _build_table_docx(
    coverage_df: pd.DataFrame, annual_df: pd.DataFrame, event_df: pd.DataFrame, output_path: Path
) -> None:
    document = Document()
    _set_document_defaults(document)
    _set_landscape(document)
    _add_title(document, "Table R1. Expanded Summary Statistics and Sample Coverage")
    _add_note(
        document,
        "Panel A reports sample coverage and corpus totals for the canonical 2016-2025 ever-speaker panel and the filing-event estimation sample. "
        "Panels B and C report distributional summary statistics for the paper's annual-panel variables and the market/event outcomes used in the updated finance tests. "
        "Sentence-count rows in Panels B and C are per observation counts, while the full sentence corpus totals are reported separately in Panel A.",
    )

    _add_panel_heading(document, "Panel A. Coverage and corpus totals")
    _build_custom_table(
        document,
        ["Metric", "Value", "Notes"],
        _table_rows(coverage_df, ["Metric", "Value", "Notes"]),
        [3.1, 1.4, 5.8],
    )

    _add_panel_heading(document, "Panel B. Annual-panel variables")
    _build_custom_table(
        document,
        ["Variable", "Mean", "Std. Dev.", "p5", "p25", "p50", "p75", "p95", "N"],
        _table_rows(
            annual_df, ["Variable", "Mean", "Std. Dev.", "p5", "p25", "p50", "p75", "p95", "N"]
        ),
        [2.6, 1.0, 1.0, 0.75, 0.75, 0.75, 0.75, 0.75, 0.9],
    )

    _add_panel_heading(document, "Panel C. Event-study and market variables")
    _build_custom_table(
        document,
        ["Variable", "Mean", "Std. Dev.", "p5", "p25", "p50", "p75", "p95", "N"],
        _table_rows(
            event_df, ["Variable", "Mean", "Std. Dev.", "p5", "p25", "p50", "p75", "p95", "N"]
        ),
        [2.6, 1.0, 1.0, 0.75, 0.75, 0.75, 0.75, 0.75, 0.9],
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.save(str(output_path))


def _result_notes(
    metadata: dict[str, object], annual_df: pd.DataFrame, event_df: pd.DataFrame
) -> str:
    def _get(df: pd.DataFrame, label: str, field: str) -> str:
        match = df.loc[df["Variable"].eq(label), field]
        return str(match.iloc[0]) if not match.empty else ""

    return "\n".join(
        [
            "# Result Notes",
            "",
            (
                f"- Expanded annual panel: `{metadata['panel_rows']:,}` firm-years across "
                f"`{metadata['unique_firms']:,}` ever-speaker firms from `{metadata['year_min']}` to `{metadata['year_max']}`."
            ),
            (
                f"- Corpus coverage is now explicit: `{metadata['corpus_total_sentences']:,}` total AI sentences, split into "
                f"`{metadata['corpus_actionable_sentences']:,}` actionable, "
                f"`{metadata['corpus_speculative_sentences']:,}` speculative, and "
                f"`{metadata['corpus_irrelevant_sentences']:,}` irrelevant sentences."
            ),
            (
                f"- Filing-event sample: `{metadata['event_rows']:,}` events across "
                f"`{metadata['event_unique_firms']:,}` firms; usable events = `CAR[-1,+1] {metadata['car_rows']:,}`, "
                f"`BHAR[+2,+63] {metadata['bhar_3m_rows']:,}`, `BHAR[+2,+252] {metadata['bhar_12m_rows']:,}`."
            ),
            (
                f"- The old ambiguity is fixed: sentence rows in Panels B/C are per-observation counts "
                f"(for example, mean total AI sentences per firm-year = `{_get(annual_df, 'Total AI sentences per firm-year', 'Mean')}`), "
                "while Panel A reports corpus totals."
            ),
            (
                f"- Mean filing-level AI disclosure is `{_get(event_df, 'Total AI sentences per filing', 'Mean')}` sentences, "
                f"with median `CAR[-1,+1]` = `{_get(event_df, 'CAR[-1,+1]', 'p50')}` and median `BHAR[+2,+63]` = `{_get(event_df, 'BHAR[+2,+63]', 'p50')}`."
            ),
            "",
        ]
    )


def _writer_packet(args: argparse.Namespace, metadata: dict[str, object]) -> str:
    return "\n".join(
        [
            "# Writer Packet",
            "",
            "## Metadata",
            f"- Test id: `{TEST_ID}`",
            f"- Run id: `{args.run_id}`",
            f"- Date run: `{date.today().isoformat()}`",
            f"- Script/module path: `{MODULE_PATH}`",
            f"- Annual panel: `{args.annual_panel}`",
            f"- Event panel: `{args.event_panel}`",
            f"- Market features: `{args.market_features}`",
            "",
            "## Sample",
            (
                f"- Annual ever-speaker panel: `{metadata['panel_rows']:,}` firm-years across "
                f"`{metadata['unique_firms']:,}` firms, `{metadata['year_min']}`-`{metadata['year_max']}`"
            ),
            f"- AI-talking firm-years: `{metadata['ai_talk_rows']:,}`",
            (
                f"- Classified AI-sentence corpus: `{metadata['corpus_total_sentences']:,}` total "
                f"(`{metadata['corpus_actionable_sentences']:,}` actionable, "
                f"`{metadata['corpus_speculative_sentences']:,}` speculative, "
                f"`{metadata['corpus_irrelevant_sentences']:,}` irrelevant)"
            ),
            f"- Filing-event sample: `{metadata['event_rows']:,}` events across `{metadata['event_unique_firms']:,}` firms",
            "",
            "## Caption Draft",
            "Panel A reports sample coverage and corpus totals for the canonical 2016-2025 ever-speaker panel and the filing-event estimation sample. Panels B and C report distributional summary statistics for the annual-panel variables and the market/event outcomes used in the updated finance tests. Sentence-count rows in Panels B and C are per observation counts, while the full sentence corpus totals are reported separately in Panel A.",
            "",
        ]
    )


def _dataset_summary(
    args: argparse.Namespace,
    metadata: dict[str, object],
    annual_stats: list[dict[str, object]],
    event_stats: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "test_id": TEST_ID,
        "run_id": args.run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "inputs": {
            "annual_panel": str(args.annual_panel),
            "event_panel": str(args.event_panel),
            "market_features": str(args.market_features),
        },
        "metadata": metadata,
        "annual_summary_stats": annual_stats,
        "event_summary_stats": event_stats,
    }


def _copy_exports(run_dir: Path, paper_root: Path, run_id: str) -> dict[str, str]:
    exports = {
        "table_csv": paper_root / "tables" / f"{TEST_ID}_{run_id}.csv",
        "table_md": paper_root / "tables" / f"{TEST_ID}_{run_id}.md",
        "table_tex": paper_root / "latex" / f"{TEST_ID}_{run_id}.tex",
        "table_docx": paper_root / "docx" / f"{TEST_ID}_{run_id}.docx",
        "writer_packet": paper_root / "writer_packets" / f"{TEST_ID}_{run_id}.md",
        "result_notes": paper_root / "snippets" / f"{TEST_ID}_{run_id}_result_notes.md",
    }
    for path in exports.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    for src_name, dst in {
        "table_main.csv": exports["table_csv"],
        "table_main.md": exports["table_md"],
        "table_main.tex": exports["table_tex"],
        "table_main.docx": exports["table_docx"],
        "writer_packet.md": exports["writer_packet"],
        "result_notes.md": exports["result_notes"],
    }.items():
        shutil.copy2(run_dir / src_name, dst)
    return {key: str(path) for key, path in exports.items()}


def main() -> None:
    args = _parse_args()
    run_dir = args.test_root / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    annual_market = _load_annual_panel(args.annual_panel, args.market_features)
    event = _load_event_panel(args.event_panel)
    coverage_df, metadata = _coverage_rows(annual_market, annual_market, event)
    annual_df, annual_stats = _summary_table(annual_market, [*ANNUAL_VAR_DEFS, *MARKET_VAR_DEFS])
    event_df, event_stats = _summary_table(event, EVENT_VAR_DEFS)

    table_md, table_tex, combined_df = _render_table_outputs(coverage_df, annual_df, event_df)
    combined_df.to_csv(run_dir / "table_main.csv", index=False)
    coverage_df.to_csv(run_dir / "panel_a_coverage.csv", index=False)
    annual_df.to_csv(run_dir / "panel_b_annual_summary.csv", index=False)
    event_df.to_csv(run_dir / "panel_c_event_summary.csv", index=False)
    (run_dir / "table_main.md").write_text(table_md, encoding="utf-8")
    (run_dir / "table_main.tex").write_text(table_tex, encoding="utf-8")
    _build_table_docx(coverage_df, annual_df, event_df, run_dir / "table_main.docx")
    (run_dir / "result_notes.md").write_text(
        _result_notes(metadata, annual_df, event_df), encoding="utf-8"
    )
    (run_dir / "writer_packet.md").write_text(_writer_packet(args, metadata), encoding="utf-8")
    dataset_summary = _dataset_summary(args, metadata, annual_stats, event_stats)
    (run_dir / "dataset_summary.json").write_text(
        json.dumps(dataset_summary, indent=2), encoding="utf-8"
    )

    paper_exports = _copy_exports(run_dir, args.paper_root, args.run_id)
    manifest = {
        "test_id": TEST_ID,
        "run_id": args.run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "module_path": MODULE_PATH,
        "run_dir": str(run_dir),
        "outputs": {
            "dataset_summary": str(run_dir / "dataset_summary.json"),
            "table_csv": str(run_dir / "table_main.csv"),
            "panel_a_coverage": str(run_dir / "panel_a_coverage.csv"),
            "panel_b_annual_summary": str(run_dir / "panel_b_annual_summary.csv"),
            "panel_c_event_summary": str(run_dir / "panel_c_event_summary.csv"),
            "table_md": str(run_dir / "table_main.md"),
            "table_tex": str(run_dir / "table_main.tex"),
            "table_docx": str(run_dir / "table_main.docx"),
            "writer_packet": str(run_dir / "writer_packet.md"),
            "result_notes": str(run_dir / "result_notes.md"),
        },
        "paper_exports": paper_exports,
    }
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[{TEST_ID}] wrote run bundle to {run_dir}")
    print(f"[{TEST_ID}] paper table: {paper_exports['table_docx']}")


if __name__ == "__main__":
    main()
