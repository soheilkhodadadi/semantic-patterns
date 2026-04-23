"""Publication run driver for Test 20: disclosure cleanup after SEC comment-letter scrutiny."""

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
DEFAULT_EVENT_PANEL = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_2/test_runs/"
    "test_19_sec_comment_letter_scrutiny/20260423_aiw_v3_2_test_19_sec_comment_letter_scrutiny_main_v1/"
    "comment_letter_event_panel.parquet"
)
DEFAULT_TEST_ROOT = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_2/test_runs/test_20_comment_letter_cleanup"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated/v3_2"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_aiw_v3_2_test_20_comment_letter_cleanup_main_v1"
TEST_ID = "test_20_comment_letter_cleanup"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.test_20_comment_letter_cleanup"

EVENT_DEFINITIONS: list[tuple[str, str, str]] = [
    ("any_comment", "Panel A. First SEC comment letter (active AI disclosers)", "Any SEC comment"),
    (
        "ai_comment_broad",
        "Panel B. First AI-related SEC comment letter (active AI disclosers)",
        "AI-related SEC comment",
    ),
]
OUTCOMES: list[tuple[str, str]] = [
    ("SpecShare", "Speculative share"),
    ("A_S", "A/S ratio"),
    ("PatentMismatch", "PatentMismatch"),
    ("AI_Focus", "AI Focus"),
]
EVENT_WINDOWS = [-2, -1, 0, 1, 2]
COMPARE_WINDOWS = [-2, 0, 1, 2]


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


def _normalize_cik(value: object) -> str:
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())
    return digits.zfill(10) if digits else ""


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
    panel["cik"] = panel["cik"].map(_normalize_cik)
    panel["year"] = pd.to_numeric(panel["year"], errors="coerce").astype("Int64")
    panel = panel.loc[panel["year"].between(2016, 2025, inclusive="both")].copy()
    for column in ["SpecShare", "A_S", "PatentMismatch", "AI_Focus", "any_ai_talk"]:
        if column in panel.columns:
            panel[column] = pd.to_numeric(panel[column], errors="coerce")
    return panel


def _load_event_panel(path: Path) -> pd.DataFrame:
    events = pd.read_parquet(path).copy()
    events["cik"] = events["cik"].map(_normalize_cik)
    events["year"] = pd.to_numeric(events["year"], errors="coerce").astype("Int64")
    for column in ["any_comment", "ai_comment_narrow", "ai_comment_broad"]:
        if column in events.columns:
            events[column] = pd.to_numeric(events[column], errors="coerce").fillna(0).astype(int)
    return events


def _build_event_sample(panel: pd.DataFrame, events: pd.DataFrame, event_col: str) -> tuple[pd.DataFrame, dict[str, int]]:
    first_event = (
        events.loc[events[event_col].eq(1), ["cik", "year"]]
        .dropna()
        .sort_values(["cik", "year"])
        .groupby("cik", as_index=False)
        .first()
        .rename(columns={"year": "first_event_year"})
    )
    if first_event.empty:
        empty = pd.DataFrame(columns=[*panel.columns, "first_event_year", "event_time"])
        return empty, {"event_firms": 0, "active_firms": 0, "sample_rows": 0}

    merged = panel.merge(first_event, on="cik", how="inner", validate="many_to_one")
    merged["first_event_year"] = pd.to_numeric(merged["first_event_year"], errors="coerce").astype(int)
    merged["event_time"] = pd.to_numeric(merged["year"], errors="coerce").astype(int) - merged["first_event_year"]

    active_window = (
        merged.loc[merged["event_time"].isin([-1, 1]), ["cik", "event_time", "any_ai_talk"]]
        .pivot(index="cik", columns="event_time", values="any_ai_talk")
        .fillna(0)
    )
    active_firms = active_window.index[
        active_window.get(-1, pd.Series(0, index=active_window.index)).eq(1)
        & active_window.get(1, pd.Series(0, index=active_window.index)).eq(1)
    ]
    sample = merged.loc[merged["cik"].isin(active_firms) & merged["event_time"].isin(EVENT_WINDOWS)].copy()
    sample = sample.sort_values(["cik", "year"]).reset_index(drop=True)
    summary = {
        "event_firms": int(first_event["cik"].nunique()),
        "active_firms": int(sample["cik"].nunique()),
        "sample_rows": int(len(sample)),
    }
    return sample, summary


def _paired_diffs(sample: pd.DataFrame, event_label: str) -> tuple[list[dict[str, object]], list[dict[str, object]], pd.DataFrame]:
    rows: list[dict[str, object]] = []
    means_rows: list[dict[str, object]] = []
    pair_rows: list[dict[str, object]] = []

    for outcome, outcome_label in OUTCOMES:
        wide = (
            sample.loc[:, ["cik", "event_time", outcome]]
            .pivot_table(index="cik", columns="event_time", values=outcome, aggfunc="mean")
            .sort_index(axis=1)
        )
        pre = wide.get(-1)
        pre_mean = float(pre.dropna().mean()) if pre is not None else math.nan
        pair_rows.append(
            {
                "panel": event_label,
                "row_label": outcome_label,
                "event_t-2_vs_t-1": "",
                "event_t_vs_t-1": "",
                "event_t+1_vs_t-1": "",
                "event_t+2_vs_t-1": "",
                "pre_mean": pre_mean,
                "n_firms": int(wide.index.nunique()),
            }
        )
        for event_time in COMPARE_WINDOWS:
            series = wide.get(event_time)
            if series is None or pre is None:
                coef = se = p_value = math.nan
                n_pairs = 0
            else:
                diffs = (series - pre).dropna()
                n_pairs = int(len(diffs))
                coef = float(diffs.mean()) if n_pairs else math.nan
                se = float(diffs.std(ddof=1) / math.sqrt(n_pairs)) if n_pairs > 1 else math.nan
                p_value = (
                    float(stats.ttest_1samp(diffs, 0.0, nan_policy="omit").pvalue)
                    if n_pairs > 1
                    else math.nan
                )
            pair_rows[-1][
                {
                    -2: "event_t-2_vs_t-1",
                    0: "event_t_vs_t-1",
                    1: "event_t+1_vs_t-1",
                    2: "event_t+2_vs_t-1",
                }[event_time]
            ] = _cell(coef, se, p_value)
            rows.append(
                {
                    "panel": event_label,
                    "outcome": outcome,
                    "outcome_label": outcome_label,
                    "event_time": event_time,
                    "coef": coef,
                    "se": se,
                    "p_value": p_value,
                    "n_pairs": n_pairs,
                }
            )
        means = (
            sample.groupby("event_time", as_index=False)[outcome]
            .mean()
            .rename(columns={outcome: "mean_value"})
        )
        means["outcome"] = outcome
        means["outcome_label"] = outcome_label
        means["panel"] = event_label
        means_rows.extend(means.to_dict(orient="records"))

    return rows, means_rows, pd.DataFrame(pair_rows)


def _build_table(results_table: pd.DataFrame) -> pd.DataFrame:
    table = results_table.copy()
    table["Pre mean (t-1)"] = table["pre_mean"].map(lambda x: f"{x:.4f}" if math.isfinite(float(x)) else "")
    table["N firms"] = table["n_firms"].astype(int)
    return table[
        [
            "panel",
            "row_label",
            "event_t-2_vs_t-1",
            "event_t_vs_t-1",
            "event_t+1_vs_t-1",
            "event_t+2_vs_t-1",
            "Pre mean (t-1)",
            "N firms",
        ]
    ].rename(
        columns={
            "row_label": "Outcome",
            "event_t-2_vs_t-1": "t-2 vs t-1",
            "event_t_vs_t-1": "t vs t-1",
            "event_t+1_vs_t-1": "t+1 vs t-1",
            "event_t+2_vs_t-1": "t+2 vs t-1",
        }
    )


def _build_markdown(table_df: pd.DataFrame) -> str:
    frame = table_df.drop(columns=["panel"]).copy()
    headers = frame.columns.tolist()
    rows = [[str(value) for value in row] for row in frame.values.tolist()]
    return to_markdown_table(headers, rows)


def _render_latex(table_df: pd.DataFrame) -> str:
    lines = [
        "\\begin{table}[!htbp]",
        "\\centering",
        "\\caption{Disclosure cleanup after SEC comment-letter scrutiny}",
        "\\small",
        "\\begin{tabular}{lccccccl}",
        "\\hline",
        "Outcome & t-2 vs t-1 & t vs t-1 & t+1 vs t-1 & t+2 vs t-1 & Pre mean & N firms "
        + "\\\\",
        "\\hline",
    ]
    for panel, frame in table_df.groupby("panel", sort=False):
        lines.append(f"\\multicolumn{{7}}{{l}}{{\\textit{{{panel}}}}} " + "\\\\")
        for _, row in frame.iterrows():
            outcome = str(row["Outcome"]).replace("_", "\\_")
            lines.append(
                " & ".join(
                    [
                        outcome,
                        str(row["t-2 vs t-1"]),
                        str(row["t vs t-1"]),
                        str(row["t+1 vs t-1"]),
                        str(row["t+2 vs t-1"]),
                        str(row["Pre mean (t-1)"]),
                        str(row["N firms"]),
                    ]
                )
                + " "
                + "\\\\"
            )
        lines.append("\\hline")
    lines.extend(
        [
            "\\end{tabular}",
            "\\begin{flushleft}",
            "\\footnotesize Notes: Each cell reports the mean within-firm change relative to the filing year immediately before the first comment-letter event (`t-1`) among active AI disclosers, defined as firms that mention AI in both `t-1` and `t+1`. Standard errors are based on paired differences across firms. `AI-related SEC comment` uses the broad phrase match from Test 19 and should be read as a pilot because the event count is small.",
            "\\end{flushleft}",
            "\\end{table}",
        ]
    )
    return "\n".join(lines)


def _write_docx(table_df: pd.DataFrame, path: Path) -> None:
    document = Document()
    _set_document_defaults(document)
    _set_landscape(document)
    _add_title(document, "Test 20. Disclosure cleanup after SEC scrutiny")
    document.add_paragraph(
        "This table tracks how annual AI-disclosure outcomes change around a firm's first SEC comment-letter event. "
        "The main sample keeps active AI disclosers only, meaning the firm talks about AI both one year before and one year after the event, so the table measures composition cleanup rather than simple entry or exit from AI disclosure."
    )
    for panel, frame in table_df.groupby("panel", sort=False):
        document.add_paragraph(panel)
        headers = list(frame.drop(columns=["panel"]).columns)
        rows = [
            [(str(value), False) for value in row]
            for row in frame.drop(columns=["panel"]).values.tolist()
        ]
        _build_panel_table(
            document,
            headers,
            rows,
        )
        document.add_paragraph()
    _add_note(
        document,
        "Each cell reports a mean paired difference relative to `t-1`; standard errors use the cross-firm paired-difference standard error. The AI-related comment-letter panel is a pilot because the targeted event count is small."
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    document.save(path)


def _plot_event_paths(means_df: pd.DataFrame, path: Path) -> None:
    _base_style()
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.2), sharex=True)
    axes = axes.flatten()
    color_map = {
        "Any SEC comment": "#1f4e79",
        "AI-related SEC comment": "#b35c1e",
    }
    for ax, (outcome, outcome_label) in zip(axes, OUTCOMES, strict=True):
        subset = means_df.loc[means_df["outcome"].eq(outcome)].copy()
        for short_label, frame in subset.groupby("short_label", sort=False):
            frame = frame.sort_values("event_time")
            ax.plot(
                frame["event_time"],
                frame["mean_value"],
                marker="o",
                linewidth=2,
                label=short_label,
                color=color_map.get(short_label),
            )
        ax.axvline(0, color="black", linestyle="--", linewidth=0.8)
        ax.set_title(outcome_label)
        ax.set_xlabel("Event time")
        ax.set_ylabel("Mean value")
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False)
    fig.suptitle("Disclosure path around the first SEC comment-letter event", y=0.98)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    pdf_path = path.with_suffix(".pdf")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)


def _writer_packet(
    *,
    sample_summaries: dict[str, dict[str, int]],
    keyed: dict[tuple[str, str, int], dict[str, object]],
    path: Path,
) -> None:
    any_as = keyed[("Any SEC comment", "A_S", 1)]
    any_spec = keyed[("Any SEC comment", "SpecShare", 2)]
    any_pm = keyed[("Any SEC comment", "PatentMismatch", 1)]
    lines = [
        "# Writer Packet: Test 20 disclosure cleanup after SEC scrutiny",
        "",
        "## What this run does",
        "",
        "- Anchors on each firm's first SEC comment-letter year from Test 19.",
        "- Restricts the main sample to active AI disclosers: firms that talk about AI both at `t-1` and `t+1`.",
        "- Measures within-firm paired changes in disclosure composition relative to `t-1`.",
        "",
        "## Why this design matters",
        "",
        "- It avoids a mechanical entry/exit story where disclosure falls just because the firm stops mentioning AI entirely.",
        "- It is a direct oversight-discipline test: after scrutiny, do continuing AI disclosers become more credible?",
        "",
        "## Sample",
        "",
        f"- Any-comment active sample: `{sample_summaries['any_comment']['active_firms']}` firms and `{sample_summaries['any_comment']['sample_rows']}` event-window rows.",
        f"- AI-related comment active sample: `{sample_summaries['ai_comment_broad']['active_firms']}` firms and `{sample_summaries['ai_comment_broad']['sample_rows']}` rows.",
        "",
        "## Headline read",
        "",
        f"- In the main any-comment sample, `A/S` rises by `+{any_as['coef']:.4f}` at `t+1` (p=`{any_as['p_value']:.3f}`).",
        f"- `SpecShare` falls by `{any_spec['coef']:.4f}` at `t+2` (p=`{any_spec['p_value']:.3f}`).",
        f"- `PatentMismatch` declines by `{any_pm['coef']:.4f}` at `t+1` (p=`{any_pm['p_value']:.3f}`).",
        "- `AI_Focus` rises after scrutiny, so the pattern is not silence; it is more compatible with continuing AI talk alongside cleaner composition.",
        "",
        "## Interpretation discipline",
        "",
        "- This is a within-firm dynamic response, not a causal claim about why the SEC chose to comment.",
        "- The AI-related comment subset is still useful, but it remains a pilot because the event count is small.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _result_notes(
    *,
    sample_summaries: dict[str, dict[str, int]],
    keyed: dict[tuple[str, str, int], dict[str, object]],
    path: Path,
) -> None:
    lines = [
        "- Test 20 asks whether disclosure composition changes after SEC scrutiny among firms that keep talking about AI.",
        f"- Main any-comment active sample: `{sample_summaries['any_comment']['active_firms']}` firms.",
        f"- AI-related comment active sample: `{sample_summaries['ai_comment_broad']['active_firms']}` firms.",
        f"- Any-comment `A/S` change at `t+1`: `{keyed[('Any SEC comment', 'A_S', 1)]['coef']:.4f}` (p=`{keyed[('Any SEC comment', 'A_S', 1)]['p_value']:.3f}`).",
        f"- Any-comment `SpecShare` change at `t+2`: `{keyed[('Any SEC comment', 'SpecShare', 2)]['coef']:.4f}` (p=`{keyed[('Any SEC comment', 'SpecShare', 2)]['p_value']:.3f}`).",
        f"- Any-comment `PatentMismatch` change at `t+1`: `{keyed[('Any SEC comment', 'PatentMismatch', 1)]['coef']:.4f}` (p=`{keyed[('Any SEC comment', 'PatentMismatch', 1)]['p_value']:.3f}`).",
        "- Read this as evidence of composition cleanup among ongoing AI disclosers, not as evidence that scrutiny suppresses AI talk overall.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = _parse_args()
    run_dir = args.test_root / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    panel = _load_panel(args.annual_panel)
    events = _load_event_panel(args.event_panel)

    all_rows: list[dict[str, object]] = []
    means_rows: list[dict[str, object]] = []
    sample_summaries: dict[str, dict[str, int]] = {}
    table_blocks: list[pd.DataFrame] = []

    for event_col, panel_label, short_label in EVENT_DEFINITIONS:
        sample, summary = _build_event_sample(panel, events, event_col)
        sample_summaries[event_col] = summary
        rows, means, block = _paired_diffs(sample, panel_label)
        for row in rows:
            row["short_label"] = short_label
        for row in means:
            row["short_label"] = short_label
        all_rows.extend(rows)
        means_rows.extend(means)
        table_blocks.append(block)

    results = pd.DataFrame(all_rows)
    means_df = pd.DataFrame(means_rows)
    table_df = _build_table(pd.concat(table_blocks, ignore_index=True))
    keyed = {
        (row["short_label"], row["outcome"], int(row["event_time"])): row
        for row in results.to_dict(orient="records")
    }

    base_name = f"{TEST_ID}_{args.run_id}"
    local_table_csv = run_dir / f"{base_name}.csv"
    local_table_csv.parent.mkdir(parents=True, exist_ok=True)
    table_df.to_csv(local_table_csv, index=False)
    local_means_csv = run_dir / f"{base_name}_event_means.csv"
    means_df.to_csv(local_means_csv, index=False)

    local_markdown = run_dir / f"{base_name}.md"
    local_markdown.write_text(_build_markdown(table_df), encoding="utf-8")
    local_tex = run_dir / f"{base_name}.tex"
    local_tex.write_text(_render_latex(table_df), encoding="utf-8")
    local_docx = run_dir / f"{base_name}.docx"
    _write_docx(table_df, local_docx)
    local_png = run_dir / f"{base_name}.png"
    _plot_event_paths(means_df, local_png)

    writer_packet = run_dir / f"{base_name}_writer_packet.md"
    _writer_packet(sample_summaries=sample_summaries, keyed=keyed, path=writer_packet)
    notes_path = run_dir / f"{base_name}_result_notes.md"
    _result_notes(sample_summaries=sample_summaries, keyed=keyed, path=notes_path)

    paper_dirs = {
        "docx": args.paper_root / "docx",
        "latex": args.paper_root / "latex",
        "tables": args.paper_root / "tables",
        "figures": args.paper_root / "figures",
        "writer_packets": args.paper_root / "writer_packets",
        "snippets": args.paper_root / "snippets",
    }
    for dest in paper_dirs.values():
        dest.mkdir(parents=True, exist_ok=True)

    paper_docx = paper_dirs["docx"] / f"{base_name}.docx"
    paper_tex = paper_dirs["latex"] / f"{base_name}.tex"
    paper_csv = paper_dirs["tables"] / f"{base_name}.csv"
    paper_means_csv = paper_dirs["tables"] / f"{base_name}_event_means.csv"
    paper_png = paper_dirs["figures"] / f"{base_name}.png"
    paper_pdf = paper_dirs["figures"] / f"{base_name}.pdf"
    paper_writer = paper_dirs["writer_packets"] / f"{base_name}.md"
    paper_notes = paper_dirs["snippets"] / f"{base_name}_result_notes.md"

    shutil.copy2(local_docx, paper_docx)
    shutil.copy2(local_tex, paper_tex)
    shutil.copy2(local_table_csv, paper_csv)
    shutil.copy2(local_means_csv, paper_means_csv)
    shutil.copy2(local_png, paper_png)
    shutil.copy2(local_png.with_suffix(".pdf"), paper_pdf)
    shutil.copy2(writer_packet, paper_writer)
    shutil.copy2(notes_path, paper_notes)

    manifest = {
        "test_id": TEST_ID,
        "module_path": MODULE_PATH,
        "run_id": args.run_id,
        "run_timestamp_utc": datetime.now(UTC).isoformat(),
        "inputs": {
            "annual_panel": str(args.annual_panel),
            "event_panel": str(args.event_panel),
        },
        "sample_summaries": sample_summaries,
        "paper_outputs": {
            "table_docx": str(paper_docx),
            "table_tex": str(paper_tex),
            "table_csv": str(paper_csv),
            "event_means_csv": str(paper_means_csv),
            "figure_png": str(paper_png),
            "figure_pdf": str(paper_pdf),
            "writer_packet": str(paper_writer),
            "result_notes": str(paper_notes),
        },
        "local_outputs": {
            "table_docx": str(local_docx),
            "table_tex": str(local_tex),
            "table_csv": str(local_table_csv),
            "event_means_csv": str(local_means_csv),
            "figure_png": str(local_png),
            "writer_packet": str(writer_packet),
            "result_notes": str(notes_path),
        },
        "results": results.to_dict(orient="records"),
    }
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
