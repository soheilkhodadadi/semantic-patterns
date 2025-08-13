# src/classification/compute_centroids_mpnet.py
"""Compute label centroids from MPNet embeddings.

Reads the CSV produced by `embed_labeled_sentences_mpnet.py`, reconstructs
embeddings, filters invalid rows, and writes per-label mean vectors.
"""
import os
import json
import ast
import torch
import pandas as pd

IN = "data/validation/hand_labeled_ai_sentences_with_embeddings_mpnet.csv"
OUT = "data/validation/centroids_mpnet.json"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# Load embeddings CSV
df = pd.read_csv(IN)

# Convert stringified list -> tensor
def to_tensor(x):
    try:
        return torch.tensor(ast.literal_eval(x), dtype=torch.float32)
    except Exception:
        return None

# Apply conversion (pandas typing can complain; map keeps scalar -> scalar)
df["embedding"] = df["embedding"].map(to_tensor)  # type: ignore[arg-type]

# Keep rows with both embedding + label
df = df[df["embedding"].notnull() & df["label"].notnull()]

centroids = {}
for label, grp in df.groupby("label"):
    emb = torch.stack(grp["embedding"].tolist())
    centroids[label] = emb.mean(0).tolist()

with open(OUT, "w") as f:
    json.dump(centroids, f)
print(f"[✓] Wrote centroids (MPNet) → {OUT}")
