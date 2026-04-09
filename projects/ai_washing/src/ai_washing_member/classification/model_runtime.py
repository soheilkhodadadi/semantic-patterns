"""Runtime helpers for selected preliminary classifier models."""

from __future__ import annotations

import json
import os
import pickle
import time
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
from semantic_director.api_assistive import (
    build_prompt_messages,
    load_api_assistive_policy,
    parse_assistive_response_text,
    validate_assistive_response_payload,
)
from semantic_labcore.openai_responses import call_responses_api, extract_response_text


_MODEL_CACHE: dict[tuple[str, str], Any] = {}
_POLICY_CACHE: dict[str, tuple[Any, Path]] = {}
PARSE_RETRY_LIMIT = 2


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


def build_layered_runtime(
    *, binary_metadata_path: str | Path, logreg_metadata_path: str | Path
) -> dict[str, Any]:
    binary_metadata = json.loads(Path(binary_metadata_path).read_text(encoding="utf-8"))
    logreg_metadata = json.loads(Path(logreg_metadata_path).read_text(encoding="utf-8"))
    binary_runtime = dict(binary_metadata.get("runtime", {}))
    logreg_runtime = dict(logreg_metadata.get("runtime", {}))

    shared_keys = ("embedding_backend", "model_name", "hash_dim", "batch_size")
    for key in shared_keys:
        if binary_runtime.get(key) != logreg_runtime.get(key):
            raise ValueError(
                "Layered runtime requires matching embedding configuration for binary/logreg "
                f"models; mismatch on {key!r}."
            )

    return {
        "model_id": "layered_binary_relevance_logreg_as_v1",
        "model_type": "layered_binary_relevance_logreg_as",
        "status": "trained",
        "preliminary_only": True,
        "source_window_id": str(binary_metadata.get("source_window_id", "active_2021_2024")),
        "runtime": {
            "relevance_model_pickle": str(binary_runtime["relevance_model_pickle"]),
            "relevance_model_pickle_sha256": str(binary_runtime["relevance_model_pickle_sha256"]),
            "logreg_model_pickle": str(logreg_runtime["model_pickle"]),
            "logreg_model_pickle_sha256": str(logreg_runtime["model_pickle_sha256"]),
            "binary_metadata": str(binary_metadata_path),
            "binary_metadata_sha256": sha256_file(binary_metadata_path),
            "logreg_metadata": str(logreg_metadata_path),
            "logreg_metadata_sha256": sha256_file(logreg_metadata_path),
            "embedding_backend": str(binary_runtime["embedding_backend"]),
            "model_name": str(binary_runtime["model_name"]),
            "hash_dim": int(binary_runtime["hash_dim"]),
            "batch_size": int(binary_runtime["batch_size"]),
        },
    }


def build_selective_defer_runtime(
    *,
    binary_metadata_path: str | Path,
    logreg_metadata_path: str | Path,
    api_policy_path: str | Path,
    low_confidence_threshold: float,
    model_id: str = "",
) -> dict[str, Any]:
    layered = build_layered_runtime(
        binary_metadata_path=binary_metadata_path,
        logreg_metadata_path=logreg_metadata_path,
    )
    runtime = dict(layered["runtime"])
    runtime["api_a_policy"] = str(api_policy_path)
    runtime["api_a_policy_sha256"] = sha256_file(api_policy_path)
    runtime["defer_low_confidence_threshold"] = float(low_confidence_threshold)

    threshold_token = str(int(round(float(low_confidence_threshold) * 100))).zfill(2)
    selected_model_id = model_id or f"selective_defer_layered_api_a_conf{threshold_token}_v1"
    return {
        "model_id": selected_model_id,
        "model_type": "selective_defer_layered_api_a",
        "status": "trained",
        "preliminary_only": True,
        "source_window_id": str(layered.get("source_window_id", "active_2021_2024")),
        "runtime": runtime,
    }


def _load_pickle(path: str | Path) -> Any:
    resolved = Path(path).resolve()
    key = ("pickle", str(resolved))
    if key not in _MODEL_CACHE:
        with resolved.open("rb") as handle:
            _MODEL_CACHE[key] = pickle.load(handle)
    return _MODEL_CACHE[key]


def _load_api_policy(path: str | Path) -> tuple[Any, Path]:
    resolved = Path(path).resolve()
    key = str(resolved)
    if key not in _POLICY_CACHE:
        _POLICY_CACHE[key] = load_api_assistive_policy(resolved)
    return _POLICY_CACHE[key]


def _predict_layered_local_rows(
    sentences: list[str], runtime: dict[str, Any]
) -> list[dict[str, Any]]:
    rel_payload = _load_pickle(runtime["relevance_model_pickle"])
    logreg_payload = _load_pickle(runtime["logreg_model_pickle"])
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
    logreg_model = logreg_payload["model"]
    logreg_classes = [str(value) for value in logreg_model.classes_.tolist()]
    logreg_probs = logreg_model.predict_proba(embeddings)

    irr_idx = rel_classes.index("Irrelevant")
    rel_idx = rel_classes.index("Non-Irrelevant")
    logreg_index = {label: idx for idx, label in enumerate(logreg_classes)}
    rows: list[dict[str, Any]] = []

    for rel_row, logreg_row in zip(rel_probs, logreg_probs, strict=True):
        p_irrelevant = float(rel_row[irr_idx])
        p_relevant = float(rel_row[rel_idx])
        p_actionable_raw = float(logreg_row[logreg_index["Actionable"]])
        p_speculative_raw = float(logreg_row[logreg_index["Speculative"]])
        p_logreg_irrelevant = float(logreg_row[logreg_index["Irrelevant"]])
        as_mass = p_actionable_raw + p_speculative_raw
        if as_mass > 0.0:
            conditional_a = p_actionable_raw / as_mass
            conditional_s = p_speculative_raw / as_mass
        else:
            conditional_a = 0.5
            conditional_s = 0.5

        p_actionable = p_relevant * conditional_a
        p_speculative = p_relevant * conditional_s
        scores = {
            "Actionable": p_actionable,
            "Speculative": p_speculative,
            "Irrelevant": p_irrelevant,
        }
        local_label = max(scores.items(), key=lambda item: item[1])[0]
        local_confidence = float(max(scores.values()))
        binary_label = "Irrelevant" if p_irrelevant >= p_relevant else "Non-Irrelevant"
        logreg_scores = {
            "Actionable": p_actionable_raw,
            "Speculative": p_speculative_raw,
            "Irrelevant": p_logreg_irrelevant,
        }
        logreg_label = max(logreg_scores.items(), key=lambda item: item[1])[0]
        rows.append(
            {
                "scores": scores,
                "local_label": local_label,
                "local_confidence": local_confidence,
                "conditional_as_margin": float(abs(conditional_a - conditional_s)),
                "binary_label": binary_label,
                "logreg_label": logreg_label,
                "binary_logreg_relevance_disagreement": (
                    (binary_label == "Irrelevant") != (logreg_label == "Irrelevant")
                ),
            }
        )
    return rows


def _call_assistive_label(
    *,
    sentence: str,
    source_section: str,
    policy_path: str | Path,
) -> dict[str, Any]:
    policy, _ = _load_api_policy(policy_path)
    api_key = os.getenv(policy.env_var, "").strip()
    if not api_key:
        raise RuntimeError(f"{policy.env_var} is required for selective-defer classification.")

    messages = build_prompt_messages(policy, sentence, source_section=source_section)
    extra_payload: dict[str, Any] = {}
    reasoning_effort = str(policy.request.get("reasoning_effort", "")).strip()
    if reasoning_effort:
        extra_payload["reasoning"] = {"effort": reasoning_effort}
    text_format = policy.request.get("text_format", "")
    if isinstance(text_format, dict) and text_format:
        extra_payload["text"] = {"format": text_format}

    response_payload: dict[str, Any] | None = None
    response_text = ""
    for attempt in range(PARSE_RETRY_LIMIT + 1):
        response_payload = call_responses_api(
            model=policy.model,
            input_payload=messages,
            api_key=api_key,
            max_output_tokens=int(policy.request.get("max_output_tokens", 200) or 200),
            timeout_seconds=int(policy.request.get("timeout_seconds", 60) or 60),
            store=bool(policy.request.get("store", False)),
            extra_payload=extra_payload or None,
        )
        response_text = extract_response_text(response_payload)
        try:
            parsed = parse_assistive_response_text(response_text)
            validated = validate_assistive_response_payload(parsed, policy)
            return {
                "api_a_label": validated["label"],
                "api_a_confidence": validated["confidence"],
                "api_a_rationale": validated["rationale"],
                "api_a_model": policy.model,
            }
        except (ValueError, json.JSONDecodeError):
            if attempt >= PARSE_RETRY_LIMIT:
                raise
            time.sleep(min(2**attempt, 3))

    raise RuntimeError("Selective-defer API label call failed unexpectedly.")


def predict_sentences_with_metadata(
    sentences: list[str],
    manifest: dict[str, Any],
    *,
    source_sections: list[str] | None = None,
) -> tuple[list[str], list[dict[str, float]], list[dict[str, Any]]]:
    if source_sections is None:
        source_sections = [""] * len(sentences)
    if len(source_sections) != len(sentences):
        raise ValueError("source_sections must match the number of input sentences.")

    model_type = str(manifest.get("model_type", "")).strip()
    runtime = manifest.get("runtime", {}) if isinstance(manifest.get("runtime", {}), dict) else {}

    if model_type == "selective_defer_layered_api_a":
        local_rows = _predict_layered_local_rows(sentences, runtime)
        threshold = float(runtime.get("defer_low_confidence_threshold", 0.49))
        predicted: list[str] = []
        score_rows: list[dict[str, float]] = []
        metadata_rows: list[dict[str, Any]] = []
        for sentence, source_section, local in zip(
            sentences, source_sections, local_rows, strict=True
        ):
            scores = dict(local["scores"])
            local_label = str(local["local_label"])
            local_confidence = float(local["local_confidence"])
            deferred = local_confidence < threshold
            api_payload = {
                "api_a_label": "",
                "api_a_confidence": "",
                "api_a_rationale": "",
                "api_a_model": "",
            }
            final_label = local_label
            prediction_source = "local"
            if deferred:
                api_payload = _call_assistive_label(
                    sentence=str(sentence),
                    source_section=str(source_section or ""),
                    policy_path=runtime["api_a_policy"],
                )
                final_label = str(api_payload["api_a_label"])
                prediction_source = "api_a"
            predicted.append(final_label)
            score_rows.append(scores)
            metadata_rows.append(
                {
                    "prediction_source": prediction_source,
                    "deferred_to_api": bool(deferred),
                    "defer_rule": "local_confidence_below_threshold",
                    "defer_threshold": threshold,
                    "local_label": local_label,
                    "local_confidence": local_confidence,
                    "conditional_as_margin": float(local["conditional_as_margin"]),
                    "binary_logreg_relevance_disagreement": bool(
                        local["binary_logreg_relevance_disagreement"]
                    ),
                    **api_payload,
                }
            )
        return predicted, score_rows, metadata_rows

    predicted, score_rows = predict_sentences(sentences, manifest)
    metadata_rows: list[dict[str, Any]] = []
    for label, scores in zip(predicted, score_rows, strict=True):
        actionable = float(scores.get("Actionable", 0.0))
        speculative = float(scores.get("Speculative", 0.0))
        as_mass = actionable + speculative
        if as_mass > 0.0:
            conditional_as_margin = abs((actionable / as_mass) - (speculative / as_mass))
        else:
            conditional_as_margin = 0.0
        metadata_rows.append(
            {
                "prediction_source": "local",
                "deferred_to_api": False,
                "defer_rule": "",
                "defer_threshold": "",
                "local_label": label,
                "local_confidence": float(max(scores.values())) if scores else 0.0,
                "conditional_as_margin": float(conditional_as_margin),
                "binary_logreg_relevance_disagreement": False,
                "api_a_label": "",
                "api_a_confidence": "",
                "api_a_rationale": "",
                "api_a_model": "",
            }
        )
    return predicted, score_rows, metadata_rows


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

    if model_type == "layered_binary_relevance_logreg_as":
        emit("load_relevance_pickle")
        _load_pickle(runtime["relevance_model_pickle"])
        emit("load_logreg_pickle")
        _load_pickle(runtime["logreg_model_pickle"])
        backend = str(runtime.get("embedding_backend", "sentence_transformers"))
        if backend == "sentence_transformers":
            emit("load_embedding_model")
            _load_sentence_transformer(
                _resolve_sentence_transformer_source(
                    str(runtime.get("model_name", "sentence-transformers/all-mpnet-base-v2"))
                )
            )
        return

    if model_type == "selective_defer_layered_api_a":
        emit("load_relevance_pickle")
        _load_pickle(runtime["relevance_model_pickle"])
        emit("load_logreg_pickle")
        _load_pickle(runtime["logreg_model_pickle"])
        emit("load_api_policy")
        _load_api_policy(runtime["api_a_policy"])
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

    if model_type == "layered_binary_relevance_logreg_as":
        local_rows = _predict_layered_local_rows(sentences, runtime)
        predicted = [str(row["local_label"]) for row in local_rows]
        score_rows = [dict(row["scores"]) for row in local_rows]
        return predicted, score_rows

    if model_type == "selective_defer_layered_api_a":
        predicted, score_rows, _ = predict_sentences_with_metadata(sentences, manifest)
        return predicted, score_rows

    raise ValueError(f"Unsupported model_type: {model_type}")
