import sys
import os

# Add the src/ folder to the Python path dynamically
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import classifier
from classification.classify_with_centroids import classify_sentence

# Define a few sample sentences to test
test_sentences = [
    "We launched a new generative AI engine for product personalization.",  # Should be Actionable
    "We are exploring AI capabilities for internal operations.",             # Should be Speculative
    "AI is one of many technologies transforming the industry."              # Should be Irrelevant
]

# Run the classifier and print results
for sent in test_sentences:
    label, score = classify_sentence(sent)
    print(f"\n📝 Sentence: {sent}\n📌 Predicted: {label}\n📊 Scores: {score}")
