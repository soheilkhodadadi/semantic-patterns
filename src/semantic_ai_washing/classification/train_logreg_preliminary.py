"""Train a preliminary multinomial logistic-regression classifier on MPNet embeddings."""

from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.linear_model import LogisticRegression

from semantic_ai_washing.classification.preliminary_pipeline import (
    DEFAULT_EMBEDDING_BACKEND,
    DEFAULT_MODEL_NAME,
    embed_sentences,
    sha256_file,
)
from semantic_ai_washing.labeling.common import ALLOWED_LABELS, ensure_allowed_label, load_table


def _load_training_frame(
    labels_master_path: str | Path, split_registry_path: str | Path
) -> tuple[pd.DataFrame, dict[str, Any]]:
    labels_master = load_table(labels_master_path)
    split_registry = pd.read_csv(split_registry_path)
    required_label_columns = {"sentence_id", "sentence", "label"}
    required_split_columns = {"sentence_id", "split", "split_version", "seed"}
    missing_labels = sorted(required_label_columns - set(labels_master.columns))
    missing_split = sorted(required_split_columns - set(split_registry.columns))
    if missing_labels:
        raise ValueError(f"Labels master missing required columns: {missing_labels}")
    if missing_split:
        raise ValueError(f"Split registry missing required columns: {missing_split}")

    labels_master = labels_master.copy()
    labels_master["label"] = labels_master["label"].map(ensure_allowed_label)
    labels_master = labels_master[labels_master["label"].notna()].copy()
    merged = labels_master.merge(
        split_registry[["sentence_id", "split", "split_version", "seed"]],
        on="sentence_id",
        how="left",
        validate="one_to_one",
    )
    train = merged.loc[merged["split"] == "train"].copy()
    validation = merged.loc[merged["split"] == "validation"].copy()
    if train.empty:
        raise ValueError("Frozen split registry does not contain any training rows.")
    train_counts = {label: int((train["label"] == label).sum()) for label in ALLOWED_LABELS}
    validation_counts = {
        label: int((validation["label"] == label).sum()) for label in ALLOWED_LABELS
    }
    if any(count == 0 for count in train_counts.values()):
        raise ValueError(f"Training split must include all labels; observed counts={train_counts}")
    return train, {
        "rows_total": int(len(merged)),
        "rows_train": int(len(train)),
        "rows_validation_reserved": int(len(validation)),
        "train_class_counts": train_counts,
        "validation_class_counts": validation_counts,
        "split_version": str(split_registry["split_version"].astype(str).mode().iloc[0]),
        "seed": int(split_registry["seed"].astype(int).mode().iloc[0]),
    }


def run_training(args: argparse.Namespace) -> dict[str, Any]:
    model_output = Path(args.model_output)
    metadata_output = Path(args.metadata_output)
    model_output.parent.mkdir(parents=True, exist_ok=True)
    metadata_output.parent.mkdir(parents=True, exist_ok=True)

    train, split_meta = _load_training_frame(args.labels_master, args.split_registry)
    embeddings = embed_sentences(
        train["sentence"].fillna("").astype(str).tolist(),
        backend=args.embedding_backend,
        model_name=args.model_name,
        batch_size=int(args.batch_size),
        hash_dim=int(args.hash_dim),
    )
    model_kwargs: dict[str, Any] = {
        "class_weight": "balanced",
        "max_iter": int(args.max_iter),
        "random_state": int(args.seed),
        "solver": "lbfgs",
    }
    # Newer sklearn variants in this environment removed the explicit multi_class kwarg.
    if "multi_class" in LogisticRegression.__init__.__code__.co_varnames:
        model_kwargs["multi_class"] = "multinomial"
    model = LogisticRegression(**model_kwargs)
    model.fit(embeddings, train["label"].astype(str).tolist())
    with model_output.open("wb") as handle:
        pickle.dump({"model": model}, handle)

    metadata = {
        "status": "trained",
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "model_id": str(args.model_id),
        "model_type": "logreg_multiclass",
        "preliminary_only": True,
        "source_window_id": str(args.source_window_id),
        "embedding_backend": str(args.embedding_backend),
        "model_name": str(args.model_name),
        "hash_dim": int(args.hash_dim),
        "batch_size": int(args.batch_size),
        "runtime": {
            "model_pickle": str(model_output),
            "model_pickle_sha256": sha256_file(model_output),
            "embedding_backend": str(args.embedding_backend),
            "model_name": str(args.model_name),
            "hash_dim": int(args.hash_dim),
            "batch_size": int(args.batch_size),
        },
        "inputs": {
            "labels_master": str(args.labels_master),
            "split_registry": str(args.split_registry),
            "labels_master_sha256": sha256_file(args.labels_master),
            "split_registry_sha256": sha256_file(args.split_registry),
        },
        "outputs": {
            "model_pickle": str(model_output),
            "model_pickle_sha256": sha256_file(model_output),
        },
        "summary": split_meta,
    }
    metadata_output.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels-master", default="data/labels/v1/labels_master.parquet")
    parser.add_argument("--split-registry", default="data/metadata/splits/split_registry_v1.csv")
    parser.add_argument(
        "--model-output", default="artifacts/models/mpnet_logreg_prelim_v1/model.pkl"
    )
    parser.add_argument(
        "--metadata-output", default="artifacts/models/mpnet_logreg_prelim_v1/metadata.json"
    )
    parser.add_argument("--model-id", default="mpnet_logreg_prelim_v1")
    parser.add_argument("--source-window-id", default="active_2021_2024")
    parser.add_argument("--embedding-backend", default=DEFAULT_EMBEDDING_BACKEND)
    parser.add_argument("--model-name", default=DEFAULT_MODEL_NAME)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--hash-dim", type=int, default=64)
    parser.add_argument("--max-iter", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260315)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = run_training(args)
    print(
        "[prelim-logreg] trained "
        f"train_rows={metadata['summary']['rows_train']} validation_reserved={metadata['summary']['rows_validation_reserved']}"
    )
    print(f"[prelim-logreg] metadata -> {args.metadata_output}")


if __name__ == "__main__":
    main()
