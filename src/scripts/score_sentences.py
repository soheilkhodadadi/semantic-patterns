import os
from core.sentence_scorer import load_terms, init_matcher, score_sentence

input_dir = "data/processed/sec"
output_dir = "data/processed/scored"
os.makedirs(output_dir, exist_ok=True)

concrete_terms = load_terms("data/metadata/technical_terms/concrete_terms.txt")
vague_terms = load_terms("data/metadata/technical_terms/vague_terms.txt")
matcher = init_matcher(concrete_terms, vague_terms)

for filename in os.listdir(input_dir):
    if filename.endswith("_ai_sentences.txt"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename.replace("_ai_sentences.txt", "_scored.txt"))

        with open(input_path, "r", encoding="utf-8") as f:
            ai_sentences = [line.strip() for line in f if line.strip()]

        scored = [score_sentence(sent, matcher) for sent in ai_sentences]

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(scored))

        print(f"[✓] Scored {len(scored)} sentences → {output_path}")
