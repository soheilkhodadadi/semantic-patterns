# src/data/download_crsp.py
import wrds
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


def download_crsp_sample():
    # Define the tickers for the companies we want
    tickers = ["AAPL", "AMZN", "MSFT"]  # Apple, Amazon, Microsoft

    # Step 1: Get PERMNOs (unique identifiers for stocks) for these tickers
    print("Fetching PERMNOs for the tickers...")
    permno_query = f"""
        SELECT permno, ticker, comnam
        FROM crsp.stocknames
        WHERE ticker IN {tuple(tickers)}
    """
    permnos = db.raw_sql(permno_query)
    print("PERMNOs fetched successfully!")

    # Convert permno values to plain Python integers
    permno_list = permnos["permno"].tolist()  # Convert to list of integers

    # Step 2: Download monthly stock data for these PERMNOs
    print("Downloading CRSP data...")
    crsp_query = f"""
        SELECT a.permno, date, ret, prc, vol, shrout
        FROM crsp.msf AS a
        WHERE a.permno IN {tuple(permno_list)}
        AND date BETWEEN '2010-01-01' AND '2023-12-31'
    """
    crsp_data = db.raw_sql(crsp_query)
    print("CRSP data downloaded successfully!")

    # Step 3: Create the directory if it doesn't exist
    # Get the project root directory (move up two levels from the script's location)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output_dir = os.path.join(project_root, "data", "raw", "crsp")
    os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist

    # Debug: Print the absolute path of the output directory
    print(f"Project root: {project_root}")
    print(f"Absolute path of output directory: {output_dir}")

    # Step 4: Save the data to a CSV file
    output_path = os.path.join(output_dir, "crsp_sample.csv")
    print(f"Absolute path of output file: {output_path}")

    print("Saving data to CSV...")
    crsp_data.to_csv(output_path, index=False)
    print(f"Data saved to '{output_path}'")


# Run the function
if __name__ == "__main__":
    download_crsp_sample()
