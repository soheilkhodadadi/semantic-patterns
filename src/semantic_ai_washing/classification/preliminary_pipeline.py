"""Compatibility shim for the member-owned preliminary classification pipeline."""

from __future__ import annotations

from ai_washing_member.classification import preliminary_pipeline as _member

DEFAULT_MODEL_NAME = _member.DEFAULT_MODEL_NAME
DEFAULT_EMBEDDING_BACKEND = _member.DEFAULT_EMBEDDING_BACKEND
DEFAULT_HASH_DIM = _member.DEFAULT_HASH_DIM
sha256_file = _member.sha256_file
hash_embed_sentence = _member.hash_embed_sentence
_load_sentence_transformer = _member._load_sentence_transformer
_resolve_sentence_transformer_source = _member._resolve_sentence_transformer_source
embed_sentences = _member.embed_sentences
compute_centroids = _member.compute_centroids
load_centroids = _member.load_centroids
classify_embeddings = _member.classify_embeddings

__all__ = [
    "DEFAULT_MODEL_NAME",
    "DEFAULT_EMBEDDING_BACKEND",
    "DEFAULT_HASH_DIM",
    "sha256_file",
    "hash_embed_sentence",
    "_load_sentence_transformer",
    "_resolve_sentence_transformer_source",
    "embed_sentences",
    "compute_centroids",
    "load_centroids",
    "classify_embeddings",
]
