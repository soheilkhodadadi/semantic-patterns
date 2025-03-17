import sys
from pathlib import Path

# Add the root directory of the project to the PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parents[2]))

from sec_edgar_downloader import Downloader
import logging
from src.config import SEC_CONFIG  # Import your config

def download_sec_filings():
    """Download 10-K filings for specified tickers"""
    # Initialize paths
    raw_dir = Path("data/raw/sec_filings")
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize downloader
    user_agent = SEC_CONFIG.get("email")
    if not user_agent:
        logging.error("User agent (email) is not set in SEC_CONFIG")
        return
    
    logging.info(f"Using user agent: {user_agent}")
    
    try:
        dl = Downloader(
            company_name="Concordia University",  # Replace with your company name
            email_address=user_agent,             # Use your email as the email address
            download_folder=raw_dir
        )
    except Exception as e:
        logging.error(f"Failed to initialize Downloader: {str(e)}")
        return
    
    # Download filings
    for ticker in SEC_CONFIG["tickers"]:
        try:
            # Updated method call
            dl.get(
                "10-K",  # Filing type
                ticker,   # Ticker or CIK
                after=f"{SEC_CONFIG['start_year']}-01-01",
                before=f"{SEC_CONFIG['end_year']}-12-31"
            )
            logging.info(f"✅ Downloaded {ticker} 10-K filings")
        except Exception as e:
            logging.error(f"❌ Failed to download {ticker}: {str(e)}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    download_sec_filings()