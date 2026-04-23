"""Publication run driver for Test 23: analyst-coverage split specifications."""

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
from semantic_ai_washing.analysis.publication_runs.test_22_analyst_monitoring_interaction import (
    _base_style,
    _cell,
    _load_current_coverage,
    _load_panel,
    _stars,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_ANNUAL_PANEL = (
    REPO_ROOT
    / "data/processed/panel/canonical/ever_speaker_panel_2016_2025_hybrid_api_a_conf49_v1.parquet"
)
DEFAULT_ANALYST_SUMMARY = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_2/test_runs/"
    "test_21_analyst_discernment/20260423_aiw_v3_2_test_21_analyst_discernment_main_v1/"
    "ibes_annual_summary.parquet"
)
DEFAULT_TEST_ROOT = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_2/test_runs/test_23_analyst_coverage_splits"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated/v3_2"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_aiw_v3_2_test_23_analyst_coverage_splits_main_v1"
TEST_ID = "test_23_analyst_coverage_splits"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.test_23_analyst_coverage_splits"
CONTROL_SPECS = ["AI_Focus", "ln_assets", "leverage", "cash", "roa"]
OUTCOME_SPECS: list[tuple[str, str]] = [
    ("PatentMismatch_lead1", "PatentMismatch t+1"),
    ("log_patents_ai_lead1", "Log(1 + AI grants) t+1"),
    ("roa_lead2", "ROA t+2"),
]
BUCKET_SPECS: list[tuple[str, str]] = [
    ("BottomQuartile", "Bottom quartile"),
    ("LowerHalf", "Lower half"),
    ("UpperHalf", "Upper half"),
    ("TopQuartile", "Top quartile"),
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annual-panel", type=Path, default=DEFAULT_ANNUAL_PANEL)
    parser.add_argument("--analyst-summary", type=Path, default=DEFAULT_ANALYST_SUMMARY)
    parser.add_argument("--test-root", type=Path, default=DEFAULT_TEST_ROOT)
    parser.add_argument("--paper-root", type=Path, default=DEFAULT_PAPER_ROOT)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    return parser.parse_args()


def _prepare_sample(panel: pd.DataFrame, coverage: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    use = panel.merge(coverage, on=["ticker", "year"], how="left", validate="many_to_one")
    use = use.loc[use["any_ai_talk"].fillna(0).astype(int).eq(1)].copy()
    use["log_analyst_coverage_t"] = pd.to_numeric(use["log_analyst_coverage_t"], errors="coerce")
    use = use.loc[use["log_analyst_coverage_t"].notna()].copy()
    q25 = use.groupby("year")["log_analyst_coverage_t"].transform(lambda s: s.quantile(0.25))
    q50 = use.groupby("year")["log_analyst_coverage_t"].transform("median")
    q75 = use.groupby("year")["log_analyst_coverage_t"].transform(lambda s: s.quantile(0.75))
    use["BottomQuartile"] = (use["log_analyst_coverage_t"] <= q25).astype(int)
    use["LowerHalf"] = (use["log_analyst_coverage_t"] <= q50).astype(int)
    use["UpperHalf"] = (use["log_analyst_coverage_t"] >= q50).astype(int)
    use["TopQuartile"] = (use["log_analyst_coverage_t"] >= q75).astype(int)
    summary = {
        "ai_talking_rows": int(len(use)),
        "unique_firms": int(use["cik"].nunique()),
        "coverage_nonmissing": int(use["log_analyst_coverage_t"].notna().sum()),
        "years": [int(use["year"].min()), int(use["year"].max())],
        "bucket_sizes": {bucket: int(use[bucket].sum()) for bucket, _label in BUCKET_SPECS},
    }
    return use, summary


def _fit_models(sample: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for bucket, bucket_label in BUCKET_SPECS:
        subset = sample.loc[sample[bucket].eq(1)].copy()
        for outcome, outcome_label in OUTCOME_SPECS:
            needed = [outcome, "PatentMismatch", "sic2", "year", *CONTROL_SPECS]
            use = subset.dropna(subset=needed).copy()
            if use.empty:
                rows.append(
                    {
                        "bucket": bucket,
                        "bucket_label": bucket_label,
                        "outcome": outcome,
                        "outcome_label": outcome_label,
                        "coef": math.nan,
                        "se": math.nan,
                        "pvalue": math.nan,
                        "nobs": 0,
                        "outcome_mean": math.nan,
                    }
                )
                continue
            result, est_sample, _adj_r2 = _fit_absorbed_ols(
                use,
                dependent=outcome,
                rhs_terms=["PatentMismatch"],
                absorb_col="cik",
                include_year=True,
                controls=CONTROL_SPECS,
            )
            rows.append(
                {
                    "bucket": bucket,
                    "bucket_label": bucket_label,
                    "outcome": outcome,
                    "outcome_label": outcome_label,
                    "coef": float(result.params.get("PatentMismatch", math.nan)),
                    "se": float(result.bse.get("PatentMismatch", math.nan)),
                    "pvalue": float(result.pvalues.get("PatentMismatch", math.nan)),
                    "nobs": int(result.nobs),
                    "outcome_mean": float(est_sample[outcome].mean()),
                }
            )
    return rows


def _build_table(results: list[dict[str, object]]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for bucket, bucket_label in BUCKET_SPECS:
        for outcome, outcome_label in OUTCOME_SPECS:
            result = next(row for row in results if row["bucket"] == bucket and row["outcome"] == outcome)
            rows.append(
                {
                    "Coverage slice": bucket_label,
                    "Outcome": outcome_label,
                    "PatentMismatch": _cell(result["coef"], result["se"], result["pvalue"]),
                    "Outcome mean": (
                        f"{result['outcome_mean']:.4f}" if math.isfinite(result["outcome_mean"]) else ""
                    ),
                    "Observations": result["nobs"],
                }
            )
    return pd.DataFrame(rows)


def _build_markdown(table_df: pd.DataFrame) -> str:
    headers = table_df.columns.tolist()
    rows = [[str(value) for value in row] for row in table_df.values.tolist()]
    return to_markdown_table(headers, rows)


def _render_latex(table_df: pd.DataFrame) -> str:
    lines = [
        "\\begin{table}[!htbp]",
        "\\centering",
        "\\caption{Analyst-coverage split tests for later mismatch consequences}",
        "\\small",
        "\\begin{tabular}{llcrr}",
        "\\hline",
        "Coverage slice & Outcome & PatentMismatch & Outcome mean & Observations " + "\\\\",
        "\\hline",
    ]
    for _, row in table_df.iterrows():
        lines.append(
            " & ".join(
                [
                    str(row["Coverage slice"]).replace("_", "\\_"),
                    str(row["Outcome"]).replace("_", "\\_"),
                    str(row["PatentMismatch"]),
                    str(row["Outcome mean"]),
                    str(row["Observations"]),
                ]
            )
            + " "
            + "\\\\"
        )
    lines.extend(
        [
            "\\hline",
            "\\end{tabular}",
            "\\begin{flushleft}",
            "\\footnotesize Notes: Each row re-estimates the canonical annual consequence regression within a same-year analyst-coverage slice built from IBES annual EPS coverage. Lower/upper half are within-year median splits; bottom/top quartile are within-year 25th/75th percentile slices. All specifications use the AI-talking annual sample, firm fixed effects, year fixed effects, current controls, and firm-clustered standard errors.",
            "\\end{flushleft}",
            "\\end{table}",
        ]
    )
    return "\n".join(lines)


def _write_docx(table_df: pd.DataFrame, path: Path, summary: dict[str, object]) -> None:
    document = Document()
    _set_document_defaults(document)
    _set_landscape(document)
    _add_title(document, "Test 23. Analyst-coverage split specifications")
    _add_note(
        document,
        (
            "This table re-estimates the later-consequence regressions within same-year analyst-coverage slices. "
            "The question is whether the effects linked to low-credibility AI disclosure are concentrated in "
            "low-attention environments or remain visible in the more closely followed part of the sample."
        ),
    )
    _add_note(
        document,
        (
            f"Coverage-eligible AI-talking rows = {summary['coverage_nonmissing']:,}; "
            f"unique firms = {summary['unique_firms']:,}."
        ),
    )
    headers = table_df.columns.tolist()
    rows = [[(str(value), False) for value in row] for row in table_df.values.tolist()]
    _build_panel_table(document, headers, rows)
    document.save(path)


def _write_figure(results: list[dict[str, object]], *, png_path: Path, pdf_path: Path) -> None:
    _base_style()
    fig, axes = plt.subplots(1, len(OUTCOME_SPECS), figsize=(11.2, 3.8), sharey=False)
    if len(OUTCOME_SPECS) == 1:
        axes = [axes]
    order = [label for _bucket, label in BUCKET_SPECS]
    for ax, (outcome, outcome_label) in zip(axes, OUTCOME_SPECS, strict=True):
        subset = [row for row in results if row["outcome"] == outcome]
        subset = sorted(subset, key=lambda row: order.index(row["bucket_label"]))
        x = list(range(len(subset)))
        coef = [row["coef"] for row in subset]
        err = [1.96 * row["se"] if math.isfinite(row["se"]) else math.nan for row in subset]
        ax.errorbar(x, coef, yerr=err, fmt="o", capsize=3, color="#1f4e79")
        ax.axhline(0, color="black", linewidth=0.9, linestyle="--")
        ax.set_xticks(x, [row["bucket_label"] for row in subset], rotation=20, ha="right")
        ax.set_title(outcome_label)
        ax.set_ylabel("PatentMismatch coefficient")
    fig.tight_layout()
    fig.savefig(png_path, dpi=220)
    fig.savefig(pdf_path)
    plt.close(fig)


def _write_writer_packet(output_path: Path, summary: dict[str, object], results: list[dict[str, object]]) -> None:
    patent_rows = [row for row in results if row["outcome"] == "log_patents_ai_lead1"]
    roa_rows = [row for row in results if row["outcome"] == "roa_lead2"]
    lines = [
        "# Writer Packet: Test 23 analyst-coverage split specifications",
        "",
        "## Setup",
        "",
        "- Sample: AI-talking annual panel with non-missing same-year IBES analyst coverage.",
        "- Coverage slices: bottom quartile, lower half, upper half, top quartile within calendar year.",
        "- Outcome regressions: future mismatch persistence, future AI grants, and later ROA.",
        "- Specification: firm fixed effects, year fixed effects, current controls, firm-clustered standard errors.",
        "",
        "## Read",
        "",
        f"- Coverage-eligible rows = {summary['coverage_nonmissing']:,}; firms = {summary['unique_firms']:,}.",
        f"- Bottom quartile rows = {summary['bucket_sizes']['BottomQuartile']:,}; top quartile rows = {summary['bucket_sizes']['TopQuartile']:,}.",
    ]
    if patent_rows:
        best_patent = min(patent_rows, key=lambda row: row["pvalue"] if math.isfinite(row["pvalue"]) else 9)
        lines.append(
            f"- Strongest future-grant split: {best_patent['bucket_label']} coefficient = "
            f"{best_patent['coef']:.4f}{_stars(best_patent['pvalue'])} (p={best_patent['pvalue']:.3f})."
        )
    if roa_rows:
        best_roa = min(roa_rows, key=lambda row: row["pvalue"] if math.isfinite(row["pvalue"]) else 9)
        lines.append(
            f"- Strongest ROA split: {best_roa['bucket_label']} coefficient = "
            f"{best_roa['coef']:.4f}{_stars(best_roa['pvalue'])} (p={best_roa['pvalue']:.3f})."
        )
    lines.extend(
        [
            "",
            "## Placement",
            "",
            "- Best use: appendix or targeted intermediary-attention subsection.",
            "- Main-text worthy only if one split produces a materially cleaner monitoring story than the interaction table.",
        ]
    )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_result_notes(output_path: Path, results: list[dict[str, object]]) -> None:
    lines = [
        "# Result Notes: Test 23 analyst-coverage split specifications",
        "",
        "The split design checks whether later mismatch consequences concentrate in low-coverage environments or survive among more closely followed firms.",
        "",
    ]
    for bucket, bucket_label in BUCKET_SPECS:
        lines.append(f"## {bucket_label}")
        for outcome, outcome_label in OUTCOME_SPECS:
            row = next(item for item in results if item["bucket"] == bucket and item["outcome"] == outcome)
            if math.isfinite(row["coef"]):
                lines.append(
                    f"- {outcome_label}: {row['coef']:.4f}{_stars(row['pvalue'])} "
                    f"(SE {row['se']:.4f}, p={row['pvalue']:.3f}, n={row['nobs']:,})."
                )
            else:
                lines.append(f"- {outcome_label}: insufficient sample.")
        lines.append("")
    output_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


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
    coverage = _load_current_coverage(args.analyst_summary)
    sample, sample_summary = _prepare_sample(panel, coverage)
    results = _fit_models(sample)
    table_df = _build_table(results)
    markdown = _build_markdown(table_df)
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
    sample_path = run_root / "coverage_split_sample.parquet"

    _write_docx(table_df, docx_path, sample_summary)
    tex_path.write_text(latex, encoding="utf-8")
    csv_path.write_text(table_df.to_csv(index=False), encoding="utf-8")
    md_path.write_text(markdown, encoding="utf-8")
    _write_figure(results, png_path=png_path, pdf_path=pdf_path)
    _write_writer_packet(writer_path, sample_summary, results)
    _write_result_notes(notes_path, results)
    sample.to_parquet(sample_path, index=False)

    for subdir, path in {
        "docx": docx_path,
        "latex": tex_path,
        "tables": csv_path,
        "figures": png_path,
        "writer_packets": writer_path,
        "snippets": notes_path,
    }.items():
        shutil.copy2(path, args.paper_root / subdir / path.name)

    manifest = {
        "test_id": TEST_ID,
        "module_path": MODULE_PATH,
        "run_id": args.run_id,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "sample_summary": sample_summary,
        "outputs": {
            "docx": str(docx_path),
            "tex": str(tex_path),
            "csv": str(csv_path),
            "png": str(png_path),
            "pdf": str(pdf_path),
            "markdown": str(md_path),
            "writer_packet": str(writer_path),
            "result_notes": str(notes_path),
            "sample": str(sample_path),
        },
    }
    (run_root / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
