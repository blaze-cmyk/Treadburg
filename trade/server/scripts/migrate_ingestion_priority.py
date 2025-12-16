"""
Database migration to add priority and source tracking to ingestion events.
Run this once to upgrade the schema.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine
from sqlalchemy import text

def migrate():
    db = SessionLocal()
    try:
        print("🔄 Adding source and is_priority columns to ingestion_events...")
        
        # Add source column (rss, manual, backfill)
        db.execute(text("""
            ALTER TABLE ingestion_events 
            ADD COLUMN IF NOT EXISTS source VARCHAR(10) DEFAULT 'rss'
        """))
        
        # Add priority flag
        db.execute(text("""
            ALTER TABLE ingestion_events 
            ADD COLUMN IF NOT EXISTS is_priority BOOLEAN DEFAULT FALSE
        """))
        
        # Create index for priority processing
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_priority_status 
            ON ingestion_events(is_priority DESC, status, created_at)
        """))
        
        db.commit()
        print("✅ Migration complete!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
