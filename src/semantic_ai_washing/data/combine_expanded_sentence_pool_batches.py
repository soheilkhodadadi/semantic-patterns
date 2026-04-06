"""Compatibility shim for the member-owned sentence-pool combine helpers."""

from ai_washing_member.data.combine_expanded_sentence_pool_batches import (
    _load_manifest,
    _load_sentences,
    _sha256_file,
    combine_expanded_sentence_pool_batches,
    main,
    parse_args,
)

__all__ = [
    "_sha256_file",
    "_load_manifest",
    "_load_sentences",
    "combine_expanded_sentence_pool_batches",
    "parse_args",
    "main",
]
