import re
import spacy
from typing import List

nlp = spacy.load("en_core_web_lg")
nlp.max_length = 2_000_000

def segment_sentences(text: str) -> List[str]:
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]

def load_keywords(filepath: str) -> List[str]:
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def is_meaningful(sentence: str) -> bool:
    if len(sentence.split()) < 8:
        return False
    if sentence.isupper():
        return False
    if "table of contents" in sentence.lower():
        return False
    if re.match(r'^\d+$', sentence.strip()):
        return False
    return True

def filter_ai_sentences(sentences: List[str], keywords: List[str]) -> List[str]:
    ai_sentences = [
        sentence for sentence in sentences
        if any(re.search(rf"\b{re.escape(keyword)}\b", sentence, re.IGNORECASE) for keyword in keywords)
    ]

    # Filter out headers, page numbers, junk
    ai_sentences = [s for s in ai_sentences if is_meaningful(s)]

    # Deduplicate while preserving order
    seen = set()
    unique_sentences = []
    for s in ai_sentences:
        if s not in seen:
            unique_sentences.append(s)
            seen.add(s)

    return unique_sentences
