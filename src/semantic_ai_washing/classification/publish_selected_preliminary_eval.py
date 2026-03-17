"""Publish the selected preliminary model's primary held-out evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from semantic_ai_washing.classification.model_runtime import load_manifest
from semantic_ai_washing.classification.preliminary_pipeline import sha256_file


def run_publish(args: argparse.Namespace) -> dict:
    selected = load_manifest(args.selected_manifest)
    matrix = json.loads(Path(args.benchmark_matrix).read_text(encoding="utf-8"))
    output_path = Path(args.output_report)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    status = str(selected.get("status", "")).strip()
    winner = selected.get("winner") or {}
    selected_model_id = str(winner.get("model_id", "")).strip()
    primary_name = str(matrix.get("summary", {}).get("primary_benchmark_name", "held_out_v2"))

    if status != "selected" or not selected_model_id:
        payload = {
            "status": "pending_selected_model",
            "generated_at_utc": matrix.get("generated_at_utc", ""),
            "summary": {
                "status": "pending_selected_model",
                "selected_model_id": "",
                "primary_benchmark_name": primary_name,
            },
            "inputs": {
                "selected_manifest": args.selected_manifest,
                "selected_manifest_sha256": sha256_file(args.selected_manifest),
                "benchmark_matrix": args.benchmark_matrix,
                "benchmark_matrix_sha256": sha256_file(args.benchmark_matrix),
            },
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    model_rows = {row["model_id"]: row for row in matrix.get("models", [])}
    if (
        selected_model_id not in model_rows
        or primary_name not in model_rows[selected_model_id]["benchmarks"]
    ):
        raise ValueError(
            "Selected model primary benchmark metrics are missing from the benchmark matrix."
        )
    benchmark = model_rows[selected_model_id]["benchmarks"][primary_name]
    payload = {
        "status": "passed",
        "generated_at_utc": matrix.get("generated_at_utc", ""),
        "model_id": selected_model_id,
        "summary": {
            "status": "passed",
            "preliminary_only": True,
            "source_window_id": selected.get("source_window_id", "active_2021_2024"),
            "reviewed_items": benchmark["benchmark_rows"],
            "accuracy": benchmark["accuracy"],
            "macro_f1": benchmark["macro_f1"],
            "leakage_detected": benchmark["leakage_detected"],
            "heldout_overlap_count": benchmark["leakage_count"],
            "publication_grade_threshold": float(args.accuracy_threshold),
            "publication_grade_threshold_passed": benchmark["accuracy"]
            >= float(args.accuracy_threshold),
            "valid_evaluation_state": not benchmark["leakage_detected"],
            "benchmark_name": primary_name,
            "binary_relevance_accuracy": benchmark["binary_relevance_accuracy"],
            "actionable_speculative_conditional_accuracy": benchmark[
                "actionable_speculative_conditional_accuracy"
            ],
        },
        "inputs": {
            "selected_manifest": args.selected_manifest,
            "selected_manifest_sha256": sha256_file(args.selected_manifest),
            "benchmark_matrix": args.benchmark_matrix,
            "benchmark_matrix_sha256": sha256_file(args.benchmark_matrix),
        },
        "confusion_matrix": benchmark["confusion_matrix"],
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--selected-manifest", default="artifacts/models/prelim_selected_model_v1.json"
    )
    parser.add_argument(
        "--benchmark-matrix", default="reports/evaluation/model_benchmark_matrix_prelim_v1.json"
    )
    parser.add_argument(
        "--output-report", default="reports/evaluation/heldout_eval_prelim_v2.json"
    )
    parser.add_argument("--accuracy-threshold", type=float, default=0.80)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_publish(args)
    print(f"[prelim-selected-eval] status={payload['status']}")
    print(f"[prelim-selected-eval] report -> {args.output_report}")


if __name__ == "__main__":
    main()
