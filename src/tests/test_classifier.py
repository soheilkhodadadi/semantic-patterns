import sys
import os

# Add the src/ folder to the Python path dynamically
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from classification.classify_with_centroids import classify_sentence

test_sentences = [
    "We launched a new generative AI engine for product personalization.",  # Actionable
    "We are exploring AI capabilities for internal operations.",             # Speculative
    "AI is one of many technologies transforming the industry."             # Irrelevant
]

for sent in test_sentences:
    label, score = classify_sentence(sent)
    print(f"\n📝 Sentence: {sent}\n📌 Predicted: {label}\n📊 Scores: {score}")
