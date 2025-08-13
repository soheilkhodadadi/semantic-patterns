import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer
from classification.utils import load_centroids

# Near top-level config (toggle here for different embedding backbones / centroids)
MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"  # change back to MiniLM if needed
CENTROIDS_PATH = "data/validation/centroids_mpnet.json"

# Select device (e.g., MPS for Apple Silicon or fallback to CPU)
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

# Load model and centroids (single instantiation to avoid device churn)
model = SentenceTransformer(MODEL_NAME).to(device)
centroids = load_centroids(CENTROIDS_PATH)
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
