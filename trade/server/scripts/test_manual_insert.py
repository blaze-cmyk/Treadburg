import sys
import os
import json
from sqlalchemy.orm import Session

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.document import DocumentChunk

def test_insert():
    db = SessionLocal()
    try:
        print("🧪 Testing Manual Insertion...")
        
        # Create a dummy chunk
        meta = {"page": 99, "test": True}
        chunk = DocumentChunk(
            ticker="TEST_MANUAL",
            content="Manual test content",
            embedding=[0.0] * 768,
            source="Manual",
            chunk_index=0,
            metadata_=json.dumps(meta)
        )
        
        db.add(chunk)
        db.commit()
        print("   ✅ Inserted chunk.")
        
        # Verify
        stored = db.query(DocumentChunk).filter(DocumentChunk.ticker == "TEST_MANUAL").first()
        if stored:
            print(f"   Stored Metadata (Raw): {stored.metadata_}")
            print(f"   Stored Metadata (Prop): {stored.meta}")
            
            if stored.metadata_:
                print("   ✅ Metadata stored successfully!")
            else:
                print("   ❌ Metadata is NULL!")
        else:
            print("   ❌ Chunk not found!")
            
        # Cleanup
        db.delete(stored)
        db.commit()
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_insert()
