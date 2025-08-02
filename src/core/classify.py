import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer
from src.classification.utils import load_centroids

# Select device
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

# Load model and centroids
model = SentenceTransformer("all-MiniLM-L6-v2").to(device)
centroids = load_centroids("data/validation/centroids.json")
centroids = {label: centroid.to(device) for label, centroid in centroids.items()}

def classify_sentence(sentence: str) -> tuple:
    embedding = model.encode(sentence, convert_to_tensor=True).to(device)
    scores = {
        label: F.cosine_similarity(embedding, centroid, dim=0).item()
        for label, centroid in centroids.items()
    }
    best_label = max(scores, key=scores.get)
    return best_label, scores
