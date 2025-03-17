import os
import wrds
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

def download_crsp_compustat_data():
    """Download CRSP and Compustat data from WRDS."""
    # Initialize paths
    raw_dir = Path("data/raw/crsp_compustat")
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # Connect to WRDS
    try:
        db = wrds.Connection(
            wrds_username=os.getenv("WRDS_USERNAME"),
            wrds_password=os.getenv("WRDS_PASSWORD")
        )
        logging.info("✅ Connected to WRDS")
    except Exception as e:
        logging.error(f"❌ Failed to connect to WRDS: {str(e)}")
        return
    
    # Download CRSP data
    try:
        crsp_query = """
            SELECT permno, date, ret, prc
            FROM crsp.dsf
            WHERE date BETWEEN '2010-01-01' AND '2023-12-31'
        """
        crsp_data = db.raw_sql(crsp_query)
        crsp_data.to_csv(raw_dir / "crsp_data.csv", index=False)
        logging.info("✅ Downloaded CRSP data")
    except Exception as e:
        logging.error(f"❌ Failed to download CRSP data: {str(e)}")
    
    # Download Compustat data
    try:
        compustat_query = """
            SELECT gvkey, datadate, at, sale, ni
            FROM comp.funda
            WHERE indfmt='INDL' AND datafmt='STD' AND consol='C'
        """
        compustat_data = db.raw_sql(compustat_query)
        compustat_data.to_csv(raw_dir / "compustat_data.csv", index=False)
        logging.info("✅ Downloaded Compustat data")
    except Exception as e:
        logging.error(f"❌ Failed to download Compustat data: {str(e)}")
    
    # Close the WRDS connection
    db.close()
    logging.info("✅ Closed WRDS connection")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    download_crsp_compustat_data()