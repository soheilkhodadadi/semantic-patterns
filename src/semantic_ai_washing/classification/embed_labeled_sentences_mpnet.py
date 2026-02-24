# src/classification/embed_labeled_sentences_mpnet.py
"""Embed labeled sentences using the stronger MPNet model.

This script mirrors `embed_labeled_sentences.py` (MiniLM baseline) but switches
to the `sentence-transformers/all-mpnet-base-v2` model and uses the original
cleaned labels CSV (non-revised) as requested.
"""

import os
import pandas as pd
from sentence_transformers import SentenceTransformer

IN = "data/validation/hand_labeled_ai_sentences_labeled_cleaned.csv"
OUT = "data/validation/hand_labeled_ai_sentences_with_embeddings_mpnet.csv"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# Load labeled sentences
df = pd.read_csv(IN)

# Load MPNet model (stronger model check)
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Encode each sentence (note: could batch for speed; kept simple for parity)
df["embedding"] = df["sentence"].apply(lambda s: model.encode(s, convert_to_tensor=True).tolist())

# Persist
df.to_csv(OUT, index=False)
print(f"[✓] Saved MPNet embeddings → {OUT}")
