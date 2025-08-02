import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer
from src.classification.utils import load_centroids

# Select device (e.g., MPS for Apple Silicon or fallback to CPU)
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

# Load model and centroids
model = SentenceTransformer("all-MiniLM-L6-v2").to(device)
centroids = load_centroids("data/validation/centroids.json")
centroids = {label: tensor.to(device) for label, tensor in centroids.items()}

def classify_sentence(sentence: str) -> tuple[str, dict[str, float]]:
    """
    Classify a sentence as Actionable, Speculative, or Irrelevant using cosine similarity
    against precomputed SentenceBERT centroids.

    Args:
        sentence (str): The input sentence to classify.

    Returns:
        tuple[str, dict[str, float]]: A tuple containing the predicted label and a dictionary 
        of similarity scores for each class.

    Raises:
        ValueError: If centroids are empty or scores could not be computed.
    """
    if not centroids:
        raise ValueError("Centroids are empty. Check if centroids.json is loaded correctly.")

    embedding = model.encode(sentence, convert_to_tensor=True).to(device)

    scores = {
        label: F.cosine_similarity(embedding, centroid, dim=0).item()
        for label, centroid in centroids.items()
    }

    if not scores:
        raise ValueError("No scores computed. Centroids may be invalid.")

    best_label, _ = max(scores.items(), key=lambda item: item[1])
    return best_label, scores
