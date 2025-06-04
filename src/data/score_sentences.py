import os

# Step 1: Load concrete and vague AI terms
def load_terms(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]

concrete_terms = load_terms("data/metadata/technical_terms/concrete_terms.txt")
vague_terms = load_terms("data/metadata/technical_terms/vague_terms.txt")

# Step 2: Load AI-related sentences
input_path = "data/interim/ai_sentences.txt"
if not os.path.exists(input_path):
    raise FileNotFoundError(f"{input_path} not found. Run Phase 2 first.")

with open(input_path, "r", encoding="utf-8") as f:
    ai_sentences = [line.strip() for line in f if line.strip()]

# Step 3: Score each sentence based on term matches
scored_sentences = []
for sentence in ai_sentences:
    lower_sentence = sentence.lower()
    concrete_count = sum(1 for term in concrete_terms if term in lower_sentence)
    vague_count = sum(1 for term in vague_terms if term in lower_sentence)

    total = concrete_count + vague_count
    score = concrete_count / total if total > 0 else 0

    scored_sentences.append(
        f"{sentence} | Score: {score:.2f} (Concrete: {concrete_count}, Vague: {vague_count})"
    )

# Step 4: Save results
output_path = "data/processed/scored_sentences.txt"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(scored_sentences))

print(f"[✓] Saved {len(scored_sentences)} scored sentences to {output_path}")
