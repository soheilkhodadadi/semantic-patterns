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

def filter_ai_sentences(sentences: List[str], keywords: List[str]) -> List[str]:
    ai_sentences = [
        sentence for sentence in sentences
        if any(re.search(rf"\b{re.escape(keyword)}\b", sentence, re.IGNORECASE) for keyword in keywords)
    ]
    return ai_sentences
