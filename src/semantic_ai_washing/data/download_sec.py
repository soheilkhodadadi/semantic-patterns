from pathlib import Path

from sec_edgar_downloader import Downloader
import logging
from semantic_ai_washing.config.config import SEC_CONFIG  # Import your config

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
            # Check if the filing already exists
            ticker_dir = raw_dir / "sec-edgar-filings" / ticker / "10-K"
            if ticker_dir.exists():
                # Check for the full-submission.txt file
                submission_files = list(ticker_dir.glob("**/full-submission.txt"))
                if submission_files:
                    # Check if the file is complete (size > 1 KB)
                    file_size = submission_files[0].stat().st_size  # Size in bytes
                    if file_size > 1024:  # 1 KB = 1024 bytes
                        logging.info(f"✅ Skipping {ticker} (already downloaded)")
                        continue
                    else:
                        logging.warning(f"⚠️ Partial download detected for {ticker}. Re-downloading...")
            
            # Download the filing if it doesn't exist or is incomplete
            dl.get(
                "10-K",  # Filing type
                ticker,   # Ticker or CIK
                after=f"{SEC_CONFIG['start_year']}-01-01",
                before=f"{SEC_CONFIG['end_year']}-12-31"
            )
            logging.info(f"✅ Downloaded {ticker} 10-K filings")
        except Exception as e:
            logging.error(f"❌ Failed to download {ticker}: {str(e)}")

def validate_downloads():
    """
    Validate that the downloaded SEC filings are not empty.
    """
    raw_dir = Path("data/raw/sec_filings")
    
    for ticker in SEC_CONFIG["tickers"]:
        # Check if the ticker's folder exists
        ticker_dir = raw_dir / "sec-edgar-filings" / ticker / "10-K"
        if not ticker_dir.exists():
            raise FileNotFoundError(f"Missing folder for {ticker}")
        
        # Check if the folder contains the full-submission.txt file
        submission_files = list(ticker_dir.glob("**/full-submission.txt"))
        if not submission_files:
            raise ValueError(f"No full-submission.txt file found for {ticker}")
        
        # Check if the file is complete (size > 1 KB)
        file_size = submission_files[0].stat().st_size  # Size in bytes
        if file_size <= 1024:  # 1 KB = 1024 bytes
            raise ValueError(f"Partial download detected for {ticker} (file size: {file_size} bytes)")
        
        logging.info(f"✅ Validated {ticker} 10-K filings (file size: {file_size} bytes)")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    download_sec_filings()
    validate_downloads()  # Add validation after downloading
