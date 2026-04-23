"""Publication run driver for legacy Table R5: speculative-only disclosure and AI patent timing."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, date, datetime
from pathlib import Path

from semantic_ai_washing.analysis.delivery_table_payloads import (
    summarize_table_4b_speculative_patent_timing,
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
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/test_runs/legacy_r5_speculative_patent_timing"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_hybrid_api_a_conf49_main_v1"
TEST_ID = "legacy_r5_speculative_patent_timing"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.legacy_r5_speculative_patent_timing"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annual-panel", type=Path, default=DEFAULT_ANNUAL_PANEL)
    parser.add_argument("--test-root", type=Path, default=DEFAULT_TEST_ROOT)
    parser.add_argument("--paper-root", type=Path, default=DEFAULT_PAPER_ROOT)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    return parser.parse_args()


def _prepare_payload(panel_path: Path) -> dict[str, object]:
    payload = summarize_table_4b_speculative_patent_timing(panel_path)
    payload["title"] = "Table R5. Speculative-Only Disclosure and AI Patent Timing"
    payload["note"] = str(payload["note"]).replace(
        "regression-ready ever-speaker annual panel",
        "expanded 2016-2025 ever-speaker annual panel",
    )
    return payload


def _result_notes(payload: dict[str, object]) -> str:
    body_rows = payload["body_rows"]  # type: ignore[assignment]
    first_spec = payload["models"][0]["label"]  # type: ignore[index]
    lookup = {row["label"]: row["cells"][0] for row in body_rows if row.get("kind") == "coef"}
    return "\n".join(
        [
            "# Result Notes",
            "",
            f"- Under `{first_spec}`, the coefficient on AI patents at `t-2` is `{lookup['log(1 + AI patents) at t-2']}`.",
            f"- Under `{first_spec}`, the coefficient on AI patents at `t` is `{lookup['log(1 + AI patents) at t']}`.",
            f"- Under `{first_spec}`, the coefficient on AI patents at `t+1` is `{lookup['log(1 + AI patents) at t+1']}`.",
            f"- Under `{first_spec}`, the coefficient on AI patents at `t+2` is `{lookup['log(1 + AI patents) at t+2']}`.",
            "",
        ]
    )


def _writer_packet(args: argparse.Namespace, payload: dict[str, object]) -> str:
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
            "## Caption Draft",
            "This table reports distributed-lag style regressions of speculative-only disclosure on AI patent timing in the expanded 2016-2025 ever-speaker panel. Each column varies the fixed-effects structure or sample trim, while the rows trace patent timing from t-2 through t+2. Standard errors are clustered at the firm level.",
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
