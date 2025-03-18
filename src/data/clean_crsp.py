# src/data/clean_crsp.py
import os
import pandas as pd
from pathlib import Path

def ensure_folder_exists(folder_path: str) -> None:
    """Ensure the folder exists; if not, create it."""
    Path(folder_path).mkdir(parents=True, exist_ok=True)

def clean_crsp(raw_path: str, processed_path: str) -> None:
    # Ensure processed folder exists
    ensure_folder_exists(os.path.dirname(processed_path))
    
    # Load raw CRSP data
    df = pd.read_csv(raw_path)
    
    # Convert date column
    df['date'] = pd.to_datetime(df['date'])
    
    # Handle missing returns
    df['ret'] = pd.to_numeric(df['ret'], errors='coerce')
    df.loc[df['ret'].isna(), 'ret'] = -0.3  # Delisting adjustment
    
    # Calculate market capitalization
    df['mktcap'] = abs(df['prc']) * df['shrout']
    
    # Filter extreme values
    df = df[df['mktcap'].between(1e6, 1e12)]
    
    # Standardize identifiers
    df['permno'] = df['permno'].astype(int).astype(str)
    
    # Save cleaned data
    df.to_parquet(processed_path, index=False)

if __name__ == "__main__":
    raw_crsp_path = "../data/raw/crsp/crsp_sample.csv"
    processed_crsp_path = "../data/processed/crsp/crsp_cleaned.parquet"
    clean_crsp(raw_crsp_path, processed_crsp_path)