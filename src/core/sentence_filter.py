# src/core/sentence_filter.py
"""
Core sentence filtering utilities for extracting AI-related sentences
from plain-text SEC filings.

Public API:
- load_keywords(path: str) -> list[str]
- segment_sentences(text: str) -> list[str]
- filter_ai_sentences(sentences: list[str], keywords: list[str]) -> list[str]
"""

from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List
import re

# --- Keyword loading ---------------------------------------------------------

def load_keywords(path: str) -> List[str]:
    """
    Load keywords/phrases (one per line) and return a normalized list.
    - Strips comments after '#'
    - Keeps phrases with spaces (quoted or not)
    - Deduplicates and lowercases
    """
    p = Path(path)
    if not p.exists():
        return []

    items: list[str] = []
    for raw in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        # remove trailing comments
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        # allow quoted phrases, but we ultimately store raw text
        if (line.startswith('"') and line.endswith('"')) or (line.startswith("'") and line.endswith("'")):
            line = line[1:-1].strip()
        items.append(line.lower())

    # dedupe while preserving order
    seen = set()
    out: list[str] = []
    for it in items:
        if it not in seen:
            seen.add(it)
            out.append(it)
    return out


# --- Sentence segmentation ---------------------------------------------------

@lru_cache(maxsize=1)
def _get_spacy():
    """Lazy import/load of spaCy. Falls back to a regex splitter if unavailable."""
    try:
        import spacy  # type: ignore
        try:
            return spacy.load("en_core_web_sm", disable=["ner", "tagger", "lemmatizer"])
        except Exception:
            # small fallback model if package name differs or not installed
            return spacy.blank("en")
    except Exception:
        return None


_SENT_END = re.compile(r"(?<=[\.\?!])\s+(?=[A-Z(])")


def segment_sentences(text: str) -> List[str]:
    """
    Split `text` into sentences.
    - Uses spaCy if available (with sentencizer), else regex fallback.
    - Normalizes whitespace and keeps non-empty sentences.
    """
    text = text.replace("\u00A0", " ").replace("\t", " ")
    text = re.sub(r"[ ]{2,}", " ", text)

    nlp = _get_spacy()
    if nlp is not None:
        # ensure the pipeline has a sentencizer
        if "sentencizer" not in nlp.pipe_names:
            try:
                nlp.add_pipe("sentencizer")
            except Exception:
                pass
        try:
            doc = nlp(text)
            sents = [s.text.strip() for s in doc.sents]
            return [s for s in sents if s]
        except Exception:
            pass

    # fallback
    parts = _SENT_END.split(text)
    return [p.strip() for p in parts if p and p.strip()]


# --- Post-processing --------------------------------------------------------

_PUNCTUATION_END = re.compile(r"[\.\?!]$")


def _should_skip_fragment(fragment: str) -> bool:
    """Return True if the fragment is just a page number or boilerplate."""
    stripped = fragment.strip()
    if not stripped:
        return True
    lowered = stripped.lower()
    return stripped.isdigit() or lowered == "table of contents"


def _is_incomplete(fragment: str) -> bool:
    """Detect fragments that likely need to be merged with the next line."""
    frag = fragment.strip()
    if not frag:
        return False
    if frag.endswith(";"):
        return True
    return _PUNCTUATION_END.search(frag) is None


def _starts_with_lower(fragment: str) -> bool:
    frag = fragment.lstrip()
    return bool(frag) and frag[0].islower()


def merge_sentence_fragments(sentences: List[str]) -> List[str]:
    """
    Merge sentence fragments produced by segmentation to handle page numbers and
    bullet/list continuations.

    - Skips standalone page numbers and "Table of Contents" boilerplate.
    - Merges fragments ending with semicolons or lacking sentence-ending
      punctuation when followed by a lowercase-starting continuation.
    - Normalizes capitalization and ensures a closing period if missing.
    """

    merged: list[str] = []
    idx = 0

    while idx < len(sentences):
        current = sentences[idx].strip()
        idx += 1

        if _should_skip_fragment(current):
            continue

        combined = current

        while _is_incomplete(combined):
            # Advance to the next non-skipped fragment
            while idx < len(sentences) and _should_skip_fragment(sentences[idx]):
                idx += 1

            if idx >= len(sentences):
                break

            nxt = sentences[idx].strip()

            if not _starts_with_lower(nxt):
                break

            # Consume and merge the continuation
            combined = combined.rstrip(" ;") + " " + nxt.lstrip()
            idx += 1

        combined = combined.strip()
        if combined and combined[0].islower():
            combined = combined[0].upper() + combined[1:]
        if combined and _PUNCTUATION_END.search(combined) is None:
            combined += "."

        if combined:
            merged.append(combined)

    return merged


# --- Matching ---------------------------------------------------------------

_WORD = r"[A-Za-z0-9_\-\.]+"
# Build a conservative token/phrase matcher. We allow:
#   - exact tokens (e.g., "GPT‑4", "ChatGPT", "Autopilot")
#   - multi-word phrases (e.g., "machine learning")
#   - flexible whitespace between words
def _compile_keyword_regex(keywords: Iterable[str]) -> re.Pattern:
    tokens: list[str] = []
    for kw in keywords:
        kw = kw.strip()
        if not kw:
            continue
        # Escape punctuation but keep spaces flexible
        parts = [re.escape(p) for p in kw.split()]
        if len(parts) == 1:
            # single token: use word-ish boundaries (don't require strict \b for hyphenated terms)
            pat = rf"(?<![A-Za-z0-9]){parts[0]}(?![A-Za-z0-9])"
        else:
            # multi token: allow 1+ whitespace between escaped pieces
            pat = r"\s+".join(parts)
        tokens.append(pat)

    if not tokens:
        # match nothing
        return re.compile(r"a^\Z")

    combined = "|".join(tokens)
    return re.compile(combined, flags=re.IGNORECASE)


def filter_ai_sentences(sentences: List[str], keywords: List[str]) -> List[str]:
    """
    Return only sentences that contain any of the provided `keywords`.
    Matching is done via a compiled regex that supports multi-word phrases.
    """
    if not sentences or not keywords:
        return []

    rx = _compile_keyword_regex(keywords)
    out: list[str] = []
    for s in sentences:
        # cheap negative filter: skip very short or number-only lines
        if len(s) < 4 or s.strip().isdigit():
            continue
        if rx.search(s):
            out.append(s.strip())
    return out