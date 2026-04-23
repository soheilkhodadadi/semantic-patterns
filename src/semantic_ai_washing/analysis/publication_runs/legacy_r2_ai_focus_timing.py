"""Publication run driver for legacy Table R2: AI Focus and AI patent timing."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, date, datetime
from pathlib import Path

from semantic_ai_washing.analysis.delivery_table_payloads import summarize_table_2_timing_focus
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
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/test_runs/legacy_r2_ai_focus_timing"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_hybrid_api_a_conf49_main_v1"
TEST_ID = "legacy_r2_ai_focus_timing"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.legacy_r2_ai_focus_timing"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annual-panel", type=Path, default=DEFAULT_ANNUAL_PANEL)
    parser.add_argument("--test-root", type=Path, default=DEFAULT_TEST_ROOT)
    parser.add_argument("--paper-root", type=Path, default=DEFAULT_PAPER_ROOT)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    return parser.parse_args()


def _prepare_payload(panel_path: Path) -> dict[str, object]:
    payload = summarize_table_2_timing_focus(panel_path)
    payload["title"] = "Table R2. AI Focus and AI Patent Timing"
    payload["note"] = str(payload["note"]).replace(
        "regression-ready ever-speaker annual panel",
        "expanded 2016-2025 ever-speaker annual panel",
    )
    return payload


def _result_notes(payload: dict[str, object]) -> str:
    panel = payload["panels"][0]  # type: ignore[index]
    models = payload["models"]  # type: ignore[assignment]
    coef_map = {
        model["label"]: coef for model, coef in zip(models, panel["coef_cells"], strict=True)
    }
    footer_lookup = {
        row["label"]: row["cells"]
        for row in panel["footer_rows"]  # type: ignore[index]
    }
    return "\n".join(
        [
            "# Result Notes",
            "",
            f"- AI_Focus coefficient at `t-2`: `{coef_map['t-2']}`.",
            f"- AI_Focus coefficient at `t`: `{coef_map['t']}`.",
            f"- AI_Focus coefficient at `t+1`: `{coef_map['t+1']}`.",
            f"- AI_Focus coefficient at `t+2`: `{coef_map['t+2']}`.",
            f"- Observation counts range from `{footer_lookup['Observations'][0]}` to `{footer_lookup['Observations'][-1]}` across horizons.",
            "",
        ]
    )


def _writer_packet(args: argparse.Namespace, payload: dict[str, object]) -> str:
    panel = payload["panels"][0]  # type: ignore[index]
    models = payload["models"]  # type: ignore[assignment]
    coef_map = {
        model["label"]: coef for model, coef in zip(models, panel["coef_cells"], strict=True)
    }
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
            "## Main coefficients",
            f"- `AI_Focus` at `t-2`: `{coef_map['t-2']}`",
            f"- `AI_Focus` at `t-1`: `{coef_map['t-1']}`",
            f"- `AI_Focus` at `t`: `{coef_map['t']}`",
            f"- `AI_Focus` at `t+1`: `{coef_map['t+1']}`",
            f"- `AI_Focus` at `t+2`: `{coef_map['t+2']}`",
            "",
            "## Caption Draft",
            "This table reports firm-year panel regressions of AI patent timing on AI disclosure intensity in the expanded 2016-2025 ever-speaker panel. The focal regressor is AI Focus, defined as log(1 + AI sentences). Columns vary the patent horizon from t-2 through t+2 and absorb firm and year fixed effects with firm-clustered standard errors.",
            "",
        ]
    )


def main() -> None:
    args = _parse_args()
    run_dir = args.test_root / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    payload = _prepare_payload(args.annual_panel)
    write_payload_json(payload, run_dir / "table_payload.json")
    flatten_payload_to_csv(payload, kind="panel_timing", output_path=run_dir / "table_main.csv")
    write_payload_markdown(payload, kind="panel_timing", output_path=run_dir / "table_main.md")
    build_payload_docx(payload, kind="panel_timing", output_path=run_dir / "table_main.docx")
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
