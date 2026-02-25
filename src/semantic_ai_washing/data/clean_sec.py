import os
import re
from pysbd import Segmenter
from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd
import spacy
from spacy.matcher import PhraseMatcher


# Define paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sec_filings_dir = os.path.join(project_root, "data", "raw", "sec_filings", "sec-edgar-filings")
output_dir = os.path.join(project_root, "data", "interim")
os.makedirs(output_dir, exist_ok=True)

# Initialize segmenter and regex
segmenter = Segmenter(language="en", clean=False)
ai_pattern = re.compile(
    r"\b(artificial intelligence|machine learning|AI|deep learning)\b", re.IGNORECASE
)


# Load term lists
def load_terms(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


concrete_terms = load_terms("data/metadata/technical_terms/concrete_terms.txt")
vague_terms = load_terms("data/metadata/technical_terms/vague_terms.txt")

# Initialize SpaCy and PhraseMatcher
nlp = spacy.load("en_core_web_lg")  # Load the large English model
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")  # Case-insensitive matching
matcher.add("CONCRETE", [nlp(text) for text in concrete_terms])
matcher.add("VAGUE", [nlp(text) for text in vague_terms])


# Function to process a single file


def process_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()

        sentences = segmenter.segment(text)
        scored_sentences = []

        for sentence in sentences:
            if not ai_pattern.search(sentence):
                continue  # Skip non-AI sentences

            doc = nlp(sentence)
            matches = matcher(doc)
            concrete_count = 0
            vague_count = 0

            for match_id, start, end in matches:
                if nlp.vocab.strings[match_id] == "CONCRETE":
                    concrete_count += 1
                else:
                    vague_count += 1

            total_terms = concrete_count + vague_count
            score = concrete_count / total_terms if total_terms > 0 else 0

            scored_sentences.append(
                {
                    "sentence": sentence,
                    "score": score,
                    "concrete_terms": concrete_count,
                    "vague_terms": vague_count,
                }
            )

        return scored_sentences
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []


def main():
    results = []
    tickers = os.listdir(sec_filings_dir)
    print(f"Found {len(tickers)} tickers to process: {tickers}")

    for ticker in tickers:
        ticker_dir = os.path.join(sec_filings_dir, ticker, "10-K")
        if not os.path.exists(ticker_dir):
            print(f"Skipping {ticker}: 10-K directory not found.")
            continue

        print(f"Processing ticker: {ticker}")
        filings = os.listdir(ticker_dir)
        print(f"Found {len(filings)} filings for {ticker}: {filings}")

        filing_paths = [
            os.path.join(ticker_dir, filing, "full-submission.txt") for filing in filings
        ]

        print(f"Starting parallel processing for {ticker} with {len(filing_paths)} files.")
        try:
            with ProcessPoolExecutor(max_workers=4) as executor:
                futures = {executor.submit(process_file, path): path for path in filing_paths}

                for future in as_completed(futures):
                    path = futures[future]
                    try:
                        ai_sentences = future.result()
                        for sentence in ai_sentences:
                            results.append(
                                {
                                    "ticker": ticker,
                                    "filing_date": os.path.basename(
                                        os.path.dirname(path)
                                    ),  # Extract folder name as date
                                    "sentence": sentence["sentence"],
                                    "score": sentence["score"],
                                    "concrete_terms": sentence["concrete_terms"],
                                    "vague_terms": sentence["vague_terms"],
                                }
                            )
                        print(f"Completed processing: {path}")
                    except Exception as e:
                        print(f"Error processing {path}: {e}")
        except Exception as e:
            print(f"Error in ProcessPoolExecutor for {ticker}: {e}")

    # Save results
    df = pd.DataFrame(results)
    output_path = os.path.join(output_dir, "sec_ai_sentences.parquet")
    df.to_parquet(output_path, index=False)

    print(f"Total AI-related sentences found: {len(df)}")
    print(f"Saved results to {output_path}")


# Guard for multiprocessing
if __name__ == "__main__":
    main()
