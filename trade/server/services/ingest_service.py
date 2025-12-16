"""
On-Demand Ingestion Service
Allows agents to trigger immediate ingestion when data is missing.
"""
import asyncio
from typing import Optional, Dict
from services.sec_client import sec_client
from core.ingestion.queue_manager import queue_manager
from database import SessionLocal
from models.document import DocumentChunk
from sqlalchemy import func

class IngestService:
    """
    Service for on-demand ingestion of SEC filings.
    """
    
    async def ingest_now(self, ticker: str, form_type: str = "10-K") -> Dict:
        """
        Trigger immediate ingestion for a ticker.
        Returns status and waits for completion.
        """
        print(f"🔥 On-Demand Ingestion triggered for {ticker}")
        
        # 1. Check if already indexed
        if await self._is_indexed(ticker, form_type):
            print(f"✅ {ticker} already indexed")
            return {"status": "already_indexed", "ticker": ticker}
        
        # 2. Fetch latest filing from SEC
        filing = await sec_client.get_recent_filings(ticker, form_type)
        if not filing:
            print(f"❌ No {form_type} found for {ticker}")
            return {"status": "not_found", "ticker": ticker}
        
        # 3. Push to priority queue
        success = queue_manager.push_event(
            ticker=ticker,
            cik=filing["cik"],
            url=filing["url"],
            form_type=form_type,
            filed_at=filing["filed_at"],
            source="manual",  # Mark as user-triggered
            is_priority=True  # Process first
        )
        
        if not success:
            return {"status": "queue_failed", "ticker": ticker}
        
        print(f"📥 {ticker} queued for priority ingestion")
        
        # 4. Wait for completion (with timeout)
        max_wait = 30  # 30 seconds max
        for i in range(max_wait):
            await asyncio.sleep(1)
            if await self._is_indexed(ticker, form_type):
                print(f"✅ {ticker} ingestion complete ({i+1}s)")
                return {"status": "completed", "ticker": ticker, "wait_time": i+1}
        
        print(f"⏱️ {ticker} ingestion timeout (still processing)")
        return {"status": "timeout", "ticker": ticker}
    
    async def _is_indexed(self, ticker: str, form_type: str) -> bool:
        """Check if ticker has chunks in vector DB"""
        # Open a fresh session each time to see committed data from the worker
        db = SessionLocal()
        try:
            count = db.query(DocumentChunk).filter(
                DocumentChunk.ticker == ticker,
                DocumentChunk.source == form_type
            ).count()
            return count > 0
        finally:
            db.close()

ingest_service = IngestService()
