import os
import spacy
import pandas as pd

# Load spaCy's English language model
nlp = spacy.load("en_core_web_sm")

# Define the directory containing SEC filings
sec_filings_dir = "data/raw/sec_filings/"

# Define the output directory for interim data
output_dir = "data/interim/"
os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist

# Initialize a list to store results
results = []

# Logging: Start of the process
print("Starting SEC text processing...")

# Loop through each ticker's filings
for ticker in os.listdir(sec_filings_dir):
    ticker_dir = os.path.join(sec_filings_dir, ticker, "10-K")
    
    # Check if the 10-K directory exists
    if not os.path.exists(ticker_dir):
        print(f"Skipping {ticker}: 10-K directory not found.")
        continue
    
    # Logging: Processing ticker
    print(f"Processing ticker: {ticker}")
    
    # Loop through each filing
    for filing in os.listdir(ticker_dir):
        filing_path = os.path.join(ticker_dir, filing, "full-submission.txt")
        
        # Check if the full-submission.txt file exists
        if not os.path.exists(filing_path):
            print(f"Skipping {filing}: full-submission.txt not found.")
            continue
        
        # Logging: Processing filing
        print(f"  Processing filing: {filing}")
        
        # Read the filing text
        with open(filing_path, "r", encoding="utf-8") as file:
            text = file.read()
        
        # Use spaCy to split the text into sentences
        doc = nlp(text)
        sentences = [sent.text for sent in doc.sents]
        
        # Logging: Number of sentences extracted
        print(f"    Extracted {len(sentences)} sentences.")
        
        # Filter sentences for AI-related keywords
        ai_keywords = ["artificial intelligence", "machine learning", "AI", "deep learning"]
        ai_sentences = [sentence for sentence in sentences if any(keyword.lower() in sentence.lower() for keyword in ai_keywords)]
        
        # Logging: Number of AI-related sentences
        print(f"    Found {len(ai_sentences)} AI-related sentences.")
        
        # Store results with metadata
        for sentence in ai_sentences:
            results.append({
                "ticker": ticker,
                "filing_date": filing[:10],  # Extract date from filename (e.g., "2022-01-01")
                "sentence": sentence
            })

# Convert results to a DataFrame
df = pd.DataFrame(results)

# Logging: Total number of AI-related sentences found
print(f"Total AI-related sentences found: {len(df)}")

# Save the results to an interim file
output_path = os.path.join(output_dir, "sec_ai_sentences.parquet")
df.to_parquet(output_path, index=False)

# Logging: Output saved
print(f"Saved results to {output_path}")

# Validation: Check the output file
if os.path.exists(output_path):
    print("Validation: Output file created successfully.")
    # Load the output file and display the first few rows
    df_check = pd.read_parquet(output_path)
    print("Sample of the output:")
    print(df_check.head())
else:
    print("Validation: Output file not found. Check for errors.")