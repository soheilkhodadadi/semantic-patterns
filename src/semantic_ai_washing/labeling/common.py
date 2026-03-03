"""Shared helpers for label expansion and dataset hygiene."""

from __future__ import annotations

import hashlib
import re
from typing import Iterable

ALLOWED_LABELS = ("Actionable", "Speculative", "Irrelevant")

_NON_WORD_RE = re.compile(r"[^\w\s]+", re.UNICODE)
_WS_RE = re.compile(r"\s+")


def normalize_sentence(sentence: str) -> str:
    """Canonical sentence normalization for dedupe and leakage checks."""
    if sentence is None:
        return ""
    lowered = str(sentence).lower().strip()
    lowered = _NON_WORD_RE.sub(" ", lowered)
    lowered = _WS_RE.sub(" ", lowered)
    return lowered.strip()


def compute_sentence_id(sentence_norm: str) -> str:
    """Return stable sentence identifier derived from normalized text."""
    digest = hashlib.sha1(sentence_norm.encode("utf-8")).hexdigest()
    return digest[:16]


def compute_sample_id(source_file: str, sentence_index: int, sentence_norm: str) -> str:
    """Return stable row identifier derived from source metadata and sentence."""
    payload = f"{source_file}|{sentence_index}|{sentence_norm}"
    digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()
    return digest[:16]


def token_count(sentence: str) -> int:
    """Count non-empty whitespace-separated tokens."""
    if sentence is None:
        return 0
    return len([tok for tok in str(sentence).split() if tok.strip()])


def length_bin_from_tokens(tokens: int) -> str:
    """Return short/medium/long bin from token count."""
    if tokens <= 12:
        return "short"
    if tokens <= 24:
        return "medium"
    return "long"


def parse_uncertain_flag(value) -> int:
    """Normalize uncertainty marker to {0,1}."""
    if value is None:
        return 0
    text = str(value).strip().lower()
    if text in {"1", "true", "t", "yes", "y"}:
        return 1
    return 0


def ensure_allowed_label(label: str | None) -> str | None:
    """Return normalized label if allowed, otherwise None."""
    if label is None:
        return None
    text = str(label).strip()
    return text if text in ALLOWED_LABELS else None


def safe_int(value, default: int = 0) -> int:
    """Best-effort integer parsing."""
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return default
    try:
        return int(float(text))
    except (TypeError, ValueError):
        return default


def row_sha256(rows: Iterable[str]) -> str:
    """Hash a sequence of row strings for lightweight fingerprinting."""
    hasher = hashlib.sha256()
    for row in rows:
        hasher.update(row.encode("utf-8"))
    return hasher.hexdigest()
