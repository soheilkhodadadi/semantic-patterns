"""Evaluate the preliminary centroid model on the frozen held-out set."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score

from semantic_ai_washing.classification.preliminary_pipeline import (
    embed_sentences,
    classify_embeddings,
    load_centroids,
    sha256_file,
)
from semantic_ai_washing.labeling.common import (
    ALLOWED_LABELS,
    ensure_allowed_label,
    normalize_sentence,
    load_table,
)


def _load_metadata(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if str(payload.get("status", "")).strip() != "trained":
        raise ValueError("Model metadata must report `status = trained`.")
    return payload


def _load_held_out(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required_columns = {"sentence", "label"}
    missing = sorted(required_columns - set(frame.columns))
    if missing:
        raise ValueError(f"Held-out data missing required columns: {missing}")
    frame = frame.copy()
    frame["label"] = frame["label"].map(ensure_allowed_label)
    frame = frame[frame["label"].notna()].copy()
    if frame.empty:
        raise ValueError("Held-out file does not contain valid labeled rows.")
    return frame


def _heldout_overlap_count(labels_master_path: str | Path, held_out: pd.DataFrame) -> int:
    labels_master = load_table(labels_master_path)
    if "sentence" not in labels_master.columns:
        raise ValueError("Labels master must include `sentence` for leakage checks.")
    label_norms = labels_master["sentence"].fillna("").astype(str).map(normalize_sentence)
    held_norms = held_out["sentence"].fillna("").astype(str).map(normalize_sentence)
    return int(label_norms.isin(set(held_norms)).sum())


def run_evaluation(args: argparse.Namespace) -> dict[str, Any]:
    output_path = Path(args.output_report)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    metadata = _load_metadata(args.model_metadata)
    held_out = _load_held_out(args.held_out)
    overlap_count = _heldout_overlap_count(args.labels_master, held_out)
    leakage_detected = overlap_count > 0

    centroids = load_centroids(args.centroids)
    embeddings = embed_sentences(
        held_out["sentence"].fillna("").astype(str).tolist(),
        backend=str(metadata.get("embedding_backend", args.embedding_backend)),
        model_name=str(metadata.get("model_name", args.model_name)),
        batch_size=int(args.batch_size),
        hash_dim=int(metadata.get("hash_dim", args.hash_dim)),
    )
    predicted, _score_rows = classify_embeddings(embeddings, centroids)

    y_true = held_out["label"].astype(str).tolist()
    accuracy = float(accuracy_score(y_true, predicted))
    macro_f1 = float(f1_score(y_true, predicted, labels=list(ALLOWED_LABELS), average="macro"))
    confusion = confusion_matrix(y_true, predicted, labels=list(ALLOWED_LABELS))
    confusion_payload = {
        label: {
            inner: int(confusion[row_idx, col_idx]) for col_idx, inner in enumerate(ALLOWED_LABELS)
        }
        for row_idx, label in enumerate(ALLOWED_LABELS)
    }

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
            "accuracy": accuracy,
            "macro_f1": macro_f1,
            "leakage_detected": leakage_detected,
            "heldout_overlap_count": int(overlap_count),
            "publication_grade_threshold": float(args.accuracy_threshold),
            "publication_grade_threshold_passed": accuracy >= float(args.accuracy_threshold),
            "valid_evaluation_state": valid_state,
            "embedding_backend": metadata.get("embedding_backend", args.embedding_backend),
            "model_name": metadata.get("model_name", args.model_name),
        },
        "inputs": {
            "held_out": str(args.held_out),
            "labels_master": str(args.labels_master),
            "centroids": str(args.centroids),
            "model_metadata": str(args.model_metadata),
            "held_out_sha256": sha256_file(args.held_out),
            "labels_master_sha256": sha256_file(args.labels_master),
            "centroids_sha256": sha256_file(args.centroids),
            "model_metadata_sha256": sha256_file(args.model_metadata),
        },
        "confusion_matrix": confusion_payload,
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
