import sys
import os
import asyncio
import argparse
from sqlalchemy.orm import Session

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from services.sec_client import sec_client
from core.ingestion.queue_manager import queue_manager

async def backfill_ticker(ticker: str, form_type: str = "10-K"):
    print(f"🔄 Backfilling {ticker} ({form_type})...")
    
    # 1. Fetch Filing Metadata
    filing = await sec_client.get_recent_filings(ticker, form_type)
    
    if not filing:
        print(f"❌ No recent {form_type} found for {ticker}.")
        return

    print(f"   ✅ Found {form_type} filed on {filing['filed_at']}")
    print(f"   📄 URL: {filing['url']}")
    
    # 2. Push to Queue
    try:
        success = queue_manager.push_event(
            ticker=ticker,
            cik=filing['cik'],
            url=filing['url'],
            form_type=form_type,
            filed_at=filing['filed_at']
        )
        if success:
            print(f"   🚀 Pushed to Queue! (The IngestionWorker should pick this up shortly)")
        else:
            print(f"   ❌ Failed to push to queue (Check logs)")
    except Exception as e:
        print(f"   ❌ Failed to push to queue: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill historical filings")
    parser.add_argument("ticker", help="Ticker symbol (e.g. AAPL)")
    parser.add_argument("--form", default="10-K", help="Form type (default: 10-K)")
    
    args = parser.parse_args()
    
    asyncio.run(backfill_ticker(args.ticker, args.form))
