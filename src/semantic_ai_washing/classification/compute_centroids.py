import pandas as pd
import torch
import os
import json
import ast

# Paths — updated to use revised file
input_path = "data/validation/hand_labeled_ai_sentences_with_embeddings_revised.csv"
output_path = "data/validation/centroids_revised.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Load data
df = pd.read_csv(input_path)


# Safe conversion from string to tensor
def safe_tensor(x):
    if isinstance(x, str) and x.startswith("[") and x.endswith("]"):
        try:
            vec = ast.literal_eval(x)
            if (
                isinstance(vec, list)
                and all(isinstance(n, float) for n in vec)
                and len(vec) == 384
            ):
                return torch.tensor(vec)
        except Exception:
            pass
    return None


# Apply safe conversion
df["embedding"] = df["embedding"].apply(safe_tensor)  # type: ignore
df = df[df["embedding"].notnull()]

# Compute centroids per label
centroids = {}
for label in df["label"].unique():
    vectors = torch.stack(df[df["label"] == label]["embedding"].tolist())
    centroid = vectors.mean(dim=0)
    centroids[label] = centroid.tolist()

# Save to JSON
with open(output_path, "w") as f:
    json.dump(centroids, f)

print(f"[✓] Computed centroids for {len(centroids)} classes and saved to: {output_path}")
