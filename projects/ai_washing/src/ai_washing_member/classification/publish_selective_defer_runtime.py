"""Publish a selected selective-defer runtime manifest."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from ai_washing_member.classification.model_runtime import build_selective_defer_runtime
from ai_washing_member.classification.preliminary_pipeline import sha256_file


def run_publish(args: argparse.Namespace) -> dict[str, object]:
    winner = build_selective_defer_runtime(
        binary_metadata_path=args.binary_metadata,
        logreg_metadata_path=args.logreg_metadata,
        api_policy_path=args.api_policy,
        low_confidence_threshold=float(args.low_confidence_threshold),
        model_id=str(args.model_id or "").strip(),
    )
    output_path = Path(args.output_manifest)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "selected",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "preliminary_only": True,
        "source_window_id": str(winner.get("source_window_id", "")),
        "selection_reason": str(args.selection_reason).strip(),
        "operating_point": {
            "low_confidence_threshold": float(args.low_confidence_threshold),
            "defer_policy": "api_a_on_low_local_confidence",
            "api_policy_path": str(args.api_policy),
            "api_policy_sha256": sha256_file(args.api_policy),
        },
        "benchmark_refs": {
            "heldout_report": str(args.heldout_report),
            "heldout_confidence_sweep": str(args.heldout_confidence_sweep),
            "irr_boundary_report": str(args.irr_boundary_report),
            "irr_boundary_confidence_sweep": str(args.irr_boundary_confidence_sweep),
            "decision_note": str(args.decision_note),
        },
        "inputs": {
            "binary_metadata": str(args.binary_metadata),
            "logreg_metadata": str(args.logreg_metadata),
            "api_policy": str(args.api_policy),
            "binary_metadata_sha256": sha256_file(args.binary_metadata),
            "logreg_metadata_sha256": sha256_file(args.logreg_metadata),
            "api_policy_sha256": sha256_file(args.api_policy),
        },
        "winner": winner,
    }
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--binary-metadata",
        default="artifacts/models/binary_relevance_then_as_v1/metadata.json",
    )
    parser.add_argument(
        "--logreg-metadata",
        default="artifacts/models/mpnet_logreg_prelim_v1/metadata.json",
    )
    parser.add_argument(
        "--api-policy",
        default="director/config/api_assistive_policy_heldout_v3_mini_high_output.yaml",
    )
    parser.add_argument("--low-confidence-threshold", type=float, required=True)
    parser.add_argument("--model-id", default="")
    parser.add_argument("--selection-reason", required=True)
    parser.add_argument("--output-manifest", required=True)
    parser.add_argument(
        "--heldout-report",
        default="reports/evaluation/selective_defer_heldout_v3_v1.json",
    )
    parser.add_argument(
        "--heldout-confidence-sweep",
        default="reports/evaluation/selective_defer_heldout_v3_confidence_sweep_v1.csv",
    )
    parser.add_argument(
        "--irr-boundary-report",
        default="reports/evaluation/selective_defer_irr_boundary_v1.json",
    )
    parser.add_argument(
        "--irr-boundary-confidence-sweep",
        default="reports/evaluation/selective_defer_irr_boundary_confidence_sweep_v1.csv",
    )
    parser.add_argument(
        "--decision-note",
        default="projects/ai_washing/docs/track_a_selective_defer_results_v1.md",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_publish(args)
    print(
        "[selective-defer-publish] manifest published "
        f"model_id={report['winner']['model_id']} "
        f"threshold={report['operating_point']['low_confidence_threshold']:.2f}"
    )
    print(f"[selective-defer-publish] manifest -> {args.output_manifest}")


if __name__ == "__main__":
    main()
