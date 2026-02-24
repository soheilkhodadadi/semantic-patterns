# src/data/clean_crsp.py
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

def clean_crsp(raw_path: str, processed_path: str) -> None:
    """
    Clean CRSP data and save it to the specified path.
    """
    print("Starting CRSP data cleaning...")
    
    # Check if the input file exists
    if not os.path.exists(raw_path):
        print(f"Error: Input file not found at {raw_path}")
        return
    
    # Ensure the processed folder exists
    ensure_folder_exists(os.path.dirname(processed_path))
    
    # Load raw CRSP data
    print(f"Loading raw data from: {raw_path}")
    df = pd.read_csv(raw_path)
    print(f"Raw data loaded successfully. Rows: {len(df)}")
    
    # Convert date column
    print("Converting date column...")
    df['date'] = pd.to_datetime(df['date'])
    
    # Handle missing returns
    print("Handling missing returns...")
    df['ret'] = pd.to_numeric(df['ret'], errors='coerce')
    df.loc[df['ret'].isna(), 'ret'] = -0.3  # Delisting adjustment
    
    # Calculate market capitalization
    print("Calculating market capitalization...")
    df['mktcap'] = abs(df['prc']) * df['shrout']
    
    # Filter extreme values
    print("Filtering extreme values...")
    df = df[df['mktcap'].between(1e6, 1e12)]
    print(f"Rows after filtering: {len(df)}")
    
    # Standardize identifiers
    print("Standardizing identifiers...")
    df['permno'] = df['permno'].astype(int).astype(str)
    
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
    raw_crsp_path = project_root / "data/raw/crsp/crsp_sample.csv"
    processed_crsp_path = project_root / "data/processed/crsp/crsp_cleaned.parquet"
    
    # Run the cleaning function
    clean_crsp(str(raw_crsp_path), str(processed_crsp_path))
    print("CRSP data cleaning completed.")