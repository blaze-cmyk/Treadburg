"""
Check columns in ingestion_events table.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine
from sqlalchemy import text

def check_columns():
    print(f"🔌 Checking database: {engine.url}")
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'ingestion_events'
        """))
        
        print("📊 Columns in ingestion_events:")
        for row in result:
            print(f"- {row[0]} ({row[1]})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_columns()
