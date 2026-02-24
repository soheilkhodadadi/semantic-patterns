# src/core/sentence_filter.py
"""
Core sentence filtering utilities for extracting AI-related sentences
from plain-text SEC filings.

Public API:
- load_keywords(path: str) -> list[str]
- segment_sentences(text: str) -> list[str]
- merge_page_fragments(sentences: list[str], raw_text: str | None = None) -> list[str]
- merge_sentence_fragments(sentences: list[str]) -> list[str]
- filter_ai_sentences(sentences: list[str], keywords: list[str]) -> list[str]
"""

from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List, Optional
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
        if (line.startswith('"') and line.endswith('"')) or (
            line.startswith("'") and line.endswith("'")
        ):
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
    text = text.replace("\u00a0", " ").replace("\t", " ")
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
_PAGE_MARKER = re.compile(r"[\-\u2013\u2014]\s*\d+\s*[\-\u2013\u2014]")
_PAGE_MARKER_LINE = re.compile(r"^\s*[\-\u2013\u2014]\s*\d+\s*[\-\u2013\u2014]\s*$")


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


def _starts_with_upper(fragment: str) -> bool:
    frag = fragment.lstrip()
    return bool(frag) and frag[0].isupper()


def _normalize_sentence(fragment: str) -> str:
    cleaned = re.sub(r"\s+", " ", fragment).strip()
    cleaned = _PAGE_MARKER.sub(" ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ;,-")
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]
    if cleaned and _PUNCTUATION_END.search(cleaned) is None:
        cleaned += "."
    return cleaned


def _is_page_fragment(fragment: str) -> bool:
    return bool(_PAGE_MARKER.search(fragment))


def _match_key(fragment: str) -> str:
    cleaned = _PAGE_MARKER.sub(" ", fragment)
    cleaned = re.sub(r"\s+", " ", cleaned).strip().lower()
    return cleaned.strip(" .?!;,-")


def _is_incomplete_page_fragment(fragment: str) -> bool:
    frag = fragment.strip()
    if not frag:
        return False
    if _PAGE_MARKER_LINE.match(frag):
        return True
    return (not _starts_with_upper(frag)) or (_PUNCTUATION_END.search(frag) is None)


def _reconstruct_with_raw_context(
    raw_text: str, fragment: str, context_chars: int = 180
) -> Optional[str]:
    """
    Rebuild a broken sentence around `fragment` using nearby raw text.
    Returns None if the fragment cannot be found robustly.
    """
    if not raw_text or not fragment.strip():
        return None

    # Try exact match first.
    start = raw_text.find(fragment)
    end = start + len(fragment) if start >= 0 else -1

    if start < 0:
        # Fallback: match flexible whitespace around non-empty tokens.
        parts = [re.escape(tok) for tok in fragment.split() if tok]
        if not parts:
            return None
        rx = re.compile(r"\s+".join(parts), flags=re.DOTALL)
        m = rx.search(raw_text)
        if not m:
            return None
        start, end = m.span()

    left = max(0, start - context_chars)
    right = min(len(raw_text), end + context_chars)
    local = raw_text[left:right]
    local_start = start - left
    local_end = end - left

    sentence_left = local.rfind(".", 0, local_start)
    sentence_q = local.rfind("?", 0, local_start)
    sentence_bang = local.rfind("!", 0, local_start)
    sentence_start = max(sentence_left, sentence_q, sentence_bang)
    sentence_start = sentence_start + 1 if sentence_start >= 0 else 0

    candidates = [
        pos
        for pos in (
            local.find(".", local_end),
            local.find("?", local_end),
            local.find("!", local_end),
        )
        if pos >= 0
    ]
    sentence_end = min(candidates) + 1 if candidates else len(local)

    rebuilt = local[sentence_start:sentence_end]
    rebuilt = _PAGE_MARKER.sub(" ", rebuilt)
    rebuilt = re.sub(r"\s+", " ", rebuilt).strip()
    return rebuilt or None


def merge_page_fragments(
    sentences: List[str], raw_text: Optional[str] = None, context_chars: int = 180
) -> List[str]:
    """
    Merge fragments around page markers like "- 12 -" or "— 12 —".

    A sentence is treated as an incomplete page fragment if it contains a page
    marker token and either does not start with a capital letter or lacks
    sentence-ending punctuation.

    If `raw_text` is provided, nearby characters are used to reconstruct a more
    faithful full sentence. Otherwise, neighboring sentence fragments are used.
    """
    out: list[str] = []
    idx = 0

    while idx < len(sentences):
        current = sentences[idx].strip()
        if not current:
            idx += 1
            continue

        if not (_is_page_fragment(current) and _is_incomplete_page_fragment(current)):
            out.append(current)
            idx += 1
            continue

        rebuilt = (
            _reconstruct_with_raw_context(raw_text, current, context_chars) if raw_text else None
        )

        used_next = False
        if rebuilt is not None:
            rebuilt_key = _match_key(rebuilt)
            if out and _match_key(out[-1]) and _match_key(out[-1]) in rebuilt_key:
                out.pop()
            if idx + 1 < len(sentences):
                next_fragment = sentences[idx + 1].strip()
                next_key = _match_key(next_fragment)
                used_next = bool(next_key and next_key in rebuilt_key)
        else:
            prev = out.pop() if out else ""
            nxt = ""
            if idx + 1 < len(sentences):
                nxt = sentences[idx + 1].strip()
                used_next = bool(nxt)
            center = _PAGE_MARKER.sub(" ", current).strip()
            rebuilt = " ".join(part for part in (prev, center, nxt) if part)

        normalized = _normalize_sentence(rebuilt)
        if normalized:
            out.append(normalized)

        idx += 2 if used_next else 1

    return out


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

        combined = _normalize_sentence(combined)

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
