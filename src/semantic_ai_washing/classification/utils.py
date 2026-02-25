# src/classification/utils.py

import json
import torch


def load_centroids(path="data/validation/centroids.json"):
    with open(path, "r") as f:
        data = json.load(f)
    return {label: torch.tensor(vec) for label, vec in data.items()}
