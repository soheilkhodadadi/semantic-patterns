"""Publication run driver for legacy Table A1: full determinants of PatentMismatch."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, date, datetime
from pathlib import Path

from semantic_ai_washing.analysis.delivery_table_payloads import (
    summarize_table_7_mismatch_determinants,
)
from semantic_ai_washing.analysis.publication_runs.legacy_timing_table_utils import (
    build_payload_docx,
    copy_table_exports,
    flatten_payload_to_csv,
    write_payload_json,
    write_payload_markdown,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_ANNUAL_PANEL = (
    REPO_ROOT
    / "data/processed/panel/canonical/ever_speaker_panel_2016_2025_hybrid_api_a_conf49_v1.parquet"
)
DEFAULT_TEST_ROOT = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/test_runs/legacy_a1_mismatch_determinants_full"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_hybrid_api_a_conf49_main_v1"
TEST_ID = "legacy_a1_mismatch_determinants_full"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.legacy_a1_mismatch_determinants_full"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annual-panel", type=Path, default=DEFAULT_ANNUAL_PANEL)
    parser.add_argument("--test-root", type=Path, default=DEFAULT_TEST_ROOT)
    parser.add_argument("--paper-root", type=Path, default=DEFAULT_PAPER_ROOT)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    return parser.parse_args()


def _prepare_payload(panel_path: Path) -> dict[str, object]:
    payload = summarize_table_7_mismatch_determinants(panel_path)
    payload["title"] = "Table A1. Full-Baseline Determinants of PatentMismatch"
    payload["dependent_label"] = "Dependent variable: any PatentMismatch incident, 2016-2025"
    payload["note"] = str(payload["note"]).replace("2016-2024", "2016-2025")
    return payload


def _result_notes(payload: dict[str, object]) -> str:
    models = payload["models"]  # type: ignore[assignment]
    body_rows = payload["body_rows"]  # type: ignore[assignment]
    multivar_idx = len(models) - 1
    lookup = {row["label"]: row["cells"][multivar_idx] for row in body_rows if row.get("kind") == "coef"}
    footer = {row["label"]: row["cells"] for row in payload["footer_rows"]}  # type: ignore[assignment]
    return "\n".join(
        [
            "# Result Notes",
            "",
            f"- In the full multivariate column, `Log assets` is `{lookup['Log assets']}` and `ROA` is `{lookup['ROA']}`.",
            f"- In the full multivariate column, `R&D/assets` is `{lookup['R&D/assets']}` and `Leverage` is `{lookup['Leverage']}`.",
            f"- The full-baseline multivariate sample falls to `{footer['Observations'][multivar_idx]}` firms because R&D/assets and employees are not broadly observed.",
            "",
        ]
    )


def _writer_packet(args: argparse.Namespace, payload: dict[str, object]) -> str:
    models = payload["models"]  # type: ignore[assignment]
    body_rows = payload["body_rows"]  # type: ignore[assignment]
    footer_rows = payload["footer_rows"]  # type: ignore[assignment]
    multivar_idx = len(models) - 1
    lookup = {row["label"]: row["cells"][multivar_idx] for row in body_rows if row.get("kind") == "coef"}
    footer = {row["label"]: row["cells"] for row in footer_rows}
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
            "- Unit of observation: `firm`",
            "- Sample filters: `baseline firm characteristics measured in 2016; mismatch outcome aggregated over expanded 2016-2025 panel`",
            "- Date range: `baseline covariates in 2016, outcome window 2016-2025`",
            f"- N range: `{footer['Observations'][0]}` to `{footer['Observations'][-1]}`",
            "",
            "## Variable Block",
            "- Dependent variable: `indicator for whether a firm records at least one PatentMismatch incident during 2016-2025`",
            "- Key regressors: `log assets, cash/assets, leverage, R&D/assets, CAPX/assets, ROA, employees (k)`",
            "- Baseline year: `2016`",
            "",
            "## Estimation Block",
            "- Fixed effects: `baseline SIC2 industry FE`",
            "- Clustering: `industry level`",
            "- Weighting: `unweighted cross-sectional OLS`",
            "",
            "## Result Block",
            f"- Multivariate `Log assets`: `{lookup['Log assets']}`",
            f"- Multivariate `ROA`: `{lookup['ROA']}`",
            f"- Multivariate `R&D/assets`: `{lookup['R&D/assets']}`",
            f"- Multivariate `Leverage`: `{lookup['Leverage']}`",
            f"- Multivariate N: `{footer['Observations'][-1]}`",
            "- One-sentence interpretation: `full-baseline determinants are directionally similar to the reduced table but become much noisier once the sample is forced onto the smaller complete-case subset`",
            "- Candidate use: `appendix only`",
            "",
            "## Caption Draft",
            "This appendix table reports full-baseline cross-sectional regressions for whether a firm records at least one PatentMismatch incident on the expanded 2016-2025 panel. Baseline covariates are measured in 2016 and include log assets, cash/assets, leverage, R&D/assets, CAPX/assets, ROA, and employees. All specifications include baseline industry fixed effects, and standard errors are clustered at the industry level.",
            "",
        ]
    )


def main() -> None:
    args = _parse_args()
    run_dir = args.test_root / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    payload = _prepare_payload(args.annual_panel)
    write_payload_json(payload, run_dir / "table_payload.json")
    flatten_payload_to_csv(payload, kind="row_matrix", output_path=run_dir / "table_main.csv")
    write_payload_markdown(payload, kind="row_matrix", output_path=run_dir / "table_main.md")
    build_payload_docx(payload, kind="row_matrix", output_path=run_dir / "table_main.docx")
    (run_dir / "result_notes.md").write_text(_result_notes(payload), encoding="utf-8")
    (run_dir / "writer_packet.md").write_text(_writer_packet(args, payload), encoding="utf-8")
    dataset_summary = {
        "test_id": TEST_ID,
        "run_id": args.run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "inputs": {"annual_panel": str(args.annual_panel)},
        "payload": payload,
    }
    (run_dir / "dataset_summary.json").write_text(
        json.dumps(dataset_summary, indent=2), encoding="utf-8"
    )
    paper_exports = copy_table_exports(
        run_dir, args.paper_root, test_id=TEST_ID, run_id=args.run_id
    )
    manifest = {
        "test_id": TEST_ID,
        "run_id": args.run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "module_path": MODULE_PATH,
        "run_dir": str(run_dir),
        "outputs": {
            "table_payload": str(run_dir / "table_payload.json"),
            "table_csv": str(run_dir / "table_main.csv"),
            "table_md": str(run_dir / "table_main.md"),
            "table_docx": str(run_dir / "table_main.docx"),
            "writer_packet": str(run_dir / "writer_packet.md"),
            "result_notes": str(run_dir / "result_notes.md"),
            "dataset_summary": str(run_dir / "dataset_summary.json"),
        },
        "paper_exports": paper_exports,
    }
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[{TEST_ID}] wrote run bundle to {run_dir}")
    print(f"[{TEST_ID}] paper table: {paper_exports['table_docx']}")


if __name__ == "__main__":
    main()
