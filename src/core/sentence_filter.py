# src/core/sentence_filter.py
import re
from typing import List, Iterable, Pattern

# --- spaCy load with graceful fallback ---------------------------------------
try:
    import spacy  # type: ignore
    try:
        nlp = spacy.load("en_core_web_lg")
    except Exception:
        try:
            nlp = spacy.load("en_core_web_md")
        except Exception:
            nlp = spacy.load("en_core_web_sm")
    nlp.max_length = 2_000_000
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        "spaCy English model is not installed. Run one of:\n"
        "  python -m spacy download en_core_web_lg\n"
        "  python -m spacy download en_core_web_md\n"
        "  python -m spacy download en_core_web_sm\n"
        f"Original error: {e}"
    )

def segment_sentences(text: str) -> List[str]:
    """
    Split raw filing text into sentences using spaCy, trimming whitespace and dropping empties.
    """
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if sent.text and sent.text.strip()]

def load_keywords(filepath: str) -> List[str]:
    """
    Load one keyword/phrase per line from a UTF-8 text file.
    Empty lines are ignored. Whitespace is stripped.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# --- Heuristics ---------------------------------------------------------------

def is_meaningful(sentence: str, min_words: int = 8) -> bool:
    """
    Heuristic to drop obvious junk such as headings, page numbers, and very short lines.
    """
    s = sentence.strip()
    if not s:
        return False
    # length/shape
    if len(s.split()) < min_words:
        return False
    # all caps blocks often are headings
    if s.isupper():
        return False
    low = s.lower()
    if "table of contents" in low:
        return False
    # "item 1", "item 1a", etc. (common in 10-K headings)
    if re.match(r"^item\\s+\\d+[a-z]?(\\.|:|\\s|$)", low):
        return False
    # bare numbers or page marks
    if re.match(r"^\\s*\\d+\\s*$", s):
        return False
    # lines that are mostly punctuation
    if re.match(r"^[\\W_]+$", s):
        return False
    return True

# --- Keyword compilation & matching ------------------------------------------

def compile_keyword_patterns(keywords: Iterable[str]) -> List[Pattern]:
    """
    Precompile case-insensitive regex patterns with word boundaries for each keyword/phrase.
    Example: 'natural language processing' → r'\\bnatural\\ language\\ processing\\b' (case-insensitive)
    """
    patterns: List[Pattern] = []
    for kw in keywords:
        if not kw:
            continue
        # Use word boundaries around the whole phrase; escape inner punctuation safely
        patt = re.compile(rf"\\b{re.escape(kw)}\\b", flags=re.IGNORECASE)
        patterns.append(patt)
    return patterns

def sentence_has_any_pattern(sentence: str, patterns: List[Pattern]) -> bool:
    """
    True if the sentence matches any of the compiled keyword patterns.
    """
    for p in patterns:
        if p.search(sentence):
            return True
    return False

def filter_ai_sentences(sentences: List[str], keywords: List[str]) -> List[str]:
    """
    Keep sentences that match at least one keyword/phrase and pass the 'meaningful' heuristic.
    Deduplicates while preserving original order.
    """
    patterns = compile_keyword_patterns(keywords)

    ai_sentences = []
    for s in sentences:
        if not sentence_has_any_pattern(s, patterns):
            continue
        if not is_meaningful(s):
            continue
        ai_sentences.append(s)

    # Deduplicate while preserving order
    seen = set()
    unique_sentences = []
    for s in ai_sentences:
        if s not in seen:
            unique_sentences.append(s)
            seen.add(s)

    return unique_sentences