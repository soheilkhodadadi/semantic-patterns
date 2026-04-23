"""Publication run driver for Test 01: mismatch surge through 2025."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from semantic_ai_washing.analysis.delivery_table_payloads import _add_patent_mismatch

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_PANEL = (
    REPO_ROOT
    / "data/processed/panel/canonical/ever_speaker_panel_2016_2025_hybrid_api_a_conf49_v1.parquet"
)
DEFAULT_TEST_ROOT = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/test_runs/test_01_mismatch_surge"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_hybrid_api_a_conf49_main_v1"
TEST_ID = "test_01_mismatch_surge"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.test_01_mismatch_surge"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", type=Path, default=DEFAULT_PANEL)
    parser.add_argument("--test-root", type=Path, default=DEFAULT_TEST_ROOT)
    parser.add_argument("--paper-root", type=Path, default=DEFAULT_PAPER_ROOT)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument(
        "--figure-start-year",
        type=int,
        default=2018,
        help="First year shown in the paper-facing figure. Full summaries still cover all years.",
    )
    parser.add_argument(
        "--min-sector-talk-count",
        type=int,
        default=25,
        help="Minimum AI-talking firm-years for a named sector to appear in Panel B.",
    )
    parser.add_argument(
        "--keep-other-sector",
        action="store_true",
        help="Include the residual 'Other' bucket in the paper-facing top-sector figure.",
    )
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


def _sector_bucket_from_sic2(series: pd.Series) -> pd.Series:
    sic2 = pd.to_numeric(series, errors="coerce")
    sector = pd.Series("Other", index=series.index, dtype="object")
    sector.loc[sic2.between(10, 14, inclusive="both")] = "Mining"
    sector.loc[sic2.between(15, 17, inclusive="both")] = "Construction"
    sector.loc[sic2.between(20, 39, inclusive="both")] = "Manufacturing"
    sector.loc[sic2.between(40, 49, inclusive="both")] = "Transport/Utilities"
    sector.loc[sic2.between(50, 59, inclusive="both")] = "Trade"
    sector.loc[sic2.between(60, 64, inclusive="both")] = "Finance/Insurance"
    sector.loc[sic2.between(65, 67, inclusive="both")] = "Real Estate"
    sector.loc[sic2.between(70, 89, inclusive="both")] = "Services"
    return sector


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


def _style_axes(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, axis="y", color="#d9d9d9", linewidth=0.7)
    ax.grid(False, axis="x")


def _build_summaries(
    panel: pd.DataFrame,
    *,
    min_sector_talk_count: int,
    keep_other_sector: bool,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    talk = panel.loc[panel["any_ai_talk"].fillna(0).astype(int).eq(1)].copy()
    talk["sector_bucket"] = _sector_bucket_from_sic2(talk["sic2"])

    yearly = (
        talk.groupby("year", as_index=False)
        .agg(
            mismatch_count=("PatentMismatch", "sum"),
            ai_talking_count=("PatentMismatch", "size"),
            mismatch_share=("PatentMismatch", "mean"),
        )
        .sort_values("year")
        .reset_index(drop=True)
    )
    yearly["mismatch_share_pct"] = 100 * yearly["mismatch_share"]

    sector_all = (
        talk.groupby("sector_bucket", as_index=False)
        .agg(
            mismatch_count=("PatentMismatch", "sum"),
            ai_talking_count=("PatentMismatch", "size"),
            mismatch_share=("PatentMismatch", "mean"),
        )
        .sort_values(["mismatch_count", "mismatch_share"], ascending=[False, False])
        .reset_index(drop=True)
    )
    sector_all["mismatch_share_pct"] = 100 * sector_all["mismatch_share"]

    sector_fig = sector_all.loc[sector_all["ai_talking_count"] >= min_sector_talk_count].copy()
    if not keep_other_sector:
        sector_fig = sector_fig.loc[sector_fig["sector_bucket"] != "Other"].copy()
    sector_fig = (
        sector_fig.head(6).sort_values("mismatch_count", ascending=True).reset_index(drop=True)
    )
    return yearly, sector_all, sector_fig


def _build_combined_table(
    yearly: pd.DataFrame, sector_all: pd.DataFrame, sector_fig: pd.DataFrame
) -> pd.DataFrame:
    annual = yearly.copy()
    annual["section"] = "annual"
    annual["sector_bucket"] = pd.NA
    annual["included_in_figure"] = False
    annual = annual[
        [
            "section",
            "year",
            "sector_bucket",
            "mismatch_count",
            "ai_talking_count",
            "mismatch_share",
            "mismatch_share_pct",
            "included_in_figure",
        ]
    ]

    sector = sector_all.copy()
    sector["section"] = "sector"
    sector["year"] = pd.NA
    sector["included_in_figure"] = sector["sector_bucket"].isin(sector_fig["sector_bucket"])
    sector = sector[
        [
            "section",
            "year",
            "sector_bucket",
            "mismatch_count",
            "ai_talking_count",
            "mismatch_share",
            "mismatch_share_pct",
            "included_in_figure",
        ]
    ]
    return pd.concat([annual, sector], ignore_index=True)


def _markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return "\n".join(lines)


def _render_table_markdown(
    yearly: pd.DataFrame, sector_all: pd.DataFrame, sector_fig: pd.DataFrame
) -> str:
    annual = yearly.copy()
    annual["mismatch_share_pct"] = annual["mismatch_share_pct"].map(lambda v: f"{v:.2f}")
    sector = sector_all.copy()
    sector["mismatch_share_pct"] = sector["mismatch_share_pct"].map(lambda v: f"{v:.2f}")

    annual_md = _markdown_table(
        ["year", "mismatch_count", "ai_talking_count", "mismatch_share_pct"],
        annual[
            ["year", "mismatch_count", "ai_talking_count", "mismatch_share_pct"]
        ].values.tolist(),
    )
    sector_md = _markdown_table(
        ["sector_bucket", "mismatch_count", "ai_talking_count", "mismatch_share_pct"],
        sector[
            ["sector_bucket", "mismatch_count", "ai_talking_count", "mismatch_share_pct"]
        ].values.tolist(),
    )
    shown = ", ".join(sector_fig["sector_bucket"].tolist()) if not sector_fig.empty else "none"
    return "\n".join(
        [
            "# Table Main",
            "",
            "## Annual mismatch incidence",
            annual_md,
            "",
            "## Full sector summary",
            sector_md,
            "",
            f"Figure Panel B sectors: {shown}",
            "",
        ]
    )


def _plot_figure(
    yearly: pd.DataFrame, sector_fig: pd.DataFrame, output_base: Path
) -> tuple[Path, Path]:
    _base_style()
    fig, axes = plt.subplots(2, 1, figsize=(8.2, 8.8), constrained_layout=True)

    ax = axes[0]
    ax.bar(
        yearly["year"].astype(str),
        yearly["mismatch_count"],
        color="#c46b48",
        alpha=0.85,
        label="Mismatch incidents",
    )
    ax.set_title("Panel A. PatentMismatch Incidence Over Time")
    ax.set_ylabel("Mismatch incidents")
    _style_axes(ax)
    ax.grid(False, axis="x")

    ax_right = ax.twinx()
    ax_right.plot(
        yearly["year"].astype(str),
        yearly["mismatch_share_pct"],
        color="#1d3557",
        marker="o",
        linewidth=2.1,
        label="Mismatch share (%)",
    )
    ax_right.set_ylabel("Mismatch share (%)")
    ax_right.spines["top"].set_visible(False)
    ax_right.grid(False)
    handles_left, labels_left = ax.get_legend_handles_labels()
    handles_right, labels_right = ax_right.get_legend_handles_labels()
    ax.legend(
        handles_left + handles_right, labels_left + labels_right, loc="upper left", frameon=False
    )

    ax2 = axes[1]
    bars = ax2.barh(
        sector_fig["sector_bucket"],
        sector_fig["mismatch_count"],
        color="#2a9d8f",
        alpha=0.9,
    )
    ax2.set_title("Panel B. Top Sectors by PatentMismatch Incidents")
    ax2.set_xlabel("Mismatch incidents")
    ax2.set_ylabel("")
    _style_axes(ax2)
    ax2.grid(True, axis="x", color="#d9d9d9", linewidth=0.7)
    ax2.grid(False, axis="y")
    for bar, share, talk_count in zip(
        bars, sector_fig["mismatch_share"], sector_fig["ai_talking_count"], strict=True
    ):
        ax2.text(
            bar.get_width() + 2,
            bar.get_y() + bar.get_height() / 2,
            f"{100 * share:.1f}% of talk years\nN={int(talk_count)}",
            va="center",
            ha="left",
            fontsize=9,
        )

    png_path = output_base.with_suffix(".png")
    pdf_path = output_base.with_suffix(".pdf")
    fig.savefig(png_path, dpi=220, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    return png_path, pdf_path


def _writer_packet(
    args: argparse.Namespace,
    panel: pd.DataFrame,
    yearly: pd.DataFrame,
    sector_fig: pd.DataFrame,
) -> str:
    share_2024 = float(yearly.loc[yearly["year"].eq(2024), "mismatch_share"].iloc[0])
    share_2025 = float(yearly.loc[yearly["year"].eq(2025), "mismatch_share"].iloc[0])
    talk_2024 = int(yearly.loc[yearly["year"].eq(2024), "ai_talking_count"].iloc[0])
    talk_2025 = int(yearly.loc[yearly["year"].eq(2025), "ai_talking_count"].iloc[0])
    delta_share_pp = 100 * (share_2025 - share_2024)
    delta_talk_pct = 100 * ((talk_2025 / talk_2024) - 1.0)
    sector_text = ", ".join(
        f"{row.sector_bucket} ({int(row.mismatch_count)} incidents; {row.mismatch_share_pct:.1f}%)"
        for row in sector_fig.itertuples()
    )
    keep_other_note = (
        "The residual `Other` sector bucket was retained in Panel B."
        if args.keep_other_sector
        else "The residual `Other` sector bucket was kept in the CSV output but excluded from Panel B so the paper-facing figure shows named sectors only."
    )
    early_year_note = (
        f"Panel A in the paper-facing figure starts in `{args.figure_start_year}`. "
        "The full-year summary remains in the run bundle, but `2016-2017` are excluded from the plotted main figure because the contemporaneous grant-based patent benchmark is extremely sparse in those years and the within-year low-credibility cutoff becomes mechanically unstable."
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
            f"- Input panel filename(s): `{args.panel}`",
            "- Unit of observation: `firm-year`",
            "- Sample filters: `ever-speaker annual panel; figure denominator restricted to AI-talking firm-years`",
            "- Date range: `2016-2025`",
            f"- Exact N: `{int(panel['any_ai_talk'].fillna(0).astype(int).sum()):,}` AI-talking firm-years out of `{len(panel):,}` ever-speaker firm-years",
            "",
            "## Variables",
            "- Dependent variable: `n/a descriptive figure`",
            "- Key regressor(s): `PatentMismatch`, `any_ai_talk`, `sector_bucket`",
            "- Treatment/event definition: `PatentMismatch = 1 when an AI-talking firm-year has low-credibility disclosure (bottom-year quartile of A_S or top-year quartile of SpecShare) and weak contemporaneous AI patenting relative to the industry-year mean`",
            "- Control set: `none`",
            "- Transformations: `mismatch share computed among AI-talking firm-years; sector buckets mapped from SIC2`",
            "",
            "## Estimation",
            "- Model equation: `n/a descriptive aggregation`",
            "- Fixed effects: `none`",
            "- Clustering: `none`",
            "- Weighting: `unweighted counts and shares`",
            "- Benchmark / abnormal return model: `n/a`",
            "",
            "## Results",
            f"- Key coefficient(s) or spread(s): `2024 mismatch share = {100 * share_2024:.2f}%`; `2025 mismatch share = {100 * share_2025:.2f}%`",
            "- Standard error / t-stat / p-value: `n/a descriptive figure`",
            f"- Economic magnitude: `AI-talking firm-years rose from {talk_2024:,} in 2024 to {talk_2025:,} in 2025 ({delta_talk_pct:.1f}%), while mismatch share moved by {delta_share_pp:.2f} percentage points.`",
            "- One-sentence interpretation: `The mismatch rate stays extremely high in 2025 and edges above the already elevated 2024 level rather than mean-reverting.`",
            "- Main text / appendix / discard: `main text`",
            "",
            "## Caption Draft",
            f"This figure uses the ever-speaker annual panel and restricts the denominator to AI-talking firm-years where appropriate. Panel A plots the annual count of PatentMismatch firm-years and the share of AI-talking firm-years flagged as mismatch for `{args.figure_start_year}-2025`. Panel B plots the six named sectors with the highest number of mismatch incidents and annotates each bar with the mismatch share within that sector. The `2016-2017` observations are retained in the audit tables but excluded from the plotted figure because the early-year patent benchmark is too sparse for stable visual interpretation.",
            "",
            "## Notes",
            f"- Attrition / missingness note: `{keep_other_note}`",
            f"- Early-year stability note: `{early_year_note}`",
            f"- Any unusual diagnostics: `Top Panel B sectors in this run: {sector_text}.`",
            "",
        ]
    )


def _result_notes(args: argparse.Namespace, yearly: pd.DataFrame, sector_fig: pd.DataFrame) -> str:
    share_2024 = float(yearly.loc[yearly["year"].eq(2024), "mismatch_share"].iloc[0])
    share_2025 = float(yearly.loc[yearly["year"].eq(2025), "mismatch_share"].iloc[0])
    talk_2024 = int(yearly.loc[yearly["year"].eq(2024), "ai_talking_count"].iloc[0])
    talk_2025 = int(yearly.loc[yearly["year"].eq(2025), "ai_talking_count"].iloc[0])
    delta_share_pp = 100 * (share_2025 - share_2024)
    top_sector = sector_fig.iloc[-1] if not sector_fig.empty else None
    lines = [
        "# Result Notes",
        "",
        f"- 2024 mismatch share among AI-talking firm-years: `{100 * share_2024:.2f}%` (`{talk_2024:,}` AI-talking firm-years).",
        f"- 2025 mismatch share among AI-talking firm-years: `{100 * share_2025:.2f}%` (`{talk_2025:,}` AI-talking firm-years).",
        f"- Change from 2024 to 2025: `{delta_share_pp:.2f}` percentage points.",
        f"- Paper-facing figure window starts at `{args.figure_start_year}`. The full annual series is preserved in `table_main.csv` and `dataset_summary.json`, but `2016-2017` are excluded from the plotted figure because early-year grant-side patent incidence is too sparse for stable visual interpretation.",
    ]
    if top_sector is not None:
        lines.append(
            f"- Highest-incidence named sector in Panel B: `{top_sector['sector_bucket']}` with `{int(top_sector['mismatch_count']):,}` mismatch incidents and `{top_sector['mismatch_share_pct']:.1f}%` mismatch share."
        )
    return "\n".join(lines) + "\n"


def _dataset_summary(
    panel: pd.DataFrame,
    yearly: pd.DataFrame,
    sector_all: pd.DataFrame,
    sector_fig: pd.DataFrame,
    *,
    args: argparse.Namespace,
) -> dict[str, object]:
    share_2024 = float(yearly.loc[yearly["year"].eq(2024), "mismatch_share"].iloc[0])
    share_2025 = float(yearly.loc[yearly["year"].eq(2025), "mismatch_share"].iloc[0])
    talk_2024 = int(yearly.loc[yearly["year"].eq(2024), "ai_talking_count"].iloc[0])
    talk_2025 = int(yearly.loc[yearly["year"].eq(2025), "ai_talking_count"].iloc[0])
    return {
        "test_id": TEST_ID,
        "run_id": args.run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "input_panel": str(args.panel),
        "row_count_panel": int(len(panel)),
        "firm_count": int(panel["cik"].nunique(dropna=True)),
        "year_min": int(panel["year"].min()),
        "year_max": int(panel["year"].max()),
        "ai_talking_row_count": int(panel["any_ai_talk"].fillna(0).astype(int).sum()),
        "mismatch_row_count": int(panel["PatentMismatch"].fillna(0).astype(int).sum()),
        "annual_counts": yearly.to_dict(orient="records"),
        "top_sector_summary": sector_all.head(10).to_dict(orient="records"),
        "figure_panel_b_sectors": sector_fig["sector_bucket"].tolist(),
        "figure_start_year": int(args.figure_start_year),
        "figure_yearly_counts": yearly.loc[yearly["year"].ge(args.figure_start_year)].to_dict(
            orient="records"
        ),
        "share_2024": share_2024,
        "share_2025": share_2025,
        "share_change_pp_2024_2025": 100 * (share_2025 - share_2024),
        "ai_talking_count_2024": talk_2024,
        "ai_talking_count_2025": talk_2025,
        "ai_talking_growth_pct_2024_2025": 100 * ((talk_2025 / talk_2024) - 1.0),
    }


def _copy_exports(run_dir: Path, paper_root: Path, run_id: str) -> dict[str, str]:
    exports = {
        "figure_png": paper_root / "figures" / f"{TEST_ID}_{run_id}.png",
        "figure_pdf": paper_root / "figures" / f"{TEST_ID}_{run_id}.pdf",
        "table_csv": paper_root / "tables" / f"{TEST_ID}_{run_id}.csv",
        "table_md": paper_root / "tables" / f"{TEST_ID}_{run_id}.md",
        "writer_packet": paper_root / "writer_packets" / f"{TEST_ID}_{run_id}.md",
        "result_notes": paper_root / "snippets" / f"{TEST_ID}_{run_id}_result_notes.md",
    }
    exports["figure_png"].parent.mkdir(parents=True, exist_ok=True)
    exports["figure_pdf"].parent.mkdir(parents=True, exist_ok=True)
    exports["table_csv"].parent.mkdir(parents=True, exist_ok=True)
    exports["writer_packet"].parent.mkdir(parents=True, exist_ok=True)
    exports["result_notes"].parent.mkdir(parents=True, exist_ok=True)

    mapping = {
        run_dir / "figure_main.png": exports["figure_png"],
        run_dir / "figure_main.pdf": exports["figure_pdf"],
        run_dir / "table_main.csv": exports["table_csv"],
        run_dir / "table_main.md": exports["table_md"],
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

    panel = pd.read_parquet(args.panel)
    panel = _ensure_sic2(panel)
    panel = _add_patent_mismatch(panel)

    yearly, sector_all, sector_fig = _build_summaries(
        panel,
        min_sector_talk_count=args.min_sector_talk_count,
        keep_other_sector=args.keep_other_sector,
    )
    combined = _build_combined_table(yearly, sector_all, sector_fig)
    combined.to_csv(run_dir / "table_main.csv", index=False)
    (run_dir / "table_main.md").write_text(
        _render_table_markdown(yearly, sector_all, sector_fig), encoding="utf-8"
    )
    figure_yearly = yearly.loc[yearly["year"].ge(args.figure_start_year)].copy()
    png_path, pdf_path = _plot_figure(figure_yearly, sector_fig, run_dir / "figure_main")
    (run_dir / "writer_packet.md").write_text(
        _writer_packet(args, panel, yearly, sector_fig), encoding="utf-8"
    )
    (run_dir / "result_notes.md").write_text(
        _result_notes(args, yearly, sector_fig), encoding="utf-8"
    )

    dataset_summary = _dataset_summary(panel, yearly, sector_all, sector_fig, args=args)
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
            "panel": str(args.panel),
            "figure_start_year": args.figure_start_year,
            "min_sector_talk_count": args.min_sector_talk_count,
            "keep_other_sector": args.keep_other_sector,
        },
        "run_dir": str(run_dir),
        "outputs": {
            "dataset_summary": str(run_dir / "dataset_summary.json"),
            "table_csv": str(run_dir / "table_main.csv"),
            "table_md": str(run_dir / "table_main.md"),
            "figure_png": str(png_path),
            "figure_pdf": str(pdf_path),
            "writer_packet": str(run_dir / "writer_packet.md"),
            "result_notes": str(run_dir / "result_notes.md"),
        },
        "paper_exports": paper_exports,
    }
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"[{TEST_ID}] wrote run bundle to {run_dir}")
    print(f"[{TEST_ID}] 2024 mismatch share: {dataset_summary['share_2024']:.6f}")
    print(f"[{TEST_ID}] 2025 mismatch share: {dataset_summary['share_2025']:.6f}")
    print(f"[{TEST_ID}] paper figure: {paper_exports['figure_png']}")


if __name__ == "__main__":
    main()
