import spacy
from spacy.matcher import PhraseMatcher
from typing import List

nlp = spacy.load("en_core_web_lg")
nlp.max_length = 2_000_000

fuzzy_vague_followups = {
    "solutions",
    "tools",
    "applications",
    "platform",
    "capabilities",
    "integration",
    "functionality",
    "features",
    "systems",
    "products",
}


def load_terms(file_path: str) -> List[str]:
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def init_matcher(concrete_terms: List[str], vague_terms: List[str]) -> PhraseMatcher:
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    matcher.add("CONCRETE", [nlp.make_doc(term) for term in concrete_terms])
    matcher.add("VAGUE", [nlp.make_doc(term) for term in vague_terms])
    return matcher


def score_sentence(sentence: str, matcher: PhraseMatcher) -> str:
    doc = nlp(sentence)
    matches = matcher(doc)

    concrete_count = 0
    vague_count = 0
    fuzzy_vague_hits = 0

    for match_id, start, end in matches:
        label = nlp.vocab.strings[match_id]
        if label == "CONCRETE":
            concrete_count += 1
        elif label == "VAGUE":
            vague_count += 1

    for i, token in enumerate(doc):
        if token.text.lower() == "ai":
            window = [doc[j].text.lower() for j in range(i + 1, min(i + 5, len(doc)))]
            if any(word in fuzzy_vague_followups for word in window):
                fuzzy_vague_hits += 1

    vague_count += fuzzy_vague_hits
    total = concrete_count + vague_count
    score = concrete_count / total if total > 0 else 0

    return f"{sentence} | Score: {score:.2f} (Concrete: {concrete_count}, Vague: {vague_count}, Fuzzy Vague Hits: {fuzzy_vague_hits})"
