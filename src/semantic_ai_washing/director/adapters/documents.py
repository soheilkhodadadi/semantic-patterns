"""Compatibility shim for the package-owned director documents module."""

from semantic_director.documents import (
    read_text_document,
    summarize_document,
    summarize_roadmap_model,
)

__all__ = [
    "read_text_document",
    "summarize_document",
    "summarize_roadmap_model",
]
