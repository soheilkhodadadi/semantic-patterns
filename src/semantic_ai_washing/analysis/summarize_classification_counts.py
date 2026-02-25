"""
Summarize classification counts for each AI sentence file.
Outputs the label distribution for each firm-year.

Run: python src/analysis/summarize_classification_counts.py
"""

import os
from collections import Counter

ai_sentence_dir = "data/processed/sec"

print("\n📊 Classification Label Counts per File")
print("–" * 50)

for filename in os.listdir(ai_sentence_dir):
    if filename.endswith("_classified.txt"):
        path = os.path.join(ai_sentence_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            labels = [
                line.split(" | Label: ")[1].split(" |")[0] for line in f if " | Label: " in line
            ]
            counts = Counter(labels)
            print(f"{filename}: {dict(counts)}")
