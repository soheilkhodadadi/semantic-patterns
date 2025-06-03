import os
import re

# Step 1: Define AI-related keywords
AI_KEYWORDS = [
    r"\bAI\b", r"\bartificial intelligence\b",
    r"\bmachine learning\b", r"\bdeep learning\b",
    r"\bneural network\b", r"\bNLP\b"
]

# Step 2: Define input/output paths
input_dir = "data/external"
output_dir = "data/processed/sec"
os.makedirs(output_dir, exist_ok=True)

# Step 3: Loop over all text files in input directory
for filename in os.listdir(input_dir):
    if filename.endswith(".txt"):
        input_path = os.path.join(input_dir, filename)
        output_filename = filename.replace(".txt", "_ai_sentences.txt")
        output_path = os.path.join(output_dir, output_filename)

        # Read disclosure text line by line
        with open(input_path, "r", encoding="utf-8") as f:
            sentences = [line.strip() for line in f if line.strip()]

        # Filter AI-related sentences
        ai_sentences = []
        for sentence in sentences:
            if any(re.search(pattern, sentence, re.IGNORECASE) for pattern in AI_KEYWORDS):
                ai_sentences.append(sentence)

        # Save filtered sentences
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(ai_sentences))

        print(f"[✓] Saved {len(ai_sentences)} AI-related sentences to: {output_path}")
