import sys
import os
from sqlalchemy import text

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, Base
from models.document import DocumentChunk

def reset_db():
    print("🗑️ Dropping document_chunks table...")
    try:
        # Drop the table
        DocumentChunk.__table__.drop(engine)
        print("✅ Table dropped.")
    except Exception as e:
        print(f"⚠️ Error dropping table (might not exist): {e}")

    print("🔄 Recreating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables recreated.")

if __name__ == "__main__":
    reset_db()
