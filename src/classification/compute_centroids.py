# src/classification/compute_centroids.py

import pandas as pd
import torch
import os
import json
import ast

# Paths
input_path = "data/validation/hand_labeled_ai_sentences_with_embeddings.csv"
output_path = "data/validation/centroids.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Load DataFrame
df = pd.read_csv(input_path)

# Safe conversion from string to tensor
def safe_tensor(x):
    if isinstance(x, str) and x.startswith("[") and x.endswith("]"):
        try:
            vec = ast.literal_eval(x)
            if isinstance(vec, list) and all(isinstance(n, float) for n in vec) and len(vec) == 384:
                return torch.tensor(vec)
        except Exception:
            pass
    return None

# Apply safe conversion
df["embedding"] = df["embedding"].apply(safe_tensor)  # type: ignore

# Drop malformed entries
initial_len = len(df)
df = df[df["embedding"].notnull()]
dropped = initial_len - len(df)
print(f"[i] Dropped {dropped} rows with invalid or missing embeddings.")

# Compute centroids
centroids = {}
for label in df["label"].unique():
    subset = df[df["label"] == label]
    embeddings = torch.stack(subset["embedding"].tolist())
    centroid = embeddings.mean(dim=0)
    centroids[label] = centroid.tolist()

# Save centroids
with open(output_path, "w") as f:
    json.dump(centroids, f)

print(f"[✓] Saved centroids for {len(centroids)} classes to: {output_path}")
