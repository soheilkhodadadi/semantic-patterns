"""
Batch classifier for AI-related sentences using SentenceBERT and cosine similarity.

This script loops through all *_ai_sentences.txt files in data/processed/sec/,
classifies each sentence using the classify_sentence() function, and saves the 
results to corresponding *_classified.txt files.

Run: python src/classification/classify_all_ai_sentences.py
"""

import os
import sys

# Dynamically add the src/ folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.classify import classify_sentence

# Directory containing AI sentence files
ai_sentence_dir = "data/processed/sec"

# Loop through all *_ai_sentences.txt files
ai_files = [f for f in os.listdir(ai_sentence_dir) if f.endswith("_ai_sentences.txt")]
print(f"[✓] Found {len(ai_files)} AI sentence files.")

for filename in ai_files:
    input_path = os.path.join(ai_sentence_dir, filename)
    output_path = os.path.join(ai_sentence_dir, filename.replace("_ai_sentences.txt", "_classified.txt"))

    print(f"🔍 Classifying {filename} → {output_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        sentences = [line.strip() for line in f if line.strip()]

    outputs = []
    for sentence in sentences:
        try:
            label, scores = classify_sentence(sentence)
            line = f"{sentence} | Label: {label} | Scores: {scores}"
            outputs.append(line)
        except Exception as e:
            print(f"⚠️ Error classifying sentence: '{sentence[:60]}...': {e}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(outputs))

    print(f"[✓] Saved: {output_path}")
