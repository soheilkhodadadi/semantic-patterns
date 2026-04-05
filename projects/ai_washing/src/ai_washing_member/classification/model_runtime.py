"""Runtime helpers for selected preliminary classifier models."""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any, Callable

from ai_washing_member.classification.preliminary_pipeline import (
    _load_sentence_transformer,
    classify_embeddings,
    embed_sentences,
    load_centroids,
    _resolve_sentence_transformer_source,
    sha256_file,
)
from ai_washing_member.labeling.common import ALLOWED_LABELS


_MODEL_CACHE: dict[tuple[str, str], Any] = {}


def load_manifest(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Selected model manifest must decode to an object.")
    return payload


def build_legacy_two_stage_runtime(
    *,
    model_id: str = "legacy_two_stage_mpnet_rules",
    tau: float = 0.07,
    eps_irr: float = 0.03,
    min_tokens: int = 6,
    rule_boosts: bool = True,
) -> dict[str, Any]:
    return {
        "model_id": model_id,
        "model_type": "legacy_two_stage_mpnet_rules",
        "status": "trained",
        "preliminary_only": True,
        "source_window_id": "active_2021_2024",
        "runtime": {
            "two_stage": True,
            "rule_boosts": bool(rule_boosts),
            "tau": float(tau),
            "eps_irr": float(eps_irr),
            "min_tokens": int(min_tokens),
        },
    }


def build_centroid_runtime(
    *, metadata_path: str | Path, centroids_path: str | Path
) -> dict[str, Any]:
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    return {
        "model_id": str(metadata.get("model_id", "mpnet_prelim_centroid")),
        "model_type": str(metadata.get("model_type", "centroid_multiclass")),
        "status": str(metadata.get("status", "")),
        "preliminary_only": bool(metadata.get("preliminary_only", True)),
        "source_window_id": str(metadata.get("source_window_id", "active_2021_2024")),
        "runtime": {
            "centroids": str(centroids_path),
            "centroids_sha256": sha256_file(centroids_path),
            "metadata": str(metadata_path),
            "metadata_sha256": sha256_file(metadata_path),
            "embedding_backend": str(metadata.get("embedding_backend", "sentence_transformers")),
            "model_name": str(
                metadata.get("model_name", "sentence-transformers/all-mpnet-base-v2")
            ),
            "hash_dim": int(metadata.get("hash_dim", 64)),
            "batch_size": int(metadata.get("batch_size", 32)),
        },
    }


def build_pickle_runtime(*, metadata_path: str | Path) -> dict[str, Any]:
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    runtime = dict(metadata.get("runtime", {}))
    runtime.setdefault("metadata", str(metadata_path))
    runtime.setdefault("metadata_sha256", sha256_file(metadata_path))
    return {
        "model_id": str(metadata.get("model_id", "")),
        "model_type": str(metadata.get("model_type", "")),
        "status": str(metadata.get("status", "")),
        "preliminary_only": bool(metadata.get("preliminary_only", True)),
        "source_window_id": str(metadata.get("source_window_id", "active_2021_2024")),
        "runtime": runtime,
    }


def _load_pickle(path: str | Path) -> Any:
    resolved = Path(path).resolve()
    key = ("pickle", str(resolved))
    if key not in _MODEL_CACHE:
        with resolved.open("rb") as handle:
            _MODEL_CACHE[key] = pickle.load(handle)
    return _MODEL_CACHE[key]


def warm_runtime(
    manifest: dict[str, Any], *, on_stage: Callable[[str], None] | None = None
) -> None:
    model_type = str(manifest.get("model_type", "")).strip()
    runtime = manifest.get("runtime", {}) if isinstance(manifest.get("runtime", {}), dict) else {}

    def emit(stage: str) -> None:
        if on_stage is not None:
            on_stage(stage)

    if model_type == "centroid_multiclass":
        emit("load_centroids")
        load_centroids(runtime["centroids"])
        backend = str(runtime.get("embedding_backend", "sentence_transformers"))
        if backend == "sentence_transformers":
            emit("load_embedding_model")
            _load_sentence_transformer(
                _resolve_sentence_transformer_source(
                    str(runtime.get("model_name", "sentence-transformers/all-mpnet-base-v2"))
                )
            )
        return

    if model_type == "logreg_multiclass":
        emit("load_model_pickle")
        _load_pickle(runtime["model_pickle"])
        backend = str(runtime.get("embedding_backend", "sentence_transformers"))
        if backend == "sentence_transformers":
            emit("load_embedding_model")
            _load_sentence_transformer(
                _resolve_sentence_transformer_source(
                    str(runtime.get("model_name", "sentence-transformers/all-mpnet-base-v2"))
                )
            )
        return

    if model_type == "binary_relevance_then_as":
        emit("load_relevance_pickle")
        _load_pickle(runtime["relevance_model_pickle"])
        emit("load_actionable_speculative_pickle")
        _load_pickle(runtime["actionable_speculative_model_pickle"])
        backend = str(runtime.get("embedding_backend", "sentence_transformers"))
        if backend == "sentence_transformers":
            emit("load_embedding_model")
            _load_sentence_transformer(
                _resolve_sentence_transformer_source(
                    str(runtime.get("model_name", "sentence-transformers/all-mpnet-base-v2"))
                )
            )
        return


def predict_sentences(
    sentences: list[str], manifest: dict[str, Any]
) -> tuple[list[str], list[dict[str, float]]]:
    model_type = str(manifest.get("model_type", "")).strip()
    runtime = manifest.get("runtime", {}) if isinstance(manifest.get("runtime", {}), dict) else {}

    if model_type == "legacy_two_stage_mpnet_rules":
        from semantic_ai_washing.core.classify import classify_two_stage

        predicted: list[str] = []
        scores: list[dict[str, float]] = []
        for sentence in sentences:
            label, score = classify_two_stage(
                sentence,
                two_stage=bool(runtime.get("two_stage", True)),
                rule_boosts=bool(runtime.get("rule_boosts", True)),
                tau=float(runtime.get("tau", 0.07)),
                eps_irr=float(runtime.get("eps_irr", 0.03)),
                min_tokens=int(runtime.get("min_tokens", 6)),
            )
            predicted.append(label)
            scores.append({name: float(score.get(name, 0.0)) for name in ALLOWED_LABELS})
        return predicted, scores

    if model_type == "centroid_multiclass":
        centroids = load_centroids(runtime["centroids"])
        embeddings = embed_sentences(
            sentences,
            backend=str(runtime.get("embedding_backend", "sentence_transformers")),
            model_name=str(runtime.get("model_name", "sentence-transformers/all-mpnet-base-v2")),
            batch_size=int(runtime.get("batch_size", 32)),
            hash_dim=int(runtime.get("hash_dim", 64)),
        )
        return classify_embeddings(embeddings, centroids)

    if model_type == "logreg_multiclass":
        payload = _load_pickle(runtime["model_pickle"])
        embeddings = embed_sentences(
            sentences,
            backend=str(runtime.get("embedding_backend", "sentence_transformers")),
            model_name=str(runtime.get("model_name", "sentence-transformers/all-mpnet-base-v2")),
            batch_size=int(runtime.get("batch_size", 32)),
            hash_dim=int(runtime.get("hash_dim", 64)),
        )
        model = payload["model"]
        classes = [str(value) for value in model.classes_.tolist()]
        probs = model.predict_proba(embeddings)
        predicted = [classes[idx] for idx in probs.argmax(axis=1).tolist()]
        score_rows = []
        for row in probs:
            mapping = {label: 0.0 for label in ALLOWED_LABELS}
            for idx, label in enumerate(classes):
                if label in mapping:
                    mapping[label] = float(row[idx])
            score_rows.append(mapping)
        return predicted, score_rows

    if model_type == "binary_relevance_then_as":
        rel_payload = _load_pickle(runtime["relevance_model_pickle"])
        as_payload = _load_pickle(runtime["actionable_speculative_model_pickle"])
        embeddings = embed_sentences(
            sentences,
            backend=str(runtime.get("embedding_backend", "sentence_transformers")),
            model_name=str(runtime.get("model_name", "sentence-transformers/all-mpnet-base-v2")),
            batch_size=int(runtime.get("batch_size", 32)),
            hash_dim=int(runtime.get("hash_dim", 64)),
        )
        rel_model = rel_payload["model"]
        rel_classes = [str(value) for value in rel_model.classes_.tolist()]
        rel_probs = rel_model.predict_proba(embeddings)
        as_model = as_payload["model"]
        as_classes = [str(value) for value in as_model.classes_.tolist()]
        as_probs = as_model.predict_proba(embeddings)
        predicted: list[str] = []
        score_rows: list[dict[str, float]] = []
        irr_idx = rel_classes.index("Irrelevant")
        rel_idx = rel_classes.index("Non-Irrelevant")
        a_idx = as_classes.index("Actionable")
        s_idx = as_classes.index("Speculative")
        for rel_row, as_row in zip(rel_probs, as_probs, strict=True):
            p_irrelevant = float(rel_row[irr_idx])
            p_relevant = float(rel_row[rel_idx])
            p_actionable = p_relevant * float(as_row[a_idx])
            p_speculative = p_relevant * float(as_row[s_idx])
            scores = {
                "Actionable": p_actionable,
                "Speculative": p_speculative,
                "Irrelevant": p_irrelevant,
            }
            label = max(scores.items(), key=lambda item: item[1])[0]
            predicted.append(label)
            score_rows.append(scores)
        return predicted, score_rows

    raise ValueError(f"Unsupported model_type: {model_type}")
