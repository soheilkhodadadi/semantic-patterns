"""Evaluate a preliminary classifier on a held-out benchmark asset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from ai_washing_member.classification.benchmark_utils import (
    compute_metrics,
    heldout_overlap_count,
    load_benchmark_frame,
)
from ai_washing_member.classification.model_runtime import load_manifest, predict_sentences
from ai_washing_member.classification.preliminary_pipeline import (
    classify_embeddings,
    embed_sentences,
    load_centroids,
    sha256_file,
)


def _load_metadata(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if str(payload.get("status", "")).strip() != "trained":
        raise ValueError("Model metadata must report `status = trained`.")
    return payload


def _pending_selected_payload(args: argparse.Namespace, status: str) -> dict[str, Any]:
    payload = {
        "status": status,
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "model_id": "",
        "summary": {
            "status": status,
            "preliminary_only": True,
            "source_window_id": str(args.source_window_id),
            "reviewed_items": 0,
            "accuracy": 0.0,
            "macro_f1": 0.0,
            "leakage_detected": False,
            "heldout_overlap_count": 0,
            "publication_grade_threshold": float(args.accuracy_threshold),
            "publication_grade_threshold_passed": False,
            "valid_evaluation_state": False,
            "benchmark_name": Path(args.held_out).name,
        },
        "inputs": {
            "held_out": str(args.held_out),
            "labels_master": str(args.labels_master),
            "selected_model_manifest": str(args.selected_model_manifest),
            "held_out_sha256": sha256_file(args.held_out),
            "labels_master_sha256": sha256_file(args.labels_master),
            "selected_model_manifest_sha256": sha256_file(args.selected_model_manifest),
        },
        "confusion_matrix": {},
    }
    return payload


def run_evaluation(args: argparse.Namespace) -> dict[str, Any]:
    output_path = Path(args.output_report)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    selected_model_manifest = getattr(args, "selected_model_manifest", "")

    held_out = load_benchmark_frame(args.held_out)
    overlap_count = heldout_overlap_count(args.labels_master, held_out)
    leakage_detected = overlap_count > 0

    metadata: dict[str, Any]
    inputs: dict[str, Any]
    if selected_model_manifest:
        selected = load_manifest(selected_model_manifest)
        selected_status = str(selected.get("status", "")).strip()
        if selected_status != "selected" or not isinstance(selected.get("winner"), dict):
            payload = _pending_selected_payload(args, "pending_selected_model")
            output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            return payload
        runtime_manifest = dict(selected["winner"])
        predicted, _score_rows = predict_sentences(
            held_out["sentence"].fillna("").astype(str).tolist(),
            runtime_manifest,
        )
        metadata = {
            "model_id": runtime_manifest.get("model_id", ""),
            "source_window_id": runtime_manifest.get("source_window_id", args.source_window_id),
            "embedding_backend": runtime_manifest.get("runtime", {}).get("embedding_backend", ""),
            "model_name": runtime_manifest.get("runtime", {}).get("model_name", ""),
        }
        inputs = {
            "held_out": str(args.held_out),
            "labels_master": str(args.labels_master),
            "selected_model_manifest": str(selected_model_manifest),
            "held_out_sha256": sha256_file(args.held_out),
            "labels_master_sha256": sha256_file(args.labels_master),
            "selected_model_manifest_sha256": sha256_file(selected_model_manifest),
        }
    else:
        metadata = _load_metadata(args.model_metadata)
        centroids = load_centroids(args.centroids)
        embeddings = embed_sentences(
            held_out["sentence"].fillna("").astype(str).tolist(),
            backend=str(metadata.get("embedding_backend", args.embedding_backend)),
            model_name=str(metadata.get("model_name", args.model_name)),
            batch_size=int(args.batch_size),
            hash_dim=int(metadata.get("hash_dim", args.hash_dim)),
        )
        predicted, _score_rows = classify_embeddings(embeddings, centroids)
        inputs = {
            "held_out": str(args.held_out),
            "labels_master": str(args.labels_master),
            "centroids": str(args.centroids),
            "model_metadata": str(args.model_metadata),
            "held_out_sha256": sha256_file(args.held_out),
            "labels_master_sha256": sha256_file(args.labels_master),
            "centroids_sha256": sha256_file(args.centroids),
            "model_metadata_sha256": sha256_file(args.model_metadata),
        }

    metrics = compute_metrics(held_out["label"].astype(str).tolist(), predicted)
    valid_state = not leakage_detected and len(held_out) > 0
    status = "passed" if valid_state else "failed"
    report = {
        "status": status,
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "model_id": metadata.get("model_id", args.model_id),
        "summary": {
            "status": status,
            "preliminary_only": True,
            "source_window_id": metadata.get("source_window_id", args.source_window_id),
            "reviewed_items": int(len(held_out)),
            "accuracy": metrics["accuracy"],
            "macro_f1": metrics["macro_f1"],
            "leakage_detected": leakage_detected,
            "heldout_overlap_count": int(overlap_count),
            "publication_grade_threshold": float(args.accuracy_threshold),
            "publication_grade_threshold_passed": metrics["accuracy"]
            >= float(args.accuracy_threshold),
            "valid_evaluation_state": valid_state,
            "embedding_backend": metadata.get("embedding_backend", args.embedding_backend),
            "model_name": metadata.get("model_name", args.model_name),
            "benchmark_name": Path(args.held_out).name,
            "binary_relevance_accuracy": metrics["binary_relevance_accuracy"],
            "actionable_speculative_conditional_accuracy": metrics[
                "actionable_speculative_conditional_accuracy"
            ],
            "actionable_speculative_conditional_macro_f1": metrics[
                "actionable_speculative_conditional_macro_f1"
            ],
        },
        "inputs": inputs,
        "per_class": metrics["per_class"],
        "confusion_matrix": metrics["confusion_matrix"],
    }
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if status != "passed":
        raise SystemExit(
            "Held-out evaluation is invalid because leakage was detected or inputs are incomplete."
        )
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--held-out", default="data/validation/held_out_sentences.csv")
    parser.add_argument("--labels-master", default="data/labels/v1/labels_master.parquet")
    parser.add_argument("--centroids", default="artifacts/models/mpnet_prelim_v1/centroids.json")
    parser.add_argument(
        "--model-metadata", default="artifacts/models/mpnet_prelim_v1/metadata.json"
    )
    parser.add_argument("--selected-model-manifest", default="")
    parser.add_argument(
        "--output-report", default="reports/evaluation/heldout_eval_prelim_v1.json"
    )
    parser.add_argument("--model-id", default="mpnet_prelim_v1")
    parser.add_argument("--source-window-id", default="active_2021_2024")
    parser.add_argument("--embedding-backend", default="sentence_transformers")
    parser.add_argument("--model-name", default="sentence-transformers/all-mpnet-base-v2")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--hash-dim", type=int, default=64)
    parser.add_argument("--accuracy-threshold", type=float, default=0.80)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_evaluation(args)
    print(
        "[prelim-eval] held-out evaluated "
        f"accuracy={report['summary']['accuracy']:.4f} "
        f"macro_f1={report['summary']['macro_f1']:.4f}"
    )
    print(f"[prelim-eval] report -> {args.output_report}")


if __name__ == "__main__":
    main()
