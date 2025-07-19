import os
import re
import spacy

# AI-related keywords (matched case-insensitively with word boundaries)
AI_KEYWORDS = [
    "AI", "artificial intelligence",
    "machine learning", "deep learning",
    "neural network", "NLP"
]

# Load SpaCy's large English model
nlp = spacy.load("en_core_web_lg")

# Define input and output directories
input_dir = "data/external"
output_dir = "data/processed/sec"
os.makedirs(output_dir, exist_ok=True)

# Process all .txt files in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith(".txt"):
        input_path = os.path.join(input_dir, filename)
        output_filename = filename.replace(".txt", "_ai_sentences.txt")
        output_path = os.path.join(output_dir, output_filename)

        # Read full disclosure text
        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Segment the text into sentences
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

        # Filter sentences using regex with word boundaries
        ai_sentences = [
            sentence for sentence in sentences
            if any(re.search(rf"\b{re.escape(keyword)}\b", sentence, re.IGNORECASE) for keyword in AI_KEYWORDS)
        ]

        # Save filtered AI-related sentences
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(ai_sentences))

        print(f"[✓] Saved {len(ai_sentences)} AI-related sentences to: {output_path}")
