"""
Builds a company lookup table with CIK codes and cleaned company names.

This script creates a mapping between company names and their CIK identifiers
for use in patent extraction and other analyses.

Run: python src/patents/build_company_lookup.py
"""

import pandas as pd
import os
import re

def clean_company_name(name):
    """
    Clean company name for consistent matching.
    
    Args:
        name (str): Raw company name
        
    Returns:
        str: Cleaned company name
    """
    if pd.isna(name):
        return ""
    
    # Convert to lowercase
    name = str(name).lower()
    
    # Remove common suffixes
    suffixes = [
        r'\s+inc\.?$',
        r'\s+corp\.?$', 
        r'\s+corporation$',
        r'\s+ltd\.?$',
        r'\s+llc$',
        r'\s+co\.?$',
        r'\s+company$'
    ]
    
    for suffix in suffixes:
        name = re.sub(suffix, '', name)
    
    # Remove special characters except spaces
    name = re.sub(r'[^\w\s]', '', name)
    
    # Remove extra whitespace
    name = ' '.join(name.split())
    
    return name.strip()

def build_company_lookup():
    """
    Build company lookup table from sample data.
    
    In practice, this would load from CRSP/Compustat or SEC data.
    """
    
    # Sample company data - replace with actual data source
    companies = [
        {"cik": "0000320193", "name": "Apple Inc."},
        {"cik": "0001652044", "name": "DoorDash Inc."},
        {"cik": "0001321569", "name": "Palantir Technologies Inc."},
        {"cik": "0000789019", "name": "Microsoft Corporation"},
        {"cik": "0001652044", "name": "Alphabet Inc."},
        {"cik": "0001318605", "name": "Tesla Inc."},
        {"cik": "0001018724", "name": "Amazon.com Inc."},
        {"cik": "0001326801", "name": "Meta Platforms Inc."},
        {"cik": "0001045810", "name": "NVIDIA Corporation"},
        {"cik": "0000051143", "name": "International Business Machines Corporation"},
    ]
    
    # Create DataFrame
    df = pd.DataFrame(companies)
    
    # Add cleaned names
    df["name_clean"] = df["name"].apply(clean_company_name)
    
    # Ensure output directory exists
    output_path = "data/metadata/company_lookup.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    
    print(f"[✓] Created company lookup with {len(df)} companies")
    print(f"[✓] Saved to: {output_path}")
    
    # Display sample
    print("\nSample entries:")
    print(df.head())
    
    return df

if __name__ == "__main__":
    build_company_lookup()