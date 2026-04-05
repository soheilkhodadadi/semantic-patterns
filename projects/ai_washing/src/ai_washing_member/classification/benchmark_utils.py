"""Shared evaluation helpers for preliminary classifier benchmarking."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)

from ai_washing_member.labeling.common import (
    ALLOWED_LABELS,
    ensure_allowed_label,
    normalize_sentence,
)

BINARY_LABELS = ("Irrelevant", "Non-Irrelevant")


def load_benchmark_frame(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required = {"sentence", "label"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Benchmark file missing required columns: {missing}")
    frame = frame.copy()
    frame["label"] = frame["label"].map(ensure_allowed_label)
    frame = frame[frame["label"].notna()].copy()
    if frame.empty:
        raise ValueError(f"Benchmark file contains no valid labels: {path}")
    return frame


def build_validation_benchmark(
    labels_master_path: str | Path, split_registry_path: str | Path
) -> pd.DataFrame:
    labels = pd.read_parquet(labels_master_path)
    splits = pd.read_csv(split_registry_path)
    required_label_columns = {"sentence_id", "sentence", "label"}
    missing_labels = sorted(required_label_columns - set(labels.columns))
    if missing_labels:
        raise ValueError(f"Labels master missing required columns: {missing_labels}")
    if "split" not in splits.columns:
        raise ValueError("Split registry must include `split`.")
    merged = labels.merge(splits[["sentence_id", "split"]], on="sentence_id", how="inner")
    validation = merged.loc[
        merged["split"] == "validation", ["sentence_id", "sentence", "label"]
    ].copy()
    validation["label"] = validation["label"].map(ensure_allowed_label)
    validation = validation[validation["label"].notna()].copy()
    if validation.empty:
        raise ValueError("Validation benchmark is empty.")
    return validation


def heldout_overlap_count(labels_master_path: str | Path, benchmark_frame: pd.DataFrame) -> int:
    labels_master = pd.read_parquet(labels_master_path)
    if "sentence" not in labels_master.columns:
        raise ValueError("Labels master must include `sentence` for leakage checks.")
    label_norms = labels_master["sentence"].fillna("").astype(str).map(normalize_sentence)
    benchmark_norms = benchmark_frame["sentence"].fillna("").astype(str).map(normalize_sentence)
    return int(label_norms.isin(set(benchmark_norms)).sum())


def _to_binary(label: str) -> str:
    return "Irrelevant" if label == "Irrelevant" else "Non-Irrelevant"


def compute_metrics(y_true: list[str], y_pred: list[str]) -> dict[str, Any]:
    if len(y_true) != len(y_pred):
        raise ValueError("Prediction length must match truth length.")
    if not y_true:
        raise ValueError("Benchmark is empty.")

    accuracy = float(accuracy_score(y_true, y_pred))
    macro_f1 = float(f1_score(y_true, y_pred, labels=list(ALLOWED_LABELS), average="macro"))
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=list(ALLOWED_LABELS),
        zero_division=0,
    )
    confusion = confusion_matrix(y_true, y_pred, labels=list(ALLOWED_LABELS))
    confusion_payload = {
        label: {
            inner: int(confusion[row_idx, col_idx]) for col_idx, inner in enumerate(ALLOWED_LABELS)
        }
        for row_idx, label in enumerate(ALLOWED_LABELS)
    }
    per_class = {
        label: {
            "precision": float(precision[idx]),
            "recall": float(recall[idx]),
            "f1": float(f1[idx]),
            "support": int(support[idx]),
        }
        for idx, label in enumerate(ALLOWED_LABELS)
    }

    y_true_binary = [_to_binary(label) for label in y_true]
    y_pred_binary = [_to_binary(label) for label in y_pred]
    binary_accuracy = float(accuracy_score(y_true_binary, y_pred_binary))
    binary_macro_f1 = float(
        f1_score(y_true_binary, y_pred_binary, labels=list(BINARY_LABELS), average="macro")
    )

    as_pairs = [
        (truth, pred)
        for truth, pred in zip(y_true, y_pred, strict=True)
        if truth in {"Actionable", "Speculative"}
    ]
    if as_pairs:
        as_true = [truth for truth, _ in as_pairs]
        as_pred = [
            pred if pred in {"Actionable", "Speculative"} else "Speculative"
            for _, pred in as_pairs
        ]
        as_accuracy = float(accuracy_score(as_true, as_pred))
        as_macro_f1 = float(
            f1_score(as_true, as_pred, labels=["Actionable", "Speculative"], average="macro")
        )
    else:
        as_accuracy = 0.0
        as_macro_f1 = 0.0

    return {
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "per_class": per_class,
        "confusion_matrix": confusion_payload,
        "binary_relevance_accuracy": binary_accuracy,
        "binary_relevance_macro_f1": binary_macro_f1,
        "actionable_speculative_conditional_items": int(len(as_pairs)),
        "actionable_speculative_conditional_accuracy": as_accuracy,
        "actionable_speculative_conditional_macro_f1": as_macro_f1,
    }
