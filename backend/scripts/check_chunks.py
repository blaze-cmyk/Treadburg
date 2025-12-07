import sys
import os
from sqlalchemy.orm import Session

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.document import DocumentChunk

def check_chunks(ticker: str):
    db = SessionLocal()
    try:
        chunks = db.query(DocumentChunk).filter(DocumentChunk.ticker == ticker).all()
        print(f"\n📊 Document Chunks for {ticker}:")
        print(f"   Total Chunks: {len(chunks)}")
        
        if chunks:
            print("\n   Sample Chunk 1:")
            print(f"   Source: {chunks[0].source}")
            print(f"   Metadata (Prop): {chunks[0].meta}")
            print(f"   Metadata (Raw): {chunks[0].metadata_}")
            print(f"   Content Preview: {chunks[0].content[:200]}...")
        else:
            print("   ❌ No chunks found!")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_chunks("AAPL")
