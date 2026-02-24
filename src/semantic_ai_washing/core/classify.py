import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer
from semantic_ai_washing.classification.utils import load_centroids
import re
from typing import Tuple, Dict

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

# -----------------------------
# Two-stage + rule-assisted classifier (mirrors evaluate script)
# -----------------------------

# Heuristic patterns (kept lightweight; mirrored from evaluator)
ANY_AI = re.compile(r"\b(ai|artificial intelligence|machine learning|ml)\b", re.I)
FOCUS_ON_AI = re.compile(r"\bfocus(?:ed|es|ing)?\s+on\s+.*\b(ai|artificial intelligence)\b", re.I)
FUTURE_FEATURES = re.compile(r"\b(future|next\s+year|plan to|planning to|intend(?:s|ed)? to)\b.*\b(feature|service|module|product|capability|capabilities)\b", re.I)
INTEND_FOCUS = re.compile(r"\bintend(?:s|ed)?\s+to\s+focus\s+on\b", re.I)
GLOBAL_SUBJECT_LAWS = re.compile(r"^global operations are subject to (?:complex(?:\s*(?:and|,)?\s*changing)?|changing) laws and regulations", re.I)
LAWS_LIST_INTRO = re.compile(r"^(these|our) laws and regulations (involve|include)", re.I)
INFRASTRUCTURE = re.compile(r"\b(ai|artificial intelligence)\s+infrastructure\b", re.I)
INFRASTRUCTURE_BROAD = re.compile(r"\b(ai|artificial intelligence)\s+infrastructure\s+.*\bsuch as\b.*\b(gpu|gpus|graphics processing units|accelerators)\b", re.I)
APPLY_LEARNINGS = re.compile(r"applying\s+.*\s+learnings\b", re.I)
FUTURE_BASED_ON_AI = re.compile(r"\bfuture\b.*?(features|services).*?\bbased\s+on\b.*?(ai|artificial intelligence)\b", re.I)
INNOVATING_BUILD = re.compile(r"\binnovating\s+in\s+(ai|artificial intelligence)(?:\s+technologies)?\b.*?\bto\s+build\b", re.I)
OFFERING_ML = re.compile(r"\boffers? (?:a )?broad set of .* including .* (machine learning|ml)\b", re.I)
PROVIDES_ML = re.compile(r"\b(provides|offer(?:s|ing)?)\b.*\b(machine learning|ml)\b", re.I)
COMPLEX_ESTIMATE = re.compile(r"\brely upon? .* (techniques|algorithms|models).*(seek|seeks|aim) to estimate\b", re.I)
PREVENT_DELIVER = re.compile(r"\b(prevent\s+us\s+from\s+delivering|prevent\s+us\s+from\s+providing)\b", re.I)
USER_DIMINISH = re.compile(r"\b(user experience is diminished|affect the user experience)\b", re.I)
DECREASED_ENGAGEMENT = re.compile(r"\bdecreased\s+engagement\b.*\b(internet\s+shutdowns|taxes\s+imposed\s+on\s+the\s+use\s+of\s+social\s+media)\b", re.I)

ACTION_VERBS = re.compile(r"\b(launch|deploy|deployed|operate|operat(?:ing|es)|run|running|build|built|apply|applies|applied|recommend|recommend(?:ing|s)|develop|developed|developing|deliver|delivering|improve|improving|optimiz(?:e|es|ing)|implement|implemented|implementing|use|using|serve|serving|support|supporting)\b", re.I)
MODALS = re.compile(r"\b(may|might|could|plan to|planning to|intend(?:s|ed)? to|aim to|expect to|will)\b", re.I)

# Core centroid scorer used by both paths

def _centroid_scores(text: str) -> Dict[str, float]:
    emb = model.encode(text, convert_to_tensor=True).to(device)
    return {label: F.cosine_similarity(emb, c, dim=0).item() for label, c in centroids.items()}


def adjust_scores_v2(text: str, s: Dict[str, float]) -> Dict[str, float]:
    # Law/regulation long list → Irrelevant; global-law intro handled elsewhere
    if LAWS_LIST_INTRO.search(text):
        s["Irrelevant"] = s.get("Irrelevant", 0.0) + 0.15
        s["Speculative"] = max(0.0, s.get("Speculative", 0.0) - 0.08)
    # Offerings mentioning ML
    if OFFERING_ML.search(text) or PROVIDES_ML.search(text):
        s["Actionable"] = s.get("Actionable", 0.0) + 0.12
    # Estimation/methodology phrasing
    if COMPLEX_ESTIMATE.search(text):
        s["Speculative"] = s.get("Speculative", 0.0) + 0.12
    # Future features/services shouldn’t look actionable
    if FUTURE_FEATURES.search(text):
        s["Actionable"] = max(0.0, s.get("Actionable", 0.0) - 0.06)
    # Applying … learnings → non‑deployed
    if APPLY_LEARNINGS.search(text):
        s["Irrelevant"] = s.get("Irrelevant", 0.0) + 0.1
        s["Speculative"] = s.get("Speculative", 0.0) + 0.05
        s["Actionable"] = max(0.0, s.get("Actionable", 0.0) - 0.08)
    # Ops‑risk phrasing → actionable nudge
    if PREVENT_DELIVER.search(text) or USER_DIMINISH.search(text):
        s["Actionable"] = s.get("Actionable", 0.0) + 0.06
    # Investment laundry lists → speculative bias
    if re.search(r"continue\s+to\s+invest\s+in\s+new\s+and\s+unproven\s+technologies,?\s+including\s+(ai|artificial intelligence)", text, re.I):
        s["Speculative"] = s.get("Speculative", 0.0) + 0.12
        s["Irrelevant"] = max(0.0, s.get("Irrelevant", 0.0) - 0.06)
    # Future … based on AI → Irrelevant preference
    if FUTURE_BASED_ON_AI.search(text):
        s["Irrelevant"] = s.get("Irrelevant", 0.0) + 0.12
        s["Actionable"] = max(0.0, s.get("Actionable", 0.0) - 0.06)
    # Developing and deploying AI → actionable
    if re.search(r"develop(?:ing)?\s+and\s+deploy(?:ing)?\s+ai", text, re.I):
        s["Actionable"] = s.get("Actionable", 0.0) + 0.1
    return s


def is_irrelevant_by_rules(text: str) -> bool:
    # Do not gate when clear speculative focus or global-law intro
    if FOCUS_ON_AI.search(text) or INTEND_FOCUS.search(text) or FUTURE_FEATURES.search(text) or GLOBAL_SUBJECT_LAWS.search(text):
        return False
    # Investment laundry list shouldn’t be gated as Irrelevant
    if re.search(r"continue\s+to\s+invest\s+in\s+new\s+and\s+unproven\s+technologies,?\s+including\s+(ai|artificial intelligence)", text, re.I):
        return False
    # Generic infrastructure / data-leakage / strategy re-eval / lawsuits / decreased engagement lists → Irrelevant
    if INFRASTRUCTURE_BROAD.search(text) or INFRASTRUCTURE.search(text):
        return True
    if re.search(r"data\s+leakage|unauthorized\s+exposure\s+of\s+data", text, re.I):
        return True
    if re.search(r"reevaluated our data center investment strategy", text, re.I):
        return True
    if re.search(r"subject to multiple lawsuits|subject of multiple lawsuits", text, re.I):
        return True
    if DECREASED_ENGAGEMENT.search(text):
        return True
    if LAWS_LIST_INTRO.search(text):
        return True
    if FUTURE_BASED_ON_AI.search(text):
        return True
    if APPLY_LEARNINGS.search(text):
        return True
    if INNOVATING_BUILD.search(text) and not ACTION_VERBS.search(text):
        return True
    return False


def should_force_speculative(text: str) -> bool:
    # Explicit intent/future without strong action cues → Speculative
    return (
        (bool(MODALS.search(text)) and not bool(ACTION_VERBS.search(text)))
        or bool(INTEND_FOCUS.search(text))
        or bool(FOCUS_ON_AI.search(text))
        or bool(FUTURE_FEATURES.search(text))
        or bool(GLOBAL_SUBJECT_LAWS.search(text))
    )


def classify_two_stage(
    text: str,
    two_stage: bool = True,
    rule_boosts: bool = True,
    tau: float = 0.07,
    eps_irr: float = 0.03,
    min_tokens: int = 6,
) -> Tuple[str, Dict[str, float]]:
    """Two-stage classifier with optional rule boosts (kept API-parity with evaluator)."""
    # Hard override: explicit future/intent language with no strong action cues → Speculative
    if should_force_speculative(text) and not ACTION_VERBS.search(text):
        return "Speculative", {"Actionable": 0.0, "Speculative": 1.0, "Irrelevant": 0.0, "fine_margin": 0.0}

    tokens = len(text.split())
    if tokens < min_tokens:
        # Too short – fall back to centroid
        scores = _centroid_scores(text)
        label = max(scores.items(), key=lambda kv: kv[1])[0]
        scores["fine_margin"] = 0.0
        return label, scores

    # Early Irrelevant gate
    if two_stage and is_irrelevant_by_rules(text):
        return "Irrelevant", {"Actionable": 0.0, "Speculative": 0.0, "Irrelevant": 1.0, "fine_margin": 0.0}

    # Ops‑risk Actionable preference when no future/intent
    if (PREVENT_DELIVER.search(text) or USER_DIMINISH.search(text)) and not MODALS.search(text):
        return "Actionable", {"Actionable": 1.0, "Speculative": 0.0, "Irrelevant": 0.0, "fine_margin": 0.0}

    # Centroid pass
    scores = _centroid_scores(text)

    if rule_boosts:
        scores = adjust_scores_v2(text, scores)
        # Global law intro → speculative tilt
        if GLOBAL_SUBJECT_LAWS.search(text):
            scores["Speculative"] = scores.get("Speculative", 0.0) + 0.12
            scores["Irrelevant"] = max(0.0, scores.get("Irrelevant", 0.0) - 0.08)

    # Fine decision by margin
    a = scores.get("Actionable", 0.0)
    s = scores.get("Speculative", 0.0)
    i = scores.get("Irrelevant", 0.0)
    top = max(a, s, i)
    second = sorted([a, s, i])[-2]
    margin = abs(top - second)

    if two_stage and abs(i - max(a, s)) < eps_irr and i > 0.5:
        label = "Irrelevant"
    elif abs(a - s) < tau:
        # Tie-breaker: prefer Speculative when future/modal present; else Actionable
        if should_force_speculative(text):
            label = "Speculative"
        else:
            label = "Actionable" if a >= s else "Speculative"
    else:
        label = "Actionable" if a >= s and a >= i else ("Speculative" if s >= a and s >= i else "Irrelevant")

    scores["fine_margin"] = round(margin, 3)
    return label, scores
