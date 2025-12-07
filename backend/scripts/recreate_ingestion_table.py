"""
Recreate ingestion_events table with new schema.
This fixes the SQLAlchemy metadata issue.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, Base
from models.ingestion import IngestionEvent
from sqlalchemy import text

def recreate_table():
    print("🔄 Recreating ingestion_events table...")
    
    with engine.connect() as conn:
        # Drop the existing table
        print("❌ Dropping old table...")
        conn.execute(text("DROP TABLE IF EXISTS ingestion_events CASCADE"))
        conn.commit()
        
    # Recreate with correct schema from model
    print("✅ Creating new table with source/is_priority columns...")
    Base.metadata.tables['ingestion_events'].create(engine)
    
    print("✅ Table recreated successfully!")
    print("📊 New schema includes: source, is_priority, completed_at")

if __name__ == "__main__":
    recreate_table()
