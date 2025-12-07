from sqlalchemy.orm import Session
from database import SessionLocal
from models.ingestion import IngestionEvent, IngestionStatusEnum
from datetime import datetime
from typing import Optional, List

class QueueManager:
    """
    Simulates a message queue using PostgreSQL.
    """
    
    def push_event(self, ticker: str, cik: str, url: str, form_type: str, filed_at: datetime, 
                   source: str = "rss", is_priority: bool = False) -> bool:
        """
        Push a new ingestion event to the queue.
        Idempotent: If ticker+form+date exists, it updates it.
        source: 'rss', 'manual', or 'backfill'
        is_priority: True for user-triggered on-demand ingestion
        """
        print(f"📥 QueueManager.push_event called for {ticker} (source={source}, priority={is_priority})")
        db: Session = SessionLocal()
        try:
            # Check if exists (deduplication)
            existing = db.query(IngestionEvent).filter(
                IngestionEvent.ticker == ticker,
                IngestionEvent.form_type == form_type,
                IngestionEvent.filed_at == filed_at
            ).first()
            
            if existing:
                # Already exists, maybe update status if failed?
                # For now, just skip if pending/completed
                pass
            else:
                # Create new
                event = IngestionEvent(
                    ticker=ticker,
                    cik=cik,
                    filing_url=url,
                    form_type=form_type,
                    filed_at=filed_at,
                    status=IngestionStatusEnum.PENDING,
                    source=source,
                    is_priority=is_priority
                )
                db.add(event)
            
            db.commit()
            return True
        except Exception as e:
            print(f"Queue Push Error: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    def pop_event(self) -> Optional[IngestionEvent]:
        """
        Pop the next PENDING event and mark it PROCESSING.
        Priority order: is_priority DESC, created_at ASC
        """
        db: Session = SessionLocal()
        try:
            # Find highest priority pending event
            event = db.query(IngestionEvent).filter(
                IngestionEvent.status == IngestionStatusEnum.PENDING
            ).order_by(
                IngestionEvent.is_priority.desc(),  # Priority first
                IngestionEvent.created_at.asc()      # Then oldest
            ).with_for_update(skip_locked=True).first()  # Lock to prevent duplicate processing
            
            if event:
                event.status = IngestionStatusEnum.PROCESSING
                event.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(event)
                # Detach from session to return
                db.expunge(event)
                return event
            return None
        finally:
            db.close()

    def complete_event(self, event_id: str):
        """Mark event as COMPLETED"""
        db: Session = SessionLocal()
        try:
            event = db.query(IngestionEvent).filter(IngestionEvent.id == event_id).first()
            if event:
                event.status = IngestionStatusEnum.COMPLETED
                event.updated_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()

    def fail_event(self, event_id: str, error: str):
        """Mark event as FAILED"""
        db: Session = SessionLocal()
        try:
            event = db.query(IngestionEvent).filter(IngestionEvent.id == event_id).first()
            if event:
                event.status = IngestionStatusEnum.FAILED
                event.error_message = error
                event.updated_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()

queue_manager = QueueManager()
