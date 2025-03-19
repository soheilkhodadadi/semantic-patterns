import os
import re
from pysbd import Segmenter
from concurrent.futures import ProcessPoolExecutor
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
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    
    # Use PySBD for faster sentence segmentation
    sentences = segmenter.segment(text)
    ai_sentences = [sentence for sentence in sentences if ai_pattern.search(sentence)]
    
    return ai_sentences

# Function to process large files in chunks
def process_large_file(file_path, chunk_size=1000000):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    
    # Split text into chunks
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    
    ai_sentences = []
    for chunk in chunks:
        sentences = segmenter.segment(chunk)
        ai_sentences.extend([sentence for sentence in sentences if ai_pattern.search(sentence)])
    
    return ai_sentences

# Main processing loop
results = []
for ticker in os.listdir(sec_filings_dir):
    ticker_dir = os.path.join(sec_filings_dir, ticker, "10-K")
    if not os.path.exists(ticker_dir):
        continue
    
    filing_paths = [os.path.join(ticker_dir, filing, "full-submission.txt") for filing in os.listdir(ticker_dir)]
    
    # Process files in parallel
    with ProcessPoolExecutor() as executor:
        ai_sentences = list(executor.map(process_file, filing_paths))
    
    for sentences in ai_sentences:
        for sentence in sentences:
            results.append({
                "ticker": ticker,
                "filing_date": os.path.basename(filing_paths[0])[:10],  # Extract date from filename
                "sentence": sentence
            })

# Save results
df = pd.DataFrame(results)
df.to_parquet(os.path.join(output_dir, "sec_ai_sentences.parquet"), index=False)

print(f"Total AI-related sentences found: {len(df)}")
print(f"Saved results to {os.path.join(output_dir, 'sec_ai_sentences.parquet')}")