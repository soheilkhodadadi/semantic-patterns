import os
import re
from pysbd import Segmenter
from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd

# Define paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sec_filings_dir = os.path.join(project_root, "data", "raw", "sec_filings", "sec-edgar-filings")
output_dir = os.path.join(project_root, "data", "interim")
os.makedirs(output_dir, exist_ok=True)

# Initialize segmenter and regex
segmenter = Segmenter(language="en", clean=False)
ai_pattern = re.compile(r"\b(artificial intelligence|machine learning|AI|deep learning)\b", re.IGNORECASE)

# Function to process a single file
def process_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        
        # Use PySBD for faster sentence segmentation
        sentences = segmenter.segment(text)
        ai_sentences = [sentence for sentence in sentences if ai_pattern.search(sentence)]
        
        return ai_sentences
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

# Main processing logic
def main():
    results = []
    for ticker in os.listdir(sec_filings_dir):
        ticker_dir = os.path.join(sec_filings_dir, ticker, "10-K")
        if not os.path.exists(ticker_dir):
            print(f"Skipping {ticker}: 10-K directory not found.")
            continue
        
        # Loop through each filing folder
        filing_paths = [os.path.join(ticker_dir, filing, "full-submission.txt") for filing in os.listdir(ticker_dir)]
        
        # Process files in parallel
        try:
            with ProcessPoolExecutor(max_workers=4) as executor:
                futures = {executor.submit(process_file, path): path for path in filing_paths}
                for future in as_completed(futures):
                    path = futures[future]
                    try:
                        ai_sentences = future.result()
                        for sentence in ai_sentences:
                            results.append({
                                "ticker": ticker,
                                "filing_date": os.path.basename(path)[:10],  # Extract date from filename
                                "sentence": sentence
                            })
                        print(f"Processed {path} - Found {len(ai_sentences)} AI-related sentences.")
                    except Exception as e:
                        print(f"Error processing {path}: {e}")
        except Exception as e:
            print(f"Error in ProcessPoolExecutor: {e}")

    # Save results
    df = pd.DataFrame(results)
    output_path = os.path.join(output_dir, "sec_ai_sentences.parquet")
    df.to_parquet(output_path, index=False)

    print(f"Total AI-related sentences found: {len(df)}")
    print(f"Saved results to {output_path}")

# Guard for multiprocessing
if __name__ == "__main__":
    main()