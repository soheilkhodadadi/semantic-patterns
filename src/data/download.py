from sec_edgar_downloader import Downloader
from pathlib import Path
import logging
from src.config import SEC_CONFIG  # Import your config

def download_sec_filings():
    """Download 10-K filings for specified tickers"""
    # Initialize paths
    raw_dir = Path("data/raw/sec_filings")
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize downloader
    dl = Downloader(
        company_name="Your Project Name",
        email=SEC_CONFIG["email"],  # From config.py
        download_folder=raw_dir
    )
    
    # Download filings
    for ticker in SEC_CONFIG["tickers"]:
        try:
            dl.get(
                filing_type="10-K",
                ticker_or_cik=ticker,
                after_date=f"{SEC_CONFIG['start_year']}-01-01",
                before_date=f"{SEC_CONFIG['end_year']}-12-31"
            )
            logging.info(f"✅ Downloaded {ticker} 10-K filings")
        except Exception as e:
            logging.error(f"❌ Failed to download {ticker}: {str(e)}")

if __name__ == "__main__":
    download_sec_filings()