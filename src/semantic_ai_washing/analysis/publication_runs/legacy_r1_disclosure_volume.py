"""Publication run driver for legacy Figure R1: AI disclosure volume and composition."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from semantic_ai_washing.analysis.build_delivery_figures import (
    _base_style,
    _save_figure_docx,
    _style_axes,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_ANNUAL_PANEL = (
    REPO_ROOT
    / "data/processed/panel/canonical/ever_speaker_panel_2016_2025_hybrid_api_a_conf49_v1.parquet"
)
DEFAULT_TEST_ROOT = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/test_runs/legacy_r1_disclosure_volume"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_hybrid_api_a_conf49_main_v1"
TEST_ID = "legacy_r1_disclosure_volume"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.legacy_r1_disclosure_volume"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annual-panel", type=Path, default=DEFAULT_ANNUAL_PANEL)
    parser.add_argument("--test-root", type=Path, default=DEFAULT_TEST_ROOT)
    parser.add_argument("--paper-root", type=Path, default=DEFAULT_PAPER_ROOT)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    return parser.parse_args()


def _load_yearly(panel_path: Path) -> tuple[pd.DataFrame, dict[str, object]]:
    df = pd.read_parquet(panel_path)
    yearly = (
        df.groupby("year", as_index=False)
        .agg(
            ai_total_mean=("ai_total", "mean"),
            n_A_mean=("n_A", "mean"),
            n_S_mean=("n_S", "mean"),
            any_ai_share=("any_ai_talk", "mean"),
            firm_years=("cik", "size"),
        )
        .sort_values("year")
    )
    talker = df.loc[pd.to_numeric(df["any_ai_talk"], errors="coerce").fillna(0).gt(0)].copy()
    comp = (
        talker.groupby("year", as_index=False)
        .agg(act_share_mean=("ActShare", "mean"), spec_share_mean=("SpecShare", "mean"))
        .sort_values("year")
    )
    yearly = yearly.merge(comp, on="year", how="left")
    summary = {
        "panel_rows": int(len(df)),
        "ai_talk_rows": int(pd.to_numeric(df["any_ai_talk"], errors="coerce").fillna(0).sum()),
        "year_min": int(pd.to_numeric(df["year"], errors="coerce").min()),
        "year_max": int(pd.to_numeric(df["year"], errors="coerce").max()),
    }
    return yearly, summary


def _plot(yearly: pd.DataFrame, output_base: Path) -> tuple[Path, Path]:
    _base_style()
    fig, axes = plt.subplots(2, 1, figsize=(8.2, 8.8), constrained_layout=True)

    ax = axes[0]
    ax.plot(
        yearly["year"],
        yearly["ai_total_mean"],
        color="#22333b",
        marker="o",
        linewidth=2.3,
        label="AI sentences",
    )
    ax.plot(
        yearly["year"],
        yearly["n_A_mean"],
        color="#2a9d8f",
        marker="o",
        linewidth=2.0,
        label="Actionable",
    )
    ax.plot(
        yearly["year"],
        yearly["n_S_mean"],
        color="#c46b48",
        marker="o",
        linewidth=2.0,
        label="Speculative",
    )
    ax.set_title("Panel A. Mean AI Disclosure Counts per Firm-Year")
    ax.set_ylabel("Mean count")
    ax.set_xticks(yearly["year"].astype(int).tolist())
    ax.set_xlim(int(yearly["year"].min()), int(yearly["year"].max()))
    ax.legend(loc="upper left", frameon=False)
    _style_axes(ax)

    ax2 = axes[1]
    ax2.plot(
        yearly["year"],
        yearly["act_share_mean"],
        color="#2a9d8f",
        marker="o",
        linewidth=2.2,
        label="Actionable share",
    )
    ax2.plot(
        yearly["year"],
        yearly["spec_share_mean"],
        color="#c46b48",
        marker="o",
        linewidth=2.2,
        label="Speculative share",
    )
    ax2.plot(
        yearly["year"],
        yearly["any_ai_share"],
        color="#6c757d",
        marker="o",
        linewidth=1.8,
        linestyle="--",
        label="Any AI talk share",
    )
    ax2.set_title("Panel B. Disclosure Composition Over Time")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Share")
    ax2.set_ylim(bottom=0)
    ax2.set_xticks(yearly["year"].astype(int).tolist())
    ax2.set_xlim(int(yearly["year"].min()), int(yearly["year"].max()))
    ax2.legend(loc="upper left", frameon=False)
    _style_axes(ax2)

    png_path = output_base.with_suffix(".png")
    pdf_path = output_base.with_suffix(".pdf")
    fig.savefig(png_path, dpi=220, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    return png_path, pdf_path


def _result_notes(yearly: pd.DataFrame, summary: dict[str, object]) -> str:
    first = yearly.iloc[0]
    last = yearly.iloc[-1]
    return "\n".join(
        [
            "# Result Notes",
            "",
            (
                f"- Expanded ever-speaker panel spans `{summary['year_min']}`-`{summary['year_max']}` with "
                f"`{summary['panel_rows']:,}` firm-years and `{summary['ai_talk_rows']:,}` AI-talking firm-years."
            ),
            (
                f"- Mean AI sentences per firm-year rise from `{first['ai_total_mean']:.3f}` in `{int(first['year'])}` "
                f"to `{last['ai_total_mean']:.3f}` in `{int(last['year'])}`."
            ),
            (
                f"- Any-AI-talk share rises from `{100 * first['any_ai_share']:.1f}%` to "
                f"`{100 * last['any_ai_share']:.1f}%` across the sample window."
            ),
            (
                f"- Among AI-talking firm-years, mean actionable share moves from `{100 * first['act_share_mean']:.1f}%` "
                f"to `{100 * last['act_share_mean']:.1f}%`, while mean speculative share moves from "
                f"`{100 * first['spec_share_mean']:.1f}%` to `{100 * last['spec_share_mean']:.1f}%`."
            ),
            "",
        ]
    )


def _writer_packet(args: argparse.Namespace, summary: dict[str, object]) -> str:
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
            "",
            "## Sample",
            (
                f"- Expanded ever-speaker panel: `{summary['panel_rows']:,}` firm-years, "
                f"`{summary['year_min']}`-`{summary['year_max']}`"
            ),
            f"- AI-talking firm-years: `{summary['ai_talk_rows']:,}`",
            "",
            "## Caption Draft",
            "This figure uses the expanded 2016-2025 ever-speaker annual panel. Panel A plots mean AI sentence counts per firm-year, separating total AI sentences from the actionable and speculative subsets. Panel B plots mean actionable and speculative shares among AI-talking firm-years, together with the share of ever-speaker firm-years that contain any AI disclosure.",
            "",
        ]
    )


def _dataset_summary(
    args: argparse.Namespace, summary: dict[str, object], yearly: pd.DataFrame
) -> dict[str, object]:
    return {
        "test_id": TEST_ID,
        "run_id": args.run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "inputs": {"annual_panel": str(args.annual_panel)},
        "summary": summary,
        "yearly": yearly.to_dict(orient="records"),
    }


def _copy_exports(run_dir: Path, paper_root: Path, run_id: str) -> dict[str, str]:
    exports = {
        "figure_png": paper_root / "figures" / f"{TEST_ID}_{run_id}.png",
        "figure_pdf": paper_root / "figures" / f"{TEST_ID}_{run_id}.pdf",
        "figure_docx": paper_root / "docx" / f"{TEST_ID}_{run_id}.docx",
        "figure_series": paper_root / "tables" / f"{TEST_ID}_{run_id}_series.csv",
        "writer_packet": paper_root / "writer_packets" / f"{TEST_ID}_{run_id}.md",
        "result_notes": paper_root / "snippets" / f"{TEST_ID}_{run_id}_result_notes.md",
    }
    for path in exports.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    for src_name, dst in {
        "figure_main.png": exports["figure_png"],
        "figure_main.pdf": exports["figure_pdf"],
        "figure_main.docx": exports["figure_docx"],
        "figure_series.csv": exports["figure_series"],
        "writer_packet.md": exports["writer_packet"],
        "result_notes.md": exports["result_notes"],
    }.items():
        shutil.copy2(run_dir / src_name, dst)
    return {key: str(path) for key, path in exports.items()}


def main() -> None:
    args = _parse_args()
    run_dir = args.test_root / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    yearly, summary = _load_yearly(args.annual_panel)
    yearly.to_csv(run_dir / "figure_series.csv", index=False)
    png_path, pdf_path = _plot(yearly, run_dir / "figure_main")
    note = (
        "This figure uses the expanded 2016-2025 ever-speaker annual panel. Panel A plots mean AI sentence counts per firm-year, "
        "separating total AI sentences from the actionable and speculative subsets. Panel B plots mean actionable and speculative "
        "shares among AI-talking firm-years, together with the share of ever-speaker firm-years that contain any AI disclosure."
    )
    _save_figure_docx(
        "Figure R1. AI Disclosure Volume and Composition Over Time",
        note,
        png_path,
        run_dir / "figure_main.docx",
    )
    (run_dir / "result_notes.md").write_text(_result_notes(yearly, summary), encoding="utf-8")
    (run_dir / "writer_packet.md").write_text(_writer_packet(args, summary), encoding="utf-8")
    dataset_summary = _dataset_summary(args, summary, yearly)
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
            "figure_series": str(run_dir / "figure_series.csv"),
            "figure_png": str(png_path),
            "figure_pdf": str(pdf_path),
            "figure_docx": str(run_dir / "figure_main.docx"),
            "writer_packet": str(run_dir / "writer_packet.md"),
            "result_notes": str(run_dir / "result_notes.md"),
            "dataset_summary": str(run_dir / "dataset_summary.json"),
        },
        "paper_exports": paper_exports,
    }
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[{TEST_ID}] wrote run bundle to {run_dir}")
    print(f"[{TEST_ID}] paper figure: {paper_exports['figure_docx']}")


if __name__ == "__main__":
    main()
