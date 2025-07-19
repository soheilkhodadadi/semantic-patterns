import os
from core.sentence_filter import segment_sentences, load_keywords, filter_ai_sentences

input_dir = "data/external"
output_dir = "data/processed/sec"
keyword_path = "data/metadata/ai_keywords.txt"

os.makedirs(output_dir, exist_ok=True)
keywords = load_keywords(keyword_path)

for filename in os.listdir(input_dir):
    if filename.endswith(".txt"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename.replace(".txt", "_ai_sentences.txt"))

        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()

        sentences = segment_sentences(text)
        ai_sentences = filter_ai_sentences(sentences, keywords)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(ai_sentences))

        print(f"[✓] Saved {len(ai_sentences)} AI-related sentences to: {output_path}")
