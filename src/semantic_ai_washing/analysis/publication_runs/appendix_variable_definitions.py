"""Publication run driver for appendix variable definitions."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches

from semantic_ai_washing.analysis.publication_runs.test_03_post_filing_drift import (
    _add_note,
    _add_title,
    _apply_row_rule,
    _set_document_defaults,
    _set_landscape,
    _set_table_no_borders,
    _write_cell,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_TEST_ROOT = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/test_runs/appendix_variable_definitions"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_hybrid_api_a_conf49_main_v1"
TEST_ID = "appendix_variable_definitions"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.appendix_variable_definitions"

VARIABLE_ROWS: list[dict[str, str]] = [
    {
        "Section": "Disclosure counts",
        "Variable": "Total AI sentences per firm-year",
        "Field": "n_total",
        "Definition": "Count of classified AI-related sentences in the firm's annual filing for year t.",
        "Sample": "Annual ever-speaker panel",
    },
    {
        "Section": "Disclosure counts",
        "Variable": "Actionable AI sentences per firm-year",
        "Field": "n_A",
        "Definition": "Count of AI sentences labeled actionable in year t.",
        "Sample": "Annual ever-speaker panel",
    },
    {
        "Section": "Disclosure counts",
        "Variable": "Speculative AI sentences per firm-year",
        "Field": "n_S",
        "Definition": "Count of AI sentences labeled speculative in year t.",
        "Sample": "Annual ever-speaker panel",
    },
    {
        "Section": "Disclosure counts",
        "Variable": "Irrelevant AI sentences per firm-year",
        "Field": "n_I",
        "Definition": "Count of AI sentences labeled irrelevant in year t.",
        "Sample": "Annual ever-speaker panel",
    },
    {
        "Section": "Disclosure composition",
        "Variable": "AI focus",
        "Field": "AI_Focus",
        "Definition": "Broad AI-disclosure intensity measure carried in the canonical panel; operationally aligned with a log(1 + AI sentence count) style intensity proxy.",
        "Sample": "Annual ever-speaker panel",
    },
    {
        "Section": "Disclosure composition",
        "Variable": "Actionable share",
        "Field": "share_A",
        "Definition": "Actionable AI sentences divided by total AI sentences in the firm-year.",
        "Sample": "Annual ever-speaker panel",
    },
    {
        "Section": "Disclosure composition",
        "Variable": "Speculative share",
        "Field": "share_S",
        "Definition": "Speculative AI sentences divided by total AI sentences in the firm-year.",
        "Sample": "Annual ever-speaker panel",
    },
    {
        "Section": "Disclosure composition",
        "Variable": "CredAI",
        "Field": "CredAI",
        "Definition": "Credibility-style disclosure score that increases with actionable content and decreases with speculative content; stored directly in the canonical panel.",
        "Sample": "Annual ever-speaker panel",
    },
    {
        "Section": "Disclosure composition",
        "Variable": "A/S ratio",
        "Field": "A_S",
        "Definition": "log((1 + actionable count) / (1 + speculative count)); higher values indicate more actionable than speculative disclosure.",
        "Sample": "Annual ever-speaker panel",
    },
    {
        "Section": "Credibility construct",
        "Variable": "PatentMismatch",
        "Field": "PatentMismatch",
        "Definition": "Indicator equal to one for AI-talking firm-years that are both low-credibility in disclosure (bottom yearly quartile of A_S or top yearly quartile of speculative share) and weak in contemporaneous AI patenting relative to the industry-year mean.",
        "Sample": "Annual ever-speaker panel",
    },
    {
        "Section": "Patents",
        "Variable": "AI patents",
        "Field": "patents_ai",
        "Definition": "Count of AI-related patents linked to the firm-year.",
        "Sample": "Annual ever-speaker panel",
    },
    {
        "Section": "Patents",
        "Variable": "Total patents",
        "Field": "patents_total",
        "Definition": "Count of all patents linked to the firm-year.",
        "Sample": "Annual ever-speaker panel",
    },
    {
        "Section": "Patents",
        "Variable": "Future AI patents t+1",
        "Field": "log_patents_ai_lead1",
        "Definition": "log(1 + AI patents) measured one year after the disclosure year.",
        "Sample": "Annual ever-speaker panel",
    },
    {
        "Section": "Patents",
        "Variable": "Future AI patents t+2",
        "Field": "log_patents_ai_lead2",
        "Definition": "log(1 + AI patents) measured two years after the disclosure year.",
        "Sample": "Annual ever-speaker panel",
    },
    {
        "Section": "Controls",
        "Variable": "Log assets",
        "Field": "ln_assets",
        "Definition": "Natural log of total assets.",
        "Sample": "Annual ever-speaker panel",
    },
    {
        "Section": "Controls",
        "Variable": "Leverage",
        "Field": "leverage",
        "Definition": "Debt scaled by assets.",
        "Sample": "Annual ever-speaker panel",
    },
    {
        "Section": "Controls",
        "Variable": "Cash/assets",
        "Field": "cash",
        "Definition": "Cash holdings scaled by assets.",
        "Sample": "Annual ever-speaker panel",
    },
    {
        "Section": "Controls",
        "Variable": "R&D/assets",
        "Field": "rd_intensity",
        "Definition": "Research and development expense scaled by assets.",
        "Sample": "Annual ever-speaker panel",
    },
    {
        "Section": "Controls",
        "Variable": "CAPX/assets",
        "Field": "capx_at",
        "Definition": "Capital expenditures scaled by assets.",
        "Sample": "Annual ever-speaker panel",
    },
    {
        "Section": "Controls",
        "Variable": "ROA",
        "Field": "roa",
        "Definition": "Return on assets.",
        "Sample": "Annual ever-speaker panel",
    },
    {
        "Section": "Controls",
        "Variable": "Sales growth",
        "Field": "sales_growth",
        "Definition": "Year-over-year sales growth rate.",
        "Sample": "Annual ever-speaker panel",
    },
    {
        "Section": "Controls",
        "Variable": "Employees",
        "Field": "emp",
        "Definition": "Employee count from Compustat.",
        "Sample": "Annual ever-speaker panel",
    },
    {
        "Section": "Event-study outcomes",
        "Variable": "CAR[-1,+1]",
        "Field": "car_m1_p1",
        "Definition": "Cumulative abnormal return over the one-day-before to one-day-after filing window.",
        "Sample": "Filing-event sample",
    },
    {
        "Section": "Event-study outcomes",
        "Variable": "BHAR[+2,+21]",
        "Field": "bhar_1m",
        "Definition": "Buy-and-hold abnormal return from trading day +2 through +21 after the filing date.",
        "Sample": "Filing-event sample",
    },
    {
        "Section": "Event-study outcomes",
        "Variable": "BHAR[+2,+63]",
        "Field": "bhar_3m",
        "Definition": "Buy-and-hold abnormal return from trading day +2 through +63 after the filing date.",
        "Sample": "Filing-event sample",
    },
    {
        "Section": "Event-study outcomes",
        "Variable": "BHAR[+2,+126]",
        "Field": "bhar_6m",
        "Definition": "Buy-and-hold abnormal return from trading day +2 through +126 after the filing date.",
        "Sample": "Filing-event sample",
    },
    {
        "Section": "Event-study outcomes",
        "Variable": "BHAR[+2,+252]",
        "Field": "bhar_12m",
        "Definition": "Buy-and-hold abnormal return from trading day +2 through +252 after the filing date.",
        "Sample": "Filing-event sample",
    },
    {
        "Section": "Valuation and financing",
        "Variable": "Log MktCap/assets",
        "Field": "log_mktcap_assets",
        "Definition": "log(1 + market capitalization / assets), using merged CRSP year-end market cap and Compustat assets.",
        "Sample": "Annual panel with market merge",
    },
    {
        "Section": "Valuation and financing",
        "Variable": "Log Q proxy",
        "Field": "log_q_proxy",
        "Definition": "log(1 + market cap/assets + leverage), used when local pulls do not include full book-equity fields.",
        "Sample": "Annual panel with market merge",
    },
    {
        "Section": "Valuation and financing",
        "Variable": "Delta log Q t+1",
        "Field": "delta_log_q_proxy_lead1",
        "Definition": "One-year-ahead change in the log Q proxy.",
        "Sample": "Annual panel with market merge",
    },
    {
        "Section": "Valuation and financing",
        "Variable": "Delta shares t+1",
        "Field": "share_growth_lead1",
        "Definition": "Next-year growth in CRSP shares outstanding.",
        "Sample": "Annual panel with market merge",
    },
    {
        "Section": "Valuation and financing",
        "Variable": "Issue >5% t+1",
        "Field": "equity_issue_lead1",
        "Definition": "Indicator equal to one when next-year shares outstanding grow by more than 5%.",
        "Sample": "Annual panel with market merge",
    },
    {
        "Section": "Treatment and screens",
        "Variable": "PostChatGPT",
        "Field": "post_chatgpt / PostChatGPT",
        "Definition": "Indicator for fiscal years 2023 onward in the ChatGPT-shock designs.",
        "Sample": "Annual and event-study panels",
    },
    {
        "Section": "Treatment and screens",
        "Variable": "Non-big screen",
        "Field": "nonbig_marketcap",
        "Definition": "Indicator equal to one when a firm's market capitalization is at or below the matched-sample yearly median.",
        "Sample": "Annual panel with market merge",
    },
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-root", type=Path, default=DEFAULT_TEST_ROOT)
    parser.add_argument("--paper-root", type=Path, default=DEFAULT_PAPER_ROOT)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    return parser.parse_args()


def _escape_tex(text: str) -> str:
    return (
        text.replace("\\", "\\textbackslash{}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("_", "\\_")
        .replace("#", "\\#")
    )


def _markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def _render_outputs(table_df):
    headers = ["Section", "Variable", "Field", "Definition", "Sample"]
    rows = table_df[headers].astype(str).values.tolist()
    md = "\n".join(["# Table Main", "", _markdown_table(headers, rows), ""])
    tex_lines = [
        "% Requires \\usepackage{longtable,array}",
        "\\begin{longtable}{p{0.15\\textwidth}p{0.20\\textwidth}p{0.14\\textwidth}p{0.34\\textwidth}p{0.13\\textwidth}}",
        "\\caption{Variable definitions for the updated AI-washing analysis}\\\\",
        "\\hline",
        "Section & Variable & Field & Definition & Sample \\\\",
        "\\hline",
        "\\endfirsthead",
        "\\hline",
        "Section & Variable & Field & Definition & Sample \\\\",
        "\\hline",
        "\\endhead",
    ]
    for row in rows:
        tex_lines.append(" & ".join(_escape_tex(value) for value in row) + " \\\\")
    tex_lines.extend(["\\hline", "\\end{longtable}"])
    return md, "\n".join(tex_lines) + "\n"


def _build_docx(table_df, output_path: Path) -> None:
    document = Document()
    _set_document_defaults(document)
    _set_landscape(document)
    _add_title(document, "Appendix Table. Variable Definitions")
    _add_note(
        document,
        "This appendix table defines the main disclosure, patent, event-study, valuation, financing, and control variables used in the updated AI-washing paper. "
        "Canonical field names are listed so the appendix can be traced directly back to the generated data and analysis scripts.",
    )

    headers = ["Section", "Variable", "Field", "Definition", "Sample"]
    widths = [1.5, 2.2, 1.3, 4.5, 1.6]
    table = document.add_table(rows=len(table_df) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    _set_table_no_borders(table)

    header_row = table.rows[0]
    for idx, header in enumerate(headers):
        header_row.cells[idx].width = Inches(widths[idx])
        _write_cell(
            header_row.cells[idx],
            header,
            align=WD_ALIGN_PARAGRAPH.LEFT if idx == 0 else WD_ALIGN_PARAGRAPH.CENTER,
            size=10.0,
            bold=True,
        )
    _apply_row_rule(header_row, top=True, bottom=True)

    previous_section = None
    for row_idx, record in enumerate(table_df.to_dict("records"), start=1):
        row = table.rows[row_idx]
        section_text = record["Section"]
        if section_text == previous_section:
            section_text = ""
        previous_section = record["Section"]
        values = [
            (section_text, True),
            (record["Variable"], True),
            (record["Field"], False),
            (record["Definition"], False),
            (record["Sample"], False),
        ]
        for col_idx, (text, bold) in enumerate(values):
            row.cells[col_idx].width = Inches(widths[col_idx])
            _write_cell(
                row.cells[col_idx],
                text,
                align=WD_ALIGN_PARAGRAPH.LEFT,
                size=9.6,
                bold=bold,
            )
    _apply_row_rule(table.rows[-1], bottom=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.save(str(output_path))


def _writer_packet(args: argparse.Namespace, table_df) -> str:
    return "\n".join(
        [
            "# Writer Packet",
            "",
            "## Metadata",
            f"- Test id: `{TEST_ID}`",
            f"- Run id: `{args.run_id}`",
            f"- Date run: `{date.today().isoformat()}`",
            f"- Script/module path: `{MODULE_PATH}`",
            "",
            "## Coverage",
            f"- Variables documented: `{len(table_df):,}`",
            f"- Sections covered: `{table_df['Section'].nunique()}`",
            "",
            "## Caption Draft",
            "This appendix table defines the main disclosure, patent, event-study, valuation, financing, and control variables used in the updated AI-washing analysis. Canonical field names are included so the definitions map directly to the generated panel files and publication-run scripts.",
            "",
        ]
    )


def _result_notes(table_df) -> str:
    sections = ", ".join(table_df["Section"].drop_duplicates().tolist())
    return "\n".join(
        [
            "# Result Notes",
            "",
            f"- Variable definitions table covers `{len(table_df):,}` variables across `{table_df['Section'].nunique()}` sections.",
            f"- Sections included: {sections}.",
            "- The table is designed as a paper appendix artifact, not just an internal data dictionary, so the labels follow paper wording while retaining canonical field names.",
            "",
        ]
    )


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

    table_df = __import__("pandas").DataFrame(VARIABLE_ROWS)
    table_df.to_csv(run_dir / "table_main.csv", index=False)
    table_md, table_tex = _render_outputs(table_df)
    (run_dir / "table_main.md").write_text(table_md, encoding="utf-8")
    (run_dir / "table_main.tex").write_text(table_tex, encoding="utf-8")
    _build_docx(table_df, run_dir / "table_main.docx")
    (run_dir / "writer_packet.md").write_text(_writer_packet(args, table_df), encoding="utf-8")
    (run_dir / "result_notes.md").write_text(_result_notes(table_df), encoding="utf-8")
    dataset_summary = {
        "test_id": TEST_ID,
        "run_id": args.run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "variable_count": int(len(table_df)),
        "sections": sorted(table_df["Section"].drop_duplicates().tolist()),
    }
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
