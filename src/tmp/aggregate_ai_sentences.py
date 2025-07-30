# File: src/tmp/aggregate_ai_sentences.py

import os

input_dir = "data/processed/sec"  # where *_ai_sentences.txt are located
output_file = "data/validation/collected_ai_sentences.txt"
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Collect all *_ai_sentences.txt files
collected_sentences = []
for filename in os.listdir(input_dir):
    if filename.endswith("_ai_sentences.txt"):
        with open(os.path.join(input_dir, filename), "r", encoding="utf-8") as f:
            collected_sentences.extend([line.strip() for line in f if line.strip()])

# Save to a single file
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(collected_sentences))

print(f"[✓] Collected {len(collected_sentences)} AI-related sentences into {output_file}")
