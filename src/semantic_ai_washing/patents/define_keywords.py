"""
Defines a basic set of AI-related patent keywords and saves them to a text file.

Run: python src/patents/define_keywords.py
"""

import os

# Core AI-related keywords (used in patent titles, abstracts, or claims)
ai_keywords = [
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "neural network",
    "natural language processing",
    "AI",
    "ML",
    "computer vision",
    "reinforcement learning",
    "language model",
    "large language model",
    "generative AI",
]

# Output path
output_path = "data/metadata/patent_keywords.txt"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Save keywords to file
with open(output_path, "w") as f:
    for kw in ai_keywords:
        f.write(kw + "\n")

print(f"[✓] Saved {len(ai_keywords)} keywords to: {output_path}")
