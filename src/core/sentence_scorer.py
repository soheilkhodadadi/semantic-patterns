import os
import spacy
from spacy.matcher import PhraseMatcher

# Load term lists
def load_terms(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

concrete_terms = load_terms("data/metadata/technical_terms/concrete_terms.txt")
vague_terms = load_terms("data/metadata/technical_terms/vague_terms.txt")

# Vague suffixes for fuzzy AI match (e.g., "AI tools", "AI features")
fuzzy_vague_followups = {
    "solutions", "tools", "applications", "platform", "capabilities", "integration",
    "functionality", "features", "systems", "products"
}

# Load AI-related sentences
input_path = "data/processed/sec/20241030_10-Q_edgar_data_1792789_0001628280-24-044312_ai_sentences.txt"
if not os.path.exists(input_path):
    raise FileNotFoundError(f"{input_path} not found. Run Phase 2 first.")

with open(input_path, "r", encoding="utf-8") as f:
    ai_sentences = [line.strip() for line in f if line.strip()]

# Initialize SpaCy and PhraseMatcher
nlp = spacy.load("en_core_web_lg")
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
matcher.add("CONCRETE", [nlp.make_doc(term) for term in concrete_terms])
matcher.add("VAGUE", [nlp.make_doc(term) for term in vague_terms])

# Score sentences
scored_sentences = []
for sentence in ai_sentences:
    doc = nlp(sentence)
    matches = matcher(doc)

    concrete_count = 0
    vague_count = 0
    fuzzy_vague_hits = 0

    # Phrase matches
    for match_id, start, end in matches:
        label = nlp.vocab.strings[match_id]
        if label == "CONCRETE":
            concrete_count += 1
        elif label == "VAGUE":
            vague_count += 1

    # Fuzzy logic: check for "AI" followed by one of the vague follow-up words
    for i, token in enumerate(doc):
        if token.text.lower() == "ai":
            # Look ahead up to 4 tokens
            window = [doc[j].text.lower() for j in range(i+1, min(i+5, len(doc)))]
            if any(word in fuzzy_vague_followups for word in window):
                fuzzy_vague_hits += 1

    vague_count += fuzzy_vague_hits

    total = concrete_count + vague_count
    score = concrete_count / total if total > 0 else 0

    scored_sentences.append(
        f"{sentence} | Score: {score:.2f} (Concrete: {concrete_count}, Vague: {vague_count}, Fuzzy Vague Hits: {fuzzy_vague_hits})"
    )

# Save results
base_name = os.path.basename(input_path).replace("_ai_sentences.txt", "_scored.txt")
output_path = os.path.join("data/processed/sec", base_name)
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(scored_sentences))

print(f"\n[✓] Scored {len(scored_sentences)} sentences. Saved to: {output_path}")
