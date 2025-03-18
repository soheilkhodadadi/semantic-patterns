# src/data/clean_compustat.py
import os
import pandas as pd
from pathlib import Path

def ensure_folder_exists(folder_path: str) -> None:
    """
    Ensure the folder exists; if not, create it.
    """
    if not os.path.exists(folder_path):
        print(f"Folder does not exist. Creating: {folder_path}")
        Path(folder_path).mkdir(parents=True, exist_ok=True)
    else:
        print(f"Folder already exists: {folder_path}")

def validate_cleaned_data(df: pd.DataFrame) -> None:
    """
    Validate the cleaned data by checking for common issues.
    """
    print("\nValidating cleaned data...")
    
    # Check for missing values
    missing_values = df.isna().sum()
    print("Missing values per column:")
    print(missing_values)
    
    # Check data types
    print("\nData types:")
    print(df.dtypes)
    
    # Check for duplicates
    duplicates = df.duplicated().sum()
    print(f"\nNumber of duplicate rows: {duplicates}")
    
    # Check summary statistics
    print("\nSummary statistics for numeric columns:")
    print(df.describe())
    
    # Print a sample of the cleaned data
    print("\nSample of cleaned data:")
    print(df.head())

def clean_compustat(raw_path: str, processed_path: str) -> None:
    """
    Clean Compustat data and save it to the specified path.
    """
    print("Starting Compustat data cleaning...")
    
    # Check if the input file exists
    if not os.path.exists(raw_path):
        print(f"Error: Input file not found at {raw_path}")
        return
    
    # Ensure the processed folder exists
    ensure_folder_exists(os.path.dirname(processed_path))
    
    # Load raw Compustat data
    print(f"Loading raw data from: {raw_path}")
    df = pd.read_csv(raw_path)
    print(f"Raw data loaded successfully. Rows: {len(df)}")
    
    # Convert datadate to fiscal year-end
    print("Converting datadate to fiscal year-end...")
    df['datadate'] = pd.to_datetime(df['datadate'])
    df['fyear'] = df['datadate'].dt.year
    
    # Calculate financial ratios
    print("Calculating financial ratios...")
    df['roa'] = df['ni'] / df['at']  # Return on assets
    
    # Check if 'lt' (long-term debt) column exists
    if 'lt' in df.columns:
        df['leverage'] = df['lt'] / df['at']  # Leverage ratio
    else:
        print("Warning: 'lt' column not found. Skipping leverage calculation.")
        df['leverage'] = pd.NA  # Add a placeholder column
    
    # Handle outliers (winsorize at 1% and 99%)
    print("Handling outliers...")
    for col in ['at', 'sale', 'ni']:
        if col in df.columns:
            lower = df[col].quantile(0.01)
            upper = df[col].quantile(0.99)
            df[col] = df[col].clip(lower=lower, upper=upper)
        else:
            print(f"Warning: Column '{col}' not found. Skipping winsorization.")
    
    # Standardize identifiers
    print("Standardizing identifiers...")
    df['gvkey'] = df['gvkey'].astype(str)
    
    # Validate the cleaned data
    validate_cleaned_data(df)
    
    # Check if the output file already exists
    if os.path.exists(processed_path):
        print(f"Warning: File already exists at {processed_path}. Overwriting...")
    
    # Save cleaned data as Parquet
    print(f"Saving cleaned data to: {processed_path}")
    df.to_parquet(processed_path, index=False, engine='pyarrow')
    print("Cleaned data saved successfully!")

if __name__ == "__main__":
    # Get the project root directory (one level up from src/data)
    project_root = Path(__file__).resolve().parent.parent.parent
    
    # Define paths relative to the project root
    raw_compustat_path = project_root / "data/raw/compustat/compustat_sample.csv"
    processed_compustat_path = project_root / "data/processed/compustat/compustat_cleaned.parquet"
    
    # Run the cleaning function
    clean_compustat(str(raw_compustat_path), str(processed_compustat_path))
    print("Compustat data cleaning completed.")