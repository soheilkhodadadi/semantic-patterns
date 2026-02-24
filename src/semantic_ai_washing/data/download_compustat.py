# src/data/download_compustat.py
import wrds
import pandas as pd
from dotenv import load_dotenv
import os
import getpass

# Load environment variables from .env file
load_dotenv()

# Get WRDS credentials from .env
wrds_username = os.getenv("WRDS_USER")
wrds_password = os.getenv("WRDS_PASS")

# Override getpass to use the username and password from .env
getpass.getpass = lambda prompt: wrds_username if "username" in prompt.lower() else wrds_password

# Connect to WRDS
print("Connecting to WRDS...")
db = wrds.Connection(wrds_username=wrds_username)

def download_compustat_sample():
    # Define the tickers for the companies we want
    tickers = ['AAPL', 'AMZN', 'MSFT']  # Apple, Amazon, Microsoft
    
    # Step 1: Get GVKEYs (unique identifiers for companies) for these tickers
    print("Fetching GVKEYs for the tickers...")
    gvkey_query = f"""
        SELECT a.gvkey, a.tic, b.conm
        FROM comp.secm AS a
        JOIN comp.company AS b
        ON a.gvkey = b.gvkey
        WHERE a.tic IN {tuple(tickers)}
    """
    gvkeys = db.raw_sql(gvkey_query)
    print("GVKEYs fetched successfully!")
    
    # Step 2: Download annual financial data for these GVKEYs
    print("Downloading Compustat data...")
    compustat_query = f"""
        SELECT gvkey, datadate, fyear, at, sale, ni, ceq
        FROM comp.funda
        WHERE gvkey IN {tuple(gvkeys.gvkey)}
        AND indfmt = 'INDL'  -- Industrial format
        AND datafmt = 'STD'  -- Standard format
        AND consol = 'C'     -- Consolidated statements
        AND popsrc = 'D'     -- Primary source
    """
    compustat_data = db.raw_sql(compustat_query)
    print("Compustat data downloaded successfully!")
    
    # Step 3: Create the directory if it doesn't exist
    # Get the project root directory (move up two levels from the script's location)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output_dir = os.path.join(project_root, 'data', 'raw', 'compustat')
    os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist
    
    # Debug: Print the absolute path of the output directory
    print(f"Project root: {project_root}")
    print(f"Absolute path of output directory: {output_dir}")
    
    # Step 4: Save the data to a CSV file
    output_path = os.path.join(output_dir, 'compustat_sample.csv')
    print(f"Absolute path of output file: {output_path}")
    
    print("Saving data to CSV...")
    compustat_data.to_csv(output_path, index=False)
    print(f"Data saved to '{output_path}'")

# Run the function
if __name__ == "__main__":
    download_compustat_sample()