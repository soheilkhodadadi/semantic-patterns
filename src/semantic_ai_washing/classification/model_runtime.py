"""Compatibility shim for the member-owned preliminary model runtime."""

from __future__ import annotations

from ai_washing_member.classification import model_runtime as _member

load_manifest = _member.load_manifest
build_legacy_two_stage_runtime = _member.build_legacy_two_stage_runtime
build_centroid_runtime = _member.build_centroid_runtime
build_pickle_runtime = _member.build_pickle_runtime
build_layered_runtime = _member.build_layered_runtime
build_selective_defer_runtime = _member.build_selective_defer_runtime
warm_runtime = _member.warm_runtime
predict_sentences = _member.predict_sentences
predict_sentences_with_metadata = _member.predict_sentences_with_metadata

__all__ = [
    "load_manifest",
    "build_legacy_two_stage_runtime",
    "build_centroid_runtime",
    "build_pickle_runtime",
    "build_layered_runtime",
    "build_selective_defer_runtime",
    "warm_runtime",
    "predict_sentences",
    "predict_sentences_with_metadata",
]
