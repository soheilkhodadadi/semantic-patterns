"""Benchmark preliminary classifier candidates and publish a selected-model manifest."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import pandas as pd

from semantic_ai_washing.classification.benchmark_utils import (
    build_validation_benchmark,
    compute_metrics,
    heldout_overlap_count,
    load_benchmark_frame,
)
from semantic_ai_washing.classification.model_runtime import (
    build_centroid_runtime,
    build_legacy_two_stage_runtime,
    build_pickle_runtime,
    predict_sentences,
)
from semantic_ai_washing.classification.preliminary_pipeline import sha256_file
from ai_washing_member.labeling.common import row_sha256

PRIMARY_BENCHMARK_NAME = "held_out_v2"
SECONDARY_MAJOR_REGRESSION_TOLERANCE = 0.10


def _resolve(path: str | Path) -> Path:
    return Path(path).resolve()


def _frame_digest(frame: pd.DataFrame) -> str:
    rows = frame.fillna("").astype(str).agg("|".join, axis=1).tolist()
    return row_sha256(rows)


def _benchmark_spec(name: str, path: str | Path) -> dict[str, Any]:
    return {"name": name, "path": str(path), "exists": Path(path).exists()}


def _load_benchmark_assets(
    args: argparse.Namespace,
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    assets: dict[str, dict[str, Any]] = {}
    missing: list[str] = []

    file_assets = {
        PRIMARY_BENCHMARK_NAME: _benchmark_spec(PRIMARY_BENCHMARK_NAME, args.primary_benchmark),
        "historical_held_out": _benchmark_spec("historical_held_out", args.historical_benchmark),
        "irr_boundary_benchmark": _benchmark_spec(
            "irr_boundary_benchmark", args.irr_boundary_benchmark
        ),
    }
    for name, spec in file_assets.items():
        if spec["exists"]:
            frame = load_benchmark_frame(spec["path"])
            leakage = (
                heldout_overlap_count(args.labels_master, frame)
                if name == PRIMARY_BENCHMARK_NAME
                else 0
            )
            assets[name] = {
                "name": name,
                "role": "primary" if name == PRIMARY_BENCHMARK_NAME else "secondary",
                "frame": frame,
                "path": spec["path"],
                "sha256": sha256_file(spec["path"]),
                "row_count": int(len(frame)),
                "leakage_count": int(leakage),
            }
        else:
            missing.append(name)

    validation_frame = build_validation_benchmark(args.labels_master, args.split_registry)
    assets["frozen_validation_split"] = {
        "name": "frozen_validation_split",
        "role": "secondary",
        "frame": validation_frame,
        "path": "<derived>",
        "sha256": _frame_digest(validation_frame[["sentence", "label"]].copy()),
        "row_count": int(len(validation_frame)),
        "leakage_count": 0,
    }
    return assets, missing


def _evaluate_candidate(candidate: dict[str, Any], benchmark: dict[str, Any]) -> dict[str, Any]:
    frame = benchmark["frame"]
    start = time.perf_counter()
    predicted, _score_rows = predict_sentences(
        frame["sentence"].fillna("").astype(str).tolist(), candidate
    )
    runtime_seconds = round(time.perf_counter() - start, 6)
    metrics = compute_metrics(frame["label"].astype(str).tolist(), predicted)
    metrics.update(
        {
            "runtime_seconds": runtime_seconds,
            "benchmark_name": benchmark["name"],
            "benchmark_role": benchmark["role"],
            "benchmark_rows": int(benchmark["row_count"]),
            "benchmark_sha256": benchmark["sha256"],
            "leakage_detected": bool(benchmark["leakage_count"] > 0),
            "leakage_count": int(benchmark["leakage_count"]),
        }
    )
    return metrics


def _major_regression_threshold(scores: dict[str, dict[str, Any]], benchmark_name: str) -> float:
    available = [
        payload[benchmark_name]["macro_f1"]
        for payload in scores.values()
        if benchmark_name in payload
    ]
    if not available:
        return -1.0
    return max(available) - SECONDARY_MAJOR_REGRESSION_TOLERANCE


def _candidate_passes_primary(primary: dict[str, Any], thresholds: dict[str, float]) -> bool:
    return (
        not primary["leakage_detected"]
        and primary["accuracy"] >= thresholds["accuracy"]
        and primary["macro_f1"] >= thresholds["macro_f1"]
        and primary["actionable_speculative_conditional_accuracy"] >= thresholds["as_accuracy"]
    )


def _select_winner(
    candidates: list[dict[str, Any]],
    scores: dict[str, dict[str, Any]],
    *,
    primary_available: bool,
    thresholds: dict[str, float],
) -> tuple[str, dict[str, Any] | None, str]:
    if not primary_available:
        return (
            "pending_primary_benchmark",
            None,
            "Primary benchmark held_out_v2 is not frozen yet.",
        )

    historical_floor = _major_regression_threshold(scores, "historical_held_out")
    irr_floor = _major_regression_threshold(scores, "irr_boundary_benchmark")
    eligible: list[tuple[tuple[Any, ...], dict[str, Any], dict[str, Any]]] = []
    for candidate in candidates:
        candidate_id = candidate["model_id"]
        primary = scores[candidate_id].get(PRIMARY_BENCHMARK_NAME)
        if primary is None or not _candidate_passes_primary(primary, thresholds):
            continue
        historical = scores[candidate_id].get("historical_held_out")
        irr = scores[candidate_id].get("irr_boundary_benchmark")
        if historical is not None and historical["macro_f1"] < historical_floor:
            continue
        if irr is not None and irr["macro_f1"] < irr_floor:
            continue
        rank_key = (
            -primary["macro_f1"],
            -primary["accuracy"],
            -primary["actionable_speculative_conditional_accuracy"],
            candidate_id,
        )
        eligible.append((rank_key, candidate, primary))

    if not eligible:
        return "no_winner", None, "No wave-1 candidate cleared the preliminary benchmark gate."

    eligible.sort(key=lambda item: item[0])
    _rank_key, winner, winner_primary = eligible[0]
    reason = (
        "Selected by primary benchmark macro_f1, then accuracy, then A/S conditional accuracy, "
        "with no major regression on secondary benchmarks."
    )
    winner_payload = {
        "model_id": winner["model_id"],
        "model_type": winner["model_type"],
        "source_window_id": winner.get("source_window_id", "active_2021_2024"),
        "preliminary_only": True,
        "runtime": winner["runtime"],
        "primary_benchmark": PRIMARY_BENCHMARK_NAME,
        "primary_metrics": {
            "accuracy": winner_primary["accuracy"],
            "macro_f1": winner_primary["macro_f1"],
            "actionable_speculative_conditional_accuracy": winner_primary[
                "actionable_speculative_conditional_accuracy"
            ],
            "actionable_speculative_conditional_macro_f1": winner_primary[
                "actionable_speculative_conditional_macro_f1"
            ],
        },
    }
    return "selected", winner_payload, reason


def _markdown_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Preliminary Model Benchmark Matrix",
        "",
        f"- Status: `{payload['status']}`",
        f"- Primary benchmark available: `{payload['summary']['primary_benchmark_available']}`",
        f"- Selected model: `{payload['summary']['selected_model_id'] or 'none'}`",
        "",
        "| Model | Benchmark | Accuracy | Macro F1 | Binary Relevance Acc | A/S Conditional Acc | Leakage |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for model in payload["models"]:
        for benchmark_name, score in model["benchmarks"].items():
            lines.append(
                "| {model_id} | {benchmark} | {acc:.4f} | {macro:.4f} | {bin_acc:.4f} | {as_acc:.4f} | {leak} |".format(
                    model_id=model["model_id"],
                    benchmark=benchmark_name,
                    acc=score["accuracy"],
                    macro=score["macro_f1"],
                    bin_acc=score["binary_relevance_accuracy"],
                    as_acc=score["actionable_speculative_conditional_accuracy"],
                    leak=str(score["leakage_detected"]).lower(),
                )
            )
    return "\n".join(lines) + "\n"


def run_benchmark(args: argparse.Namespace) -> dict[str, Any]:
    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    selected_manifest_path = Path(args.selected_manifest)
    model_report_dir = Path(args.model_report_dir)
    for path in [output_json, output_md, selected_manifest_path]:
        path.parent.mkdir(parents=True, exist_ok=True)
    model_report_dir.mkdir(parents=True, exist_ok=True)

    assets, missing = _load_benchmark_assets(args)
    candidates = []
    if not bool(getattr(args, "skip_legacy", False)):
        candidates.append(
            build_legacy_two_stage_runtime(
                tau=float(args.legacy_tau),
                eps_irr=float(args.legacy_eps_irr),
                min_tokens=int(args.legacy_min_tokens),
                rule_boosts=bool(args.legacy_rule_boosts),
            )
        )
    candidates.extend(
        [
            build_centroid_runtime(
                metadata_path=args.centroid_metadata, centroids_path=args.centroid_model
            ),
            build_pickle_runtime(metadata_path=args.logreg_metadata),
            build_pickle_runtime(metadata_path=args.binary_metadata),
        ]
    )

    scores: dict[str, dict[str, Any]] = {}
    models_payload: list[dict[str, Any]] = []
    for candidate in candidates:
        candidate_id = candidate["model_id"]
        candidate_scores: dict[str, Any] = {}
        for benchmark_name, benchmark in assets.items():
            score = _evaluate_candidate(candidate, benchmark)
            candidate_scores[benchmark_name] = score
        scores[candidate_id] = candidate_scores
        model_payload = {
            "model_id": candidate_id,
            "model_type": candidate["model_type"],
            "benchmarks": candidate_scores,
        }
        models_payload.append(model_payload)
        (model_report_dir / f"{candidate_id}.json").write_text(
            json.dumps(model_payload, indent=2), encoding="utf-8"
        )

    thresholds = {
        "accuracy": float(args.min_primary_accuracy),
        "macro_f1": float(args.min_primary_macro_f1),
        "as_accuracy": float(args.min_primary_as_accuracy),
    }
    selection_status, winner_payload, selection_reason = _select_winner(
        candidates,
        scores,
        primary_available=PRIMARY_BENCHMARK_NAME in assets,
        thresholds=thresholds,
    )

    payload = {
        "status": selection_status,
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "summary": {
            "status": selection_status,
            "primary_benchmark_name": PRIMARY_BENCHMARK_NAME,
            "primary_benchmark_available": PRIMARY_BENCHMARK_NAME in assets,
            "missing_benchmarks": missing,
            "skipped_candidates": ["legacy_two_stage_mpnet_rules"]
            if bool(getattr(args, "skip_legacy", False))
            else [],
            "selected_model_id": winner_payload["model_id"] if winner_payload else "",
            "selection_reason": selection_reason,
            "minimum_gate": thresholds,
        },
        "benchmarks": {
            name: {
                "path": spec["path"],
                "row_count": int(spec["row_count"]),
                "sha256": spec["sha256"],
                "role": spec["role"],
            }
            for name, spec in assets.items()
        },
        "models": models_payload,
    }
    output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    output_md.write_text(_markdown_report(payload), encoding="utf-8")

    selected_manifest = {
        "status": selection_status,
        "generated_at_utc": payload["generated_at_utc"],
        "preliminary_only": True,
        "source_window_id": "active_2021_2024",
        "selection_reason": selection_reason,
        "benchmark_matrix": str(output_json),
        "benchmark_matrix_sha256": sha256_file(output_json),
        "winner": winner_payload,
    }
    selected_manifest_path.write_text(json.dumps(selected_manifest, indent=2), encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels-master", default="data/labels/v1/labels_master.parquet")
    parser.add_argument("--split-registry", default="data/metadata/splits/split_registry_v1.csv")
    parser.add_argument("--primary-benchmark", default="data/validation/held_out_sentences_v2.csv")
    parser.add_argument("--historical-benchmark", default="data/validation/held_out_sentences.csv")
    parser.add_argument(
        "--irr-boundary-benchmark", default="data/validation/irr_boundary_benchmark_v1.csv"
    )
    parser.add_argument(
        "--centroid-model", default="artifacts/models/mpnet_prelim_v1/centroids.json"
    )
    parser.add_argument(
        "--centroid-metadata", default="artifacts/models/mpnet_prelim_v1/metadata.json"
    )
    parser.add_argument(
        "--logreg-metadata", default="artifacts/models/mpnet_logreg_prelim_v1/metadata.json"
    )
    parser.add_argument(
        "--binary-metadata",
        default="artifacts/models/binary_relevance_then_as_v1/metadata.json",
    )
    parser.add_argument(
        "--output-json", default="reports/evaluation/model_benchmark_matrix_prelim_v1.json"
    )
    parser.add_argument(
        "--output-md", default="reports/evaluation/model_benchmark_matrix_prelim_v1.md"
    )
    parser.add_argument("--model-report-dir", default="reports/evaluation/models")
    parser.add_argument(
        "--selected-manifest", default="artifacts/models/prelim_selected_model_v1.json"
    )
    parser.add_argument("--min-primary-accuracy", type=float, default=0.70)
    parser.add_argument("--min-primary-macro-f1", type=float, default=0.65)
    parser.add_argument("--min-primary-as-accuracy", type=float, default=0.65)
    parser.add_argument("--legacy-tau", type=float, default=0.07)
    parser.add_argument("--legacy-eps-irr", type=float, default=0.03)
    parser.add_argument("--legacy-min-tokens", type=int, default=6)
    parser.add_argument("--legacy-rule-boosts", action="store_true", default=True)
    parser.add_argument("--no-legacy-rule-boosts", dest="legacy_rule_boosts", action="store_false")
    parser.add_argument(
        "--skip-legacy",
        action="store_true",
        help="Skip the legacy two-stage baseline when benchmarking modern preliminary models.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_benchmark(args)
    print(
        "[prelim-benchmark] status="
        f"{report['status']} selected={report['summary']['selected_model_id'] or 'none'}"
    )
    print(f"[prelim-benchmark] matrix -> {args.output_json}")


if __name__ == "__main__":
    main()
