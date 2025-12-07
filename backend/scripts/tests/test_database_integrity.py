"""
Database Integrity Verification Script
Checks document chunks, ingestion events, and vector search.
"""
import sys
import os
import json
from datetime import datetime
from sqlalchemy import text, func

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import SessionLocal
from models.document import DocumentChunk
from models.ingestion import IngestionEvent
from services.vector_service import vector_service
import asyncio

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

async def test_database_integrity():
    print("🧪 Testing Database Integrity...")
    results = {}
    db = SessionLocal()
    
    try:
        # 1. Check Document Chunks
        print("  Checking document chunks...")
        chunk_counts = db.query(DocumentChunk.ticker, func.count(DocumentChunk.id))\
            .group_by(DocumentChunk.ticker).all()
        
        chunks_data = {ticker: count for ticker, count in chunk_counts}
        has_chunks = len(chunks_data) > 0
        print(f"  ✅ Found chunks for {len(chunks_data)} tickers")
        
        # 2. Check Ingestion Events
        print("  Checking ingestion events...")
        event_stats = db.query(
            IngestionEvent.source, 
            IngestionEvent.is_priority, 
            IngestionEvent.status, 
            func.count(IngestionEvent.id)
        ).group_by(IngestionEvent.source, IngestionEvent.is_priority, IngestionEvent.status).all()
        
        events_data = [
            {"source": s, "priority": p, "status": st, "count": c} 
            for s, p, st, c in event_stats
        ]
        print(f"  ✅ Found {len(events_data)} event groups")
        
        # 3. Test Vector Search
        print("  Testing vector search...")
        search_ticker = "AAPL" if "AAPL" in chunks_data else list(chunks_data.keys())[0] if chunks_data else None
        
        vector_status = "SKIP"
        if search_ticker:
            docs = await vector_service.search("revenue", ticker=search_ticker, limit=3)
            vector_status = "PASS" if len(docs) > 0 else "FAIL"
            print(f"  ✅ Vector search for {search_ticker}: Found {len(docs)} chunks")
        else:
            print("  ⚠️ No chunks found to test vector search")
            
        results = {
            "test": "Database Integrity",
            "chunks": chunks_data,
            "ingestion_events": events_data,
            "vector_search": vector_status,
            "status": "PASS" if has_chunks and vector_status != "FAIL" else "FAIL",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"  ❌ Database check failed: {e}")
        results = {
            "test": "Database Integrity",
            "status": "ERROR",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    finally:
        db.close()

    # Save logs
    filename = f"{LOG_DIR}/{datetime.now().strftime('%Y%m%d')}_database_test.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    print(f"📄 Results saved to {filename}\n")

if __name__ == "__main__":
    asyncio.run(test_database_integrity())
