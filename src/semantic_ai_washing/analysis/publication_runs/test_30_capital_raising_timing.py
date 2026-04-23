"""Publication run driver for Test 30: capital-raising timing and disclosure opportunism."""

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
DEFAULT_TEST_ROOT = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_2/test_runs/test_30_capital_raising_timing"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated/v3_2"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_aiw_v3_2_test_30_capital_raising_timing_main_v1"
TEST_ID = "test_30_capital_raising_timing"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.test_30_capital_raising_timing"

PANEL_SPECS: list[tuple[str, str]] = [
    ("all", "Panel A. First large equity issue among active AI issuers"),
    ("nonbig", "Panel B. Non-big first-issue AI issuers"),
]
OUTCOME_SPECS: list[tuple[str, str]] = [
    ("LowCredibility", "LowCredibility"),
    ("ApplicationMismatch", "ApplicationMismatch"),
    ("PatentMismatch", "PatentMismatch"),
    ("SpecShare", "Speculative share"),
    ("AI_Focus", "AI Focus"),
]
FIGURE_OUTCOMES: list[tuple[str, str]] = [
    ("LowCredibility", "LowCredibility"),
    ("PatentMismatch", "PatentMismatch"),
    ("SpecShare", "Speculative share"),
    ("AI_Focus", "AI Focus"),
]
EVENT_WINDOWS = [-2, -1, 0, 1, 2]


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


def _cell(coef: float, se: float, p_value: float) -> str:
    if not (math.isfinite(coef) and math.isfinite(se)):
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
        "SpecShare",
        "LowCredibility",
        "PatentMismatch",
        "ApplicationMismatch",
        "market_cap_year_end",
        "shrout",
    ]:
        if column in panel.columns:
            panel[column] = pd.to_numeric(panel[column], errors="coerce")
    yearly_median_market_cap = panel.groupby("year")["market_cap_year_end"].transform("median")
    panel["nonbig_year"] = np.where(
        panel["market_cap_year_end"].notna() & yearly_median_market_cap.notna(),
        panel["market_cap_year_end"].le(yearly_median_market_cap),
        pd.NA,
    )
    panel = panel.sort_values(["permno", "year", "cik"]).reset_index(drop=True)
    shrout_lead1 = panel.groupby("permno", sort=False)["shrout"].shift(-1)
    panel["share_growth_lead1"] = shrout_lead1 / panel["shrout"] - 1.0
    panel["equity_issue_lead1"] = np.where(
        panel["share_growth_lead1"].notna(),
        (panel["share_growth_lead1"] > 0.05).astype(int),
        np.nan,
    )
    return panel


def _prepare_event_sample(panel: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    first_issue = (
        panel.loc[panel["equity_issue_lead1"].eq(1), ["cik", "year"]]
        .dropna()
        .sort_values(["cik", "year"])
        .drop_duplicates(subset=["cik"])
        .rename(columns={"year": "first_issue_year"})
    )
    merged = panel.merge(first_issue, on="cik", how="inner", validate="many_to_one")
    merged["first_issue_year"] = pd.to_numeric(merged["first_issue_year"], errors="coerce").astype(int)
    merged["event_time"] = pd.to_numeric(merged["year"], errors="coerce").astype(int) - merged["first_issue_year"]
    merged = merged.loc[merged["event_time"].isin(EVENT_WINDOWS)].copy()

    active_window = (
        merged.loc[merged["event_time"].isin([0, 1]), ["cik", "event_time", "any_ai_talk"]]
        .pivot(index="cik", columns="event_time", values="any_ai_talk")
        .fillna(0)
    )
    active_firms = active_window.index[
        active_window.get(0, pd.Series(0, index=active_window.index)).eq(1)
        & active_window.get(1, pd.Series(0, index=active_window.index)).eq(1)
    ]
    sample = merged.loc[merged["cik"].isin(active_firms)].copy()

    event_nonbig = (
        sample.loc[sample["event_time"].eq(0), ["cik", "nonbig_year"]]
        .drop_duplicates(subset=["cik"])
        .rename(columns={"nonbig_year": "event_nonbig"})
    )
    sample = sample.merge(event_nonbig, on="cik", how="left", validate="many_to_one")
    sample = sample.sort_values(["cik", "year"]).reset_index(drop=True)
    event_nonbig_mask = sample["event_nonbig"].eq(True)

    summary = {
        "issue_rule": "Issue>5% uses next-year CRSP shrout growth above 5%.",
        "issue_event_firms": int(first_issue["cik"].nunique()),
        "issue_event_rows": int(len(merged)),
        "active_ai_issue_firms": int(sample["cik"].nunique()),
        "active_ai_issue_rows": int(len(sample)),
        "nonbig_active_issue_firms": int(sample.loc[event_nonbig_mask, "cik"].nunique()),
        "nonbig_active_issue_rows": int(len(sample.loc[event_nonbig_mask])),
    }
    return sample, summary


def _subset_sample(sample: pd.DataFrame, subset_key: str) -> pd.DataFrame:
    if subset_key == "all":
        return sample.copy()
    if subset_key == "nonbig":
        return sample.loc[sample["event_nonbig"].eq(True)].copy()
    raise ValueError(f"Unknown subset: {subset_key}")


def _paired_diffs(sample: pd.DataFrame, panel_label: str) -> tuple[list[dict[str, object]], list[dict[str, object]], pd.DataFrame]:
    rows: list[dict[str, object]] = []
    means_rows: list[dict[str, object]] = []
    table_rows: list[dict[str, object]] = []
    for outcome, outcome_label in OUTCOME_SPECS:
        wide = (
            sample.loc[:, ["cik", "event_time", outcome]]
            .pivot_table(index="cik", columns="event_time", values=outcome, aggfunc="mean")
            .sort_index(axis=1)
        )
        event_mean = float(wide.get(0).dropna().mean()) if wide.get(0) is not None else math.nan
        n_firms = int(wide.index.nunique())
        row_payload = {
            "Panel": panel_label,
            "Outcome": outcome_label,
            "Event year vs. t-1": "",
            "t+1 vs. event year": "",
            "t+2 vs. event year": "",
            "Event-year mean": f"{event_mean:.4f}" if math.isfinite(event_mean) else "",
            "N firms": str(n_firms),
        }
        compare_specs = [
            ((0, -1), "Event year vs. t-1"),
            ((1, 0), "t+1 vs. event year"),
            ((2, 0), "t+2 vs. event year"),
        ]
        for (left, right), label in compare_specs:
            left_series = wide.get(left)
            right_series = wide.get(right)
            if left_series is None or right_series is None:
                coef = se = p_value = math.nan
                n_pairs = 0
            else:
                diffs = (left_series - right_series).dropna()
                n_pairs = int(len(diffs))
                coef = float(diffs.mean()) if n_pairs else math.nan
                se = float(diffs.std(ddof=1) / math.sqrt(n_pairs)) if n_pairs > 1 else math.nan
                p_value = (
                    float(stats.ttest_1samp(diffs, 0.0, nan_policy="omit").pvalue)
                    if n_pairs > 1
                    else math.nan
                )
            row_payload[label] = _cell(coef, se, p_value)
            rows.append(
                {
                    "panel": panel_label,
                    "outcome": outcome,
                    "outcome_label": outcome_label,
                    "comparison": label,
                    "coef": coef,
                    "se": se,
                    "p_value": p_value,
                    "n_pairs": n_pairs,
                }
            )
        table_rows.append(row_payload)

        means = (
            sample.groupby("event_time", as_index=False)[outcome]
            .mean()
            .rename(columns={outcome: "mean_value"})
        )
        means["panel"] = panel_label
        means["outcome"] = outcome
        means["outcome_label"] = outcome_label
        means_rows.extend(means.to_dict(orient="records"))
    return rows, means_rows, pd.DataFrame(table_rows)


def _build_table(table_frames: list[pd.DataFrame]) -> pd.DataFrame:
    combined_rows: list[dict[str, object]] = []
    for frame in table_frames:
        panel_label = frame.iloc[0]["Panel"]
        combined_rows.append(
            {
                "Panel": panel_label,
                "Outcome": "",
                "Event year vs. t-1": "",
                "t+1 vs. event year": "",
                "t+2 vs. event year": "",
                "Event-year mean": "",
                "N firms": "",
            }
        )
        for _, row in frame.iterrows():
            payload = row.to_dict()
            payload["Panel"] = ""
            combined_rows.append(payload)
    return pd.DataFrame(combined_rows)


def _render_markdown(table_df: pd.DataFrame) -> str:
    headers = table_df.columns.tolist()
    rows = [[str(value) for value in row] for row in table_df.values.tolist()]
    return to_markdown_table(headers, rows)


def _render_latex(table_df: pd.DataFrame) -> str:
    lines = [
        "\\begin{table}[!htbp]",
        "\\centering",
        "\\caption{Capital-raising timing and low-credibility AI disclosure}",
        "\\small",
        "\\begin{tabular}{llcccrr}",
        "\\hline",
        "Panel & Outcome & Event year vs. t-1 & t+1 vs. event year & t+2 vs. event year & Event-year mean & Obs. \\\\",
        "\\hline",
    ]
    for _, row in table_df.iterrows():
        if row["Panel"]:
            lines.append("\\multicolumn{7}{l}{\\textit{" + str(row["Panel"]).replace("&", "\\&") + "}} \\\\")
            continue
        lines.append(
            " & ".join(
                [
                    "",
                    str(row["Outcome"]).replace("_", "\\_"),
                    str(row["Event year vs. t-1"]),
                    str(row["t+1 vs. event year"]),
                    str(row["t+2 vs. event year"]),
                    str(row["Event-year mean"]),
                    str(row["N firms"]),
                ]
            )
            + " \\\\",
        )
    lines.extend(
        [
            "\\hline",
            "\\end{tabular}",
            "\\begin{flushleft}",
            "\\footnotesize Notes: Event year 0 is the disclosure year preceding a large equity-issuance window, where Issue>5\\% is defined as next-year CRSP shares-outstanding growth above 5\\%. The event sample keeps each firm's first such issue year and focuses on active AI issuers that continue talking about AI in the event year and the following year. Positive values in the first comparison indicate deterioration or intensification into the issuance window; negative values in the second and third comparisons indicate partial unwind after the issue year.",
            "\\end{flushleft}",
            "\\end{table}",
        ]
    )
    return "\n".join(lines) + "\n"


def _write_docx(path: Path, table_df: pd.DataFrame, summary: dict[str, object]) -> None:
    document = Document()
    _set_document_defaults(document)
    _set_landscape(document)
    _add_title(document, "Test 30. Capital-raising timing and disclosure opportunism")
    _add_note(
        document,
        (
            "This table studies whether low-credibility AI disclosure intensifies around first large equity-issuance windows. "
            "Event year 0 is the disclosure year before an issuance episode, defined using next-year shares-outstanding growth."
        ),
    )
    _add_note(
        document,
        (
            f"First issue-event firms = {summary['issue_event_firms']:,}; active AI issue-event firms = {summary['active_ai_issue_firms']:,}; "
            f"non-big active issue-event firms = {summary['nonbig_active_issue_firms']:,}."
        ),
    )
    _add_note(document, summary["issue_rule"])
    headers = table_df.columns.tolist()
    rows = [[(str(value), False) for value in row] for row in table_df.values.tolist()]
    _build_panel_table(document, headers, rows)
    document.save(path)


def _write_figure(means_rows: pd.DataFrame, *, png_path: Path, pdf_path: Path) -> None:
    _base_style()
    fig, axes = plt.subplots(2, 2, figsize=(11.2, 7.0), sharex=True)
    axes = axes.flatten()
    colors = {
        PANEL_SPECS[0][1]: "#1f4e79",
        PANEL_SPECS[1][1]: "#8b0000",
    }
    for ax, (outcome, outcome_label) in zip(axes, FIGURE_OUTCOMES, strict=True):
        subset = means_rows.loc[means_rows["outcome"].eq(outcome)].copy()
        for _subset_key, panel_label in PANEL_SPECS:
            panel_frame = subset.loc[subset["panel"].eq(panel_label)].sort_values("event_time")
            if panel_frame.empty:
                continue
            ax.plot(
                panel_frame["event_time"],
                panel_frame["mean_value"],
                marker="o",
                linewidth=2,
                label=panel_label.replace("Panel ", ""),
                color=colors[panel_label],
            )
        ax.axvline(0, color="black", linewidth=0.9, linestyle=":")
        ax.set_title(outcome_label)
        ax.set_xlabel("Event time")
        ax.set_ylabel("Mean outcome")
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(png_path, dpi=220, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)


def _write_writer_packet(path: Path, summary: dict[str, object], rows: list[dict[str, object]]) -> None:
    keyed = {(row["panel"], row["outcome"], row["comparison"]): row for row in rows}
    panel = PANEL_SPECS[0][1]
    nonbig_panel = PANEL_SPECS[1][1]
    lines = [
        "# Writer Packet: Test 30 capital-raising timing and disclosure opportunism",
        "",
        "## Setup",
        "",
        "- Event year 0 is the disclosure year before a large equity-issuance window.",
        f"- Issuance rule: {summary['issue_rule']}",
        "- Sample keeps each firm's first such issue year and focuses on active AI issuers that continue discussing AI in year 0 and year +1.",
        "",
        "## Density",
        "",
        f"- First issue-event firms: `{summary['issue_event_firms']:,}`.",
        f"- Active AI issue-event firms: `{summary['active_ai_issue_firms']:,}` across `{summary['active_ai_issue_rows']:,}` event-window rows.",
        f"- Non-big active issue-event firms: `{summary['nonbig_active_issue_firms']:,}` across `{summary['nonbig_active_issue_rows']:,}` rows.",
        "",
        "## Main read",
        "",
        f"- All active AI issuers: `PatentMismatch` rises into the issuance window by `{keyed[(panel, 'PatentMismatch', 'Event year vs. t-1')]['coef']:.4f}` (p=`{keyed[(panel, 'PatentMismatch', 'Event year vs. t-1')]['p_value']:.3f}`) and then falls by `{keyed[(panel, 'PatentMismatch', 't+1 vs. event year')]['coef']:.4f}` (p=`{keyed[(panel, 'PatentMismatch', 't+1 vs. event year')]['p_value']:.3f}`) in the following year.",
        f"- `LowCredibility` shows the same rise-then-partial-unwind pattern: `{keyed[(panel, 'LowCredibility', 'Event year vs. t-1')]['coef']:.4f}` into the event year and `{keyed[(panel, 'LowCredibility', 't+1 vs. event year')]['coef']:.4f}` afterward.",
        f"- `AI_Focus` keeps rising through and after issuance: `{keyed[(panel, 'AI_Focus', 'Event year vs. t-1')]['coef']:.4f}` into year 0 and `{keyed[(panel, 'AI_Focus', 't+1 vs. event year')]['coef']:.4f}` afterward.",
        f"- Non-big issuers retain the credibility-timing pattern: `PatentMismatch` `{keyed[(nonbig_panel, 'PatentMismatch', 'Event year vs. t-1')]['coef']:.4f}` into year 0 and `{keyed[(nonbig_panel, 'PatentMismatch', 't+1 vs. event year')]['coef']:.4f}` after issuance.",
        "",
        "## Interpretation",
        "",
        "- Best reading: capital-raising windows line up with a temporary deterioration in disclosure credibility rather than a simple disappearance of AI talk.",
        "- The rise in `AI_Focus` means the pattern is more consistent with amplified AI promotion around financing than with post-issue silence.",
        "- Because the credibility measures partly unwind after the issue year, the financing-opportunism interpretation is stronger than the earlier broad financing-outcome regressions.",
        "",
        "## Placement",
        "",
        "- Best use: high appendix or supporting main-text incentive/financing extension if we want one explicit opportunism result tied to capital markets.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_result_notes(path: Path, rows: list[dict[str, object]]) -> None:
    lines = [
        "# Result Notes: Test 30 capital-raising timing and disclosure opportunism",
        "",
        "This packet studies event-time disclosure behavior around first large equity-issuance windows among active AI issuers.",
        "",
    ]
    for _subset_key, panel_label in PANEL_SPECS:
        panel_rows = [row for row in rows if row["panel"] == panel_label]
        lines.append(f"## {panel_label}")
        for outcome, outcome_label in OUTCOME_SPECS:
            outcome_rows = [row for row in panel_rows if row["outcome"] == outcome]
            lines.append(f"### {outcome_label}")
            for comparison in ["Event year vs. t-1", "t+1 vs. event year", "t+2 vs. event year"]:
                row = next(item for item in outcome_rows if item["comparison"] == comparison)
                lines.append(
                    f"- {comparison}: `{row['coef']:.4f}` (SE `{row['se']:.4f}`, p=`{row['p_value']:.3f}`, n=`{row['n_pairs']}`)."
                )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = _parse_args()
    run_root = args.test_root / args.run_id
    run_root.mkdir(parents=True, exist_ok=True)
    for subdir in ["docx", "latex", "tables", "figures", "writer_packets", "snippets"]:
        (args.paper_root / subdir).mkdir(parents=True, exist_ok=True)

    panel = _load_panel(args.annual_panel)
    sample, summary = _prepare_event_sample(panel)

    rows: list[dict[str, object]] = []
    means_rows: list[dict[str, object]] = []
    table_frames: list[pd.DataFrame] = []
    for subset_key, panel_label in PANEL_SPECS:
        subset = _subset_sample(sample, subset_key)
        panel_rows, panel_means, panel_table = _paired_diffs(subset, panel_label)
        rows.extend(panel_rows)
        means_rows.extend(panel_means)
        table_frames.append(panel_table)
    table_df = _build_table(table_frames)
    means_df = pd.DataFrame(means_rows)

    stem = f"{TEST_ID}_{args.run_id}"
    docx_path = run_root / f"{stem}.docx"
    latex_path = run_root / f"{stem}.tex"
    csv_path = run_root / f"{stem}.csv"
    png_path = run_root / f"{stem}.png"
    pdf_path = run_root / f"{stem}.pdf"
    writer_packet_path = run_root / f"{stem}_writer_packet.md"
    result_notes_path = run_root / f"{stem}_result_notes.md"
    figure_series_path = run_root / f"{stem}_figure_series.csv"

    markdown = _render_markdown(table_df)
    latex = _render_latex(table_df)
    table_df.to_csv(csv_path, index=False)
    latex_path.write_text(latex, encoding="utf-8")
    _write_docx(docx_path, table_df, summary)
    _write_figure(means_df, png_path=png_path, pdf_path=pdf_path)
    _write_writer_packet(writer_packet_path, summary, rows)
    _write_result_notes(result_notes_path, rows)
    means_df.to_csv(figure_series_path, index=False)

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
        "inputs": {"annual_panel": str(args.annual_panel)},
        "sample_summary": summary,
        "paired_rows": rows,
        "figure_rows": means_rows,
        "outputs": {
            "docx": str(docx_path),
            "latex": str(latex_path),
            "csv": str(csv_path),
            "figure_png": str(png_path),
            "figure_pdf": str(pdf_path),
            "writer_packet": str(writer_packet_path),
            "result_notes": str(result_notes_path),
            "figure_series_csv": str(figure_series_path),
            "markdown_preview": markdown,
        },
    }
    (run_root / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
