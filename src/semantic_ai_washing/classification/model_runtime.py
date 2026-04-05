"""Compatibility shim for the member-owned preliminary model runtime."""

from __future__ import annotations

from ai_washing_member.classification import model_runtime as _member

load_manifest = _member.load_manifest
build_legacy_two_stage_runtime = _member.build_legacy_two_stage_runtime
build_centroid_runtime = _member.build_centroid_runtime
build_pickle_runtime = _member.build_pickle_runtime
warm_runtime = _member.warm_runtime
predict_sentences = _member.predict_sentences

__all__ = [
    "load_manifest",
    "build_legacy_two_stage_runtime",
    "build_centroid_runtime",
    "build_pickle_runtime",
    "warm_runtime",
    "predict_sentences",
]
