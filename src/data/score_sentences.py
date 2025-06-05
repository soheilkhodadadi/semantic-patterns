import os
import spacy
from spacy.matcher import PhraseMatcher

# Load term lists
def load_terms(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

concrete_terms = load_terms("data/metadata/technical_terms/concrete_terms.txt")
vague_terms = load_terms("data/metadata/technical_terms/vague_terms.txt")

# Show loaded term lists
print("\n[DEBUG] Concrete terms:")
for term in concrete_terms:
    print(f" - {term} → {[t.text for t in term.split()]}")

print("\n[DEBUG] Vague terms:")
for term in vague_terms:
    print(f" - {term} → {[t.text for t in term.split()]}")

# Load AI-related sentences
input_path = "data/processed/sec/20241030_10-Q_edgar_data_1792789_0001628280-24-044312_ai_sentences.txt"
if not os.path.exists(input_path):
    raise FileNotFoundError(f"{input_path} not found. Run Phase 2 first.")

with open(input_path, "r", encoding="utf-8") as f:
    ai_sentences = [line.strip() for line in f if line.strip()]

# Initialize SpaCy and PhraseMatcher
nlp = spacy.load("en_core_web_lg")
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

# Use nlp.make_doc to preserve tokenization
concrete_patterns = [nlp.make_doc(term) for term in concrete_terms]
vague_patterns = [nlp.make_doc(term) for term in vague_terms]
matcher.add("CONCRETE", concrete_patterns)
matcher.add("VAGUE", vague_patterns)

# Score sentences
scored_sentences = []
for sentence in ai_sentences:
    doc = nlp(sentence)
    matches = matcher(doc)

    print(f"\n[Sentence] {sentence}")
    print(f"[Tokens] {[token.text for token in doc]}")

    match_debug = []
    concrete_count = 0
    vague_count = 0

    for match_id, start, end in matches:
        label = nlp.vocab.strings[match_id]
        span = doc[start:end]
        match_debug.append(f"{label}: '{span.text}'")
        if label == "CONCRETE":
            concrete_count += 1
        elif label == "VAGUE":
            vague_count += 1

    if match_debug:
        print("[Matches]")
        for m in match_debug:
            print(f"  → {m}")
    else:
        print("→ No matches found.")

    total = concrete_count + vague_count
    score = concrete_count / total if total > 0 else 0

    scored_sentences.append(
        f"{sentence} | Score: {score:.2f} (Concrete: {concrete_count}, Vague: {vague_count})"
    )

# Save results
base_name = os.path.basename(input_path).replace("_ai_sentences.txt", "_scored.txt")
output_path = os.path.join("data/processed/sec", base_name)
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(scored_sentences))

print(f"\n[✓] Saved {len(scored_sentences)} scored sentences to: {output_path}")
