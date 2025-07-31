from src.classification.classify_with_centroids import classify_sentence

test_sentences = [
    "We launched a new generative AI engine for product personalization.",  # Actionable
    "We are exploring AI capabilities for internal operations.",             # Speculative
    "AI is one of many technologies transforming the industry."             # Irrelevant
]

for sent in test_sentences:
    label, score = classify_sentence(sent)
    print(f"\n📝 Sentence: {sent}\n📌 Predicted: {label}\n📊 Scores: {score}")
