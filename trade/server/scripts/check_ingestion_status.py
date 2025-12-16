import sys
import os
import time
from sqlalchemy.orm import Session

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.ingestion import IngestionEvent, IngestionStatusEnum

def check_status():
    db = SessionLocal()
    try:
        events = db.query(IngestionEvent).order_by(IngestionEvent.created_at.desc()).limit(5).all()
        print("\n📊 Recent Ingestion Events:")
        for event in events:
            print(f"   - {event.ticker} ({event.form_type}): {event.status}")
            if event.status == IngestionStatusEnum.FAILED:
                print(f"     ❌ Error: {event.error_message}")
            elif event.status == IngestionStatusEnum.COMPLETED:
                print(f"     ✅ Completed at {event.updated_at}")
    finally:
        db.close()

if __name__ == "__main__":
    check_status()
