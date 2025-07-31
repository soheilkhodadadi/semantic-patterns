import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer
from .utils import load_centroids

"""
Classify a sentence using cosine similarity to precomputed centroids.

Requires:
- Revised centroids file from data/validation/centroids_revised.json
- SentenceBERT model (all-MiniLM-L6-v2)
"""

# Load the SentenceBERT model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Device selection for Apple Silicon (MPS) or CPU fallback
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

# Load the revised centroids
centroids = load_centroids("data/validation/centroids_revised.json")
centroids = {label: tensor.to(device) for label, tensor in centroids.items()}

def classify_sentence(sentence: str) -> tuple:
    """
    Classify a sentence as Actionable, Speculative, or Irrelevant
    using cosine similarity to centroids.
    """
    if not centroids:
        raise ValueError("Centroids are empty. Check if centroids_revised.json is loaded properly.")

    embedding = model.encode(sentence, convert_to_tensor=True).to(device)

    scores = {
        label: F.cosine_similarity(embedding, centroid, dim=0).item()
        for label, centroid in centroids.items()
    }

    if not scores:
        raise ValueError("No scores computed. Check if embeddings and centroids are valid.")

    best_label, _ = max(scores.items(), key=lambda item: item[1])
    return best_label, scores
