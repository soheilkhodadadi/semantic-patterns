"""
Spot-check random sentences from classified files to manually evaluate accuracy.

Run: python src/tests/spot_check_classifications.py
"""

import os
import random

ai_sentence_dir = "data/processed/sec"
num_files = 3
samples_per_file = 5

# Grab a few random _classified.txt files
classified_files = [f for f in os.listdir(ai_sentence_dir) if f.endswith("_classified.txt")]
selected_files = random.sample(classified_files, min(len(classified_files), num_files))

print(f"🔍 Sampling {samples_per_file} sentences from each of {len(selected_files)} files...\n")

for filename in selected_files:
    path = os.path.join(ai_sentence_dir, filename)
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
        sample = random.sample(lines, min(samples_per_file, len(lines)))

    print(f"\n📄 File: {filename}")
    print("–" * 60)
    for line in sample:
        print("🧾", line)
    print("–" * 60)
