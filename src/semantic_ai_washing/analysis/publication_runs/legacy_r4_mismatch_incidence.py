"""Publication run driver for legacy Figure R4: mismatch incidence over time and by industry."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

from semantic_ai_washing.analysis.build_delivery_figures import _save_figure_docx, build_figure_4

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_ANNUAL_PANEL = (
    REPO_ROOT
    / "data/processed/panel/canonical/ever_speaker_panel_2016_2025_hybrid_api_a_conf49_v1.parquet"
)
DEFAULT_TEST_ROOT = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/test_runs/legacy_r4_mismatch_incidence"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_hybrid_api_a_conf49_main_v1"
TEST_ID = "legacy_r4_mismatch_incidence"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.legacy_r4_mismatch_incidence"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annual-panel", type=Path, default=DEFAULT_ANNUAL_PANEL)
    parser.add_argument("--test-root", type=Path, default=DEFAULT_TEST_ROOT)
    parser.add_argument("--paper-root", type=Path, default=DEFAULT_PAPER_ROOT)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    return parser.parse_args()


def _copy_exports(run_dir: Path, paper_root: Path, run_id: str) -> dict[str, str]:
    exports = {
        "figure_png": paper_root / "figures" / f"{TEST_ID}_{run_id}.png",
        "figure_docx": paper_root / "docx" / f"{TEST_ID}_{run_id}.docx",
        "writer_packet": paper_root / "writer_packets" / f"{TEST_ID}_{run_id}.md",
        "result_notes": paper_root / "snippets" / f"{TEST_ID}_{run_id}_result_notes.md",
    }
    for path in exports.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(run_dir / "figure_main.png", exports["figure_png"])
    shutil.copy2(run_dir / "figure_main.docx", exports["figure_docx"])
    shutil.copy2(run_dir / "writer_packet.md", exports["writer_packet"])
    shutil.copy2(run_dir / "result_notes.md", exports["result_notes"])
    return {key: str(path) for key, path in exports.items()}


def main() -> None:
    args = _parse_args()
    run_dir = args.test_root / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    image_path, docx_path = build_figure_4(args.annual_panel, run_dir, run_dir)
    normalized_png = run_dir / "figure_main.png"
    shutil.copy2(image_path, normalized_png)
    normalized_docx = run_dir / "figure_main.docx"
    _save_figure_docx(
        "Figure R4. PatentMismatch Incidence Over Time and by Industry",
        "This figure uses the expanded 2016-2025 ever-speaker annual panel and restricts the plotted observations to AI-talking firm-years because PatentMismatch is defined only when AI disclosure is present. Panel A plots annual PatentMismatch incidence together with the share of AI-talking firm-years flagged as mismatch. Panel B shows the industries with the highest concentration of mismatch incidents.",
        normalized_png,
        normalized_docx,
    )
    (run_dir / "result_notes.md").write_text(
        "# Result Notes\n\n- This figure restricts the denominator to AI-talking firm-years because PatentMismatch is defined only when AI disclosure is present.\n- Panel A shows the annual count and share of mismatch incidents; Panel B shows the industries with the highest concentration of mismatch incidents.\n",
        encoding="utf-8",
    )
    (run_dir / "writer_packet.md").write_text(
        "\n".join(
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
                "## Caption Draft",
                "This figure uses the expanded 2016-2025 ever-speaker annual panel and restricts the plotted observations to AI-talking firm-years. Panel A shows annual PatentMismatch incidence and the share of AI-talking firm-years flagged as mismatch. Panel B shows the industry groups with the highest concentration of mismatch incidents.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    dataset_summary = {
        "test_id": TEST_ID,
        "run_id": args.run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "inputs": {"annual_panel": str(args.annual_panel)},
        "outputs": {
            "figure_png": str(normalized_png),
            "figure_docx": str(normalized_docx),
            "source_legacy_png": str(image_path),
            "source_legacy_docx": str(docx_path),
        },
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
            "figure_png": str(normalized_png),
            "figure_docx": str(normalized_docx),
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
