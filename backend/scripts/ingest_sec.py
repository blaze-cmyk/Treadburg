import asyncio
import argparse
import sys
import os

# Add backend directory to path so we can import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ingest_service import ingest_service

async def main():
    parser = argparse.ArgumentParser(description='Ingest SEC filings for a ticker')
    parser.add_argument('--ticker', type=str, required=True, help='Ticker symbol (e.g. TSLA)')
    args = parser.parse_args()
    
    ticker = args.ticker.upper()
    print(f"Starting ingestion for {ticker}...")
    
    try:
        await ingest_service.ingest_ticker(ticker)
        print("Done!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
