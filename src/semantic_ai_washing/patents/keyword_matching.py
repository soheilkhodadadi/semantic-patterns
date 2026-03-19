"""Shared helpers for patent keyword loading, phrase matching, and name normalization."""

from __future__ import annotations

import re
from pathlib import Path


LEGAL_SUFFIXES = {
    "inc",
    "incorporated",
    "corp",
    "corporation",
    "co",
    "company",
    "ltd",
    "limited",
    "llc",
    "llp",
    "lp",
    "plc",
    "ag",
    "nv",
    "sa",
    "spa",
    "bv",
    "gmbh",
    "holdings",
    "holding",
}


def normalize_org_name(value: str) -> str:
    text = re.sub(r"[^\w\s]", " ", str(value).lower())
    tokens = [token for token in text.split() if token]
    while tokens and tokens[-1] in LEGAL_SUFFIXES:
        tokens.pop()
    return " ".join(tokens).strip()


def load_keywords(path: str) -> list[str]:
    keywords: list[str] = []
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        keywords.append(line.lower())
    if not keywords:
        raise ValueError(f"Keyword file is empty: {path}")
    return keywords


def compile_boundary_pattern(keywords: list[str]) -> re.Pattern[str]:
    parts = []
    for keyword in sorted(set(keywords), key=len, reverse=True):
        # Treat multiword phrases flexibly so "machine learning" also matches
        # "machine-learning" in patent titles/abstracts.
        escaped = re.escape(keyword).replace(r"\ ", r"(?:[\s-]+)")
        parts.append(rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])")
    return re.compile("|".join(parts), flags=re.IGNORECASE)


def matched_keywords(text: str, pattern: re.Pattern[str]) -> str:
    normalized = {
        match.group(0).lower().replace("-", " ") for match in pattern.finditer(text or "")
    }
    return " | ".join(sorted(normalized))
