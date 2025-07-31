# src/classification/embed_labeled_sentences.py

import pandas as pd
from sentence_transformers import SentenceTransformer
import os

# Paths — updated to use the relabeled file
input_path = "data/validation/hand_labeled_ai_sentences_labeled_cleaned_revised.csv"
output_path = "data/validation/hand_labeled_ai_sentences_with_embeddings_revised.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Load data
df = pd.read_csv(input_path)

# Load SentenceBERT model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Encode sentences into embeddings
df["embedding"] = df["sentence"].apply(lambda x: model.encode(x, convert_to_tensor=True).tolist())

# Save result
df.to_csv(output_path, index=False)
print(f"[✓] Saved {len(df)} embedded sentences to: {output_path}")
