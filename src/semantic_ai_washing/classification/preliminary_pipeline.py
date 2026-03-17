"""Shared helpers for the preliminary classifier workflow."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

import numpy as np

from semantic_ai_washing.labeling.common import ALLOWED_LABELS, normalize_sentence

DEFAULT_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
DEFAULT_EMBEDDING_BACKEND = "sentence_transformers"
DEFAULT_HASH_DIM = 64

_SENTENCE_TRANSFORMER_CACHE: dict[str, object] = {}


def sha256_file(path: str | Path) -> str:
    if path is None:
        return ""
    text = str(path).strip()
    if not text:
        return ""
    resolved = Path(path)
    if not resolved.exists() or resolved.is_dir():
        return ""
    hasher = hashlib.sha256()
    with resolved.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _normalize_rows(rows: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(rows, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    return rows / norms


def hash_embed_sentence(text: str, *, dim: int = DEFAULT_HASH_DIM) -> np.ndarray:
    tokens = normalize_sentence(text).split()
    vector = np.zeros(dim, dtype=np.float32)
    if not tokens:
        vector[0] = 1.0
        return vector
    for token in tokens:
        digest = hashlib.sha1(token.encode("utf-8")).digest()
        bucket = int.from_bytes(digest[:2], "big") % dim
        sign = 1.0 if digest[2] % 2 == 0 else -1.0
        weight = 1.0 + (digest[3] / 255.0)
        vector[bucket] += sign * weight
    norm = np.linalg.norm(vector)
    if norm == 0.0:
        vector[0] = 1.0
        return vector
    return vector / norm


def _load_sentence_transformer(model_name: str):
    if model_name not in _SENTENCE_TRANSFORMER_CACHE:
        from sentence_transformers import SentenceTransformer

        _SENTENCE_TRANSFORMER_CACHE[model_name] = SentenceTransformer(model_name)
    return _SENTENCE_TRANSFORMER_CACHE[model_name]


def embed_sentences(
    sentences: Iterable[str],
    *,
    backend: str = DEFAULT_EMBEDDING_BACKEND,
    model_name: str = DEFAULT_MODEL_NAME,
    batch_size: int = 32,
    hash_dim: int = DEFAULT_HASH_DIM,
) -> np.ndarray:
    sentence_list = [str(sentence) for sentence in sentences]
    if not sentence_list:
        return np.zeros((0, hash_dim), dtype=np.float32)
    if backend == "hash":
        return np.vstack(
            [hash_embed_sentence(sentence, dim=hash_dim) for sentence in sentence_list]
        )
    if backend != "sentence_transformers":
        raise ValueError(f"Unsupported embedding backend: {backend}")

    model = _load_sentence_transformer(model_name)
    embeddings = model.encode(
        sentence_list,
        batch_size=batch_size,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return np.asarray(embeddings, dtype=np.float32)


def compute_centroids(labels: list[str], embeddings: np.ndarray) -> dict[str, list[float]]:
    if len(labels) != len(embeddings):
        raise ValueError("Labels and embeddings must have the same number of rows.")
    if embeddings.ndim != 2:
        raise ValueError("Embeddings must be a 2D array.")

    centroids: dict[str, list[float]] = {}
    label_array = np.asarray(labels)
    for label in ALLOWED_LABELS:
        mask = label_array == label
        if not mask.any():
            raise ValueError(f"Missing training rows for label: {label}")
        centroid = embeddings[mask].mean(axis=0, dtype=np.float32)
        centroid = _normalize_rows(centroid.reshape(1, -1))[0]
        centroids[label] = centroid.astype(float).tolist()
    return centroids


def load_centroids(path: str | Path) -> dict[str, np.ndarray]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    centroids = {
        label: np.asarray(payload[label], dtype=np.float32)
        for label in ALLOWED_LABELS
        if label in payload
    }
    missing = [label for label in ALLOWED_LABELS if label not in centroids]
    if missing:
        raise ValueError(f"Centroids JSON is missing labels: {missing}")
    return {label: _normalize_rows(vec.reshape(1, -1))[0] for label, vec in centroids.items()}


def classify_embeddings(
    embeddings: np.ndarray,
    centroids: dict[str, np.ndarray],
) -> tuple[list[str], list[dict[str, float]]]:
    if embeddings.ndim != 2:
        raise ValueError("Embeddings must be a 2D array.")
    ordered_labels = [label for label in ALLOWED_LABELS if label in centroids]
    centroid_matrix = np.vstack([centroids[label] for label in ordered_labels])
    scored_embeddings = _normalize_rows(embeddings.astype(np.float32, copy=False))
    scores = scored_embeddings @ centroid_matrix.T
    best_indices = scores.argmax(axis=1)
    predicted_labels = [ordered_labels[idx] for idx in best_indices.tolist()]
    score_rows = []
    for row in scores:
        score_rows.append({label: float(row[idx]) for idx, label in enumerate(ordered_labels)})
    return predicted_labels, score_rows
