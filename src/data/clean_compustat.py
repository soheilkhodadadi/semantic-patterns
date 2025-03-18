# src/data/clean_compustat.py
import os
import pandas as pd
from pathlib import Path

def ensure_folder_exists(folder_path: str) -> None:
    """Ensure the folder exists; if not, create it."""
    Path(folder_path).mkdir(parents=True, exist_ok=True)

def clean_compustat(raw_path: str, processed_path: str) -> None:
    # Ensure processed folder exists
    ensure_folder_exists(os.path.dirname(processed_path))
    
    # Load raw Compustat data
    df = pd.read_csv(raw_path)
    
    # Convert datadate to fiscal year-end
    df['datadate'] = pd.to_datetime(df['datadate'])
    df['fyear'] = df['datadate'].dt.year
    
    # Calculate financial ratios
    df['roa'] = df['ni'] / df['at']
    df['leverage'] = df['lt'] / df['at']
    
    # Handle outliers (winsorize at 1% and 99%)
    for col in ['at', 'sale', 'ni']:
        lower = df[col].quantile(0.01)
        upper = df[col].quantile(0.99)
        df[col] = df[col].clip(lower=lower, upper=upper)
    
    # Standardize identifiers
    df['gvkey'] = df['gvkey'].astype(str)
    
    # Save cleaned data
    df.to_parquet(processed_path, index=False)

if __name__ == "__main__":
    raw_compustat_path = "../data/raw/compustat/compustat_sample.csv"
    processed_compustat_path = "../data/processed/compustat/compustat_cleaned.parquet"
    clean_compustat(raw_compustat_path, processed_compustat_path)