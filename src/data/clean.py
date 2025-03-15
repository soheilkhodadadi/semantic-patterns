# src/data/clean.py
import pandas as pd
from pathlib import Path

def clean_sec_filings(raw_dir, interim_dir):
    """
    Clean raw SEC filings and save to interim folder.
    """
    raw_dir = Path(raw_dir)
    interim_dir = Path(interim_dir)
    interim_dir.mkdir(parents=True, exist_ok=True)
    
    # Example: Load and clean data
    for file in raw_dir.glob("*.html"):
        # Add your cleaning logic here
        print(f"Cleaning {file.name}")
    
    print("✅ Cleaning complete!")