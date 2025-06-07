import os
import re
import spacy

# Step 1: Define AI-related keywords (as lowercase phrases for substring matching)
AI_KEYWORDS = [
    "ai", "artificial intelligence",
    "machine learning", "deep learning",
    "neural network", "nlp"
]

# Step 2: Load SpaCy model for sentence segmentation
nlp = spacy.load("en_core_web_lg")

# Step 3: Define input/output paths
input_dir = "data/external"
output_dir = "data/processed/sec"
os.makedirs(output_dir, exist_ok=True)

# Step 4: Loop over all .txt files
for filename in os.listdir(input_dir):
    if filename.endswith(".txt"):
        input_path = os.path.join(input_dir, filename)
        output_filename = filename.replace(".txt", "_ai_sentences.txt")
        output_path = os.path.join(output_dir, output_filename)

        # Load and segment full text using SpaCy
        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

        # Step 5: Filter sentences containing AI keywords
        ai_sentences = [
            sentence for sentence in sentences
            if any(keyword in sentence.lower() for keyword in AI_KEYWORDS)
        ]

        # Step 6: Save filtered sentences
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(ai_sentences))

        print(f"[✓] Saved {len(ai_sentences)} AI-related sentences to: {output_path}")
