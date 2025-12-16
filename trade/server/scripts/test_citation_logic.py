import sys
import os
import asyncio
from sqlalchemy import text

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from services.ingest_service import ingest_service
from models.document import DocumentChunk

async def verify_citations():
    print("🧪 Verifying Citation Logic...")
    
    # 1. Test Ingestion Metadata
    print("\n1️⃣ Testing Metadata Extraction...")
    dummy_text = "A" * 3500 # Should be 2 pages (3000 chars per page)
    chunks = ingest_service._chunk_text(dummy_text)
    
    print(f"   Generated {len(chunks)} chunks.")
    for i, chunk in enumerate(chunks):
        meta = chunk['metadata']
        print(f"   Chunk {i}: Page {meta.get('page')}")
        
    if len(chunks) == 2 and chunks[0]['metadata']['page'] == 1 and chunks[1]['metadata']['page'] == 2:
        print("   ✅ Metadata extraction works!")
    else:
        print("   ❌ Metadata extraction failed.")

    # 2. Test DB Storage
    print("\n2️⃣ Testing DB Storage...")
    ticker = "TEST_CITATION"
    await ingest_service._process_chunks(ticker, chunks, "Test Doc")
    
    db = SessionLocal()
    stored = db.query(DocumentChunk).filter(DocumentChunk.ticker == ticker).all()
    
    if len(stored) == 2:
        # Check if metadata is retrievable
        first = stored[0]
        if first.meta.get('page') == 1:
             print(f"   ✅ DB Storage works! Retrieved Page: {first.meta.get('page')}")
        else:
             print(f"   ❌ DB Storage failed. Meta: {first.meta}")
    else:
        print(f"   ❌ DB Storage failed. Count: {len(stored)}")
    
    db.close()
    
    print("\n✅ Verification Complete.")

if __name__ == "__main__":
    asyncio.run(verify_citations())
