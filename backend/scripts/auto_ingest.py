import asyncio
import sys
import os
import argparse
from datetime import datetime
import time

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, init_db
from models.ingestion import IngestionStatus, IngestionStatusEnum
from services.ingest_service import ingest_service
from services.sec_client import sec_client

async def populate_tickers(db):
    """Fetch all tickers from SEC and add to DB if missing"""
    print("🔄 Fetching full ticker list from SEC...")
    ticker_map = await sec_client._get_ticker_map()
    
    if not ticker_map:
        print("❌ Failed to fetch ticker map")
        return

    print(f"✅ Found {len(ticker_map)} tickers. Checking for new ones...")
    
    # Get existing tickers
    existing = {t[0] for t in db.query(IngestionStatus.ticker).all()}
    
    new_tickers = []
    for ticker, cik in ticker_map.items():
        if ticker not in existing:
            new_tickers.append(
                IngestionStatus(
                    ticker=ticker,
                    cik=cik,
                    status=IngestionStatusEnum.PENDING
                )
            )
    
    if new_tickers:
        print(f"📥 Adding {len(new_tickers)} new tickers to queue...")
        # Add in batches
        batch_size = 1000
        for i in range(0, len(new_tickers), batch_size):
            db.add_all(new_tickers[i:i+batch_size])
            db.commit()
            print(f"   Added batch {i//batch_size + 1}")
    else:
        print("✅ No new tickers to add.")

async def process_queue(limit=None):
    """Process pending tickers"""
    db = SessionLocal()
    try:
        # 1. Populate Queue
        await populate_tickers(db)
        
        count = 0
        while True:
            if limit and count >= limit:
                print(f"🛑 Reached limit of {limit} tickers.")
                break
                
            # 2. Get next pending ticker
            # Prioritize: PENDING, then FAILED (retry logic could go here)
            task = db.query(IngestionStatus).filter(
                IngestionStatus.status == IngestionStatusEnum.PENDING
            ).first()
            
            if not task:
                print("✅ Queue empty. Sleeping for 60s...")
                await asyncio.sleep(60)
                continue
                
            # 3. Mark PROCESSING
            print(f"\n⚙️ Processing {task.ticker} (CIK: {task.cik})...")
            task.status = IngestionStatusEnum.PROCESSING
            task.updated_at = datetime.utcnow()
            db.commit()
            
            # 4. Ingest
            try:
                success = await ingest_service.ingest_ticker(task.ticker)
                
                if success:
                    task.status = IngestionStatusEnum.COMPLETED
                    task.last_ingested_at = datetime.utcnow()
                    task.error_message = None
                    print(f"✅ Successfully indexed {task.ticker}")
                else:
                    task.status = IngestionStatusEnum.FAILED
                    task.error_message = "Ingestion returned False"
                    print(f"❌ Failed to index {task.ticker}")
                    
            except Exception as e:
                task.status = IngestionStatusEnum.FAILED
                task.error_message = str(e)
                print(f"❌ Exception indexing {task.ticker}: {e}")
            
            task.updated_at = datetime.utcnow()
            db.commit()
            count += 1
            
            # Rate limit sleep
            await asyncio.sleep(2)
            
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, help="Limit number of tickers to process")
    args = parser.parse_args()
    
    # Ensure tables exist
    init_db()
    
    asyncio.run(process_queue(limit=args.limit))
