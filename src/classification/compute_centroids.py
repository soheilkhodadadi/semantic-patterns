# src/classification/compute_centroids.py

import pandas as pd
import torch
import os
import json
import ast  # safer than eval

# Paths
input_path = "data/validation/hand_labeled_ai_sentences_with_embeddings.csv"
output_path = "data/validation/centroids.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Load data
df = pd.read_csv(input_path)

# Convert embedding column from string to tensors
def safe_tensor(x):
    if isinstance(x, str):
        try:
            return torch.tensor(ast.literal_eval(x))
        except Exception:
            return None
    return None

df["embedding"] = df["embedding"].apply(safe_tensor)
df = df[df["embedding"].notnull()]  # Remove rows where embedding couldn't be parsed

# Compute centroids
centroids = {}
for label in df["label"].unique():
    embeddings = torch.stack(df[df["label"] == label]["embedding"].tolist())
    centroid = embeddings.mean(dim=0)
    centroids[label] = centroid.tolist()

# Save as JSON
with open(output_path, "w") as f:
    json.dump(centroids, f)

print(f"[✓] Saved centroids for {len(centroids)} classes to: {output_path}")
