import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer
from src.classification.utils import load_centroids

# Load the SentenceBERT model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load the centroids
centroids = load_centroids("data/validation/centroids.json")

def classify_sentence(sentence: str) -> tuple:
    if not centroids:
        raise ValueError("Centroids are empty. Check if centroids.json is loaded properly.")

    # Encode the input sentence
    embedding = model.encode(sentence, convert_to_tensor=True)

    # Compute cosine similarity with each class centroid
    scores = {
        label: F.cosine_similarity(embedding, centroid, dim=0).item()
        for label, centroid in centroids.items()
    }

    if not scores:
        raise ValueError("No scores computed. Make sure centroids contain valid tensors.")

    # Pick the label with the highest similarity
    best_label, _ = max(scores.items(), key=lambda item: item[1])
    return best_label, scores
