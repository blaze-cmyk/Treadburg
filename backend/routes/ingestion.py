"""
Ingestion Status API Routes
Provides endpoints to check ingestion status for debugging and monitoring
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models.ingestion import IngestionEvent
from models.document import DocumentChunk
from typing import Optional

router = APIRouter(prefix="/api/ingest", tags=["ingestion"])

@router.get("/status/{ticker}")
async def get_ingestion_status(ticker: str, db: Session = Depends(get_db)):
    """
    Get the latest ingestion status for a ticker
    """
    # Get latest event
    event = db.query(IngestionEvent).filter(
        IngestionEvent.ticker == ticker.upper()
    ).order_by(desc(IngestionEvent.created_at)).first()
    
    # Get chunk count
    chunk_count = db.query(DocumentChunk).filter(
        DocumentChunk.ticker == ticker.upper()
    ).count()
    
    if not event:
        return {
            "ticker": ticker.upper(),
            "status": "not_found",
            "chunk_count": chunk_count,
            "indexed": chunk_count > 0
        }
    
    return {
        "ticker": ticker.upper(),
        "status": event.status,
        "source": event.source,
        "is_priority": event.is_priority,
        "chunk_count": chunk_count,
        "indexed": chunk_count > 0,
        "created_at": event.created_at.isoformat() if event.created_at else None,
        "completed_at": event.completed_at.isoformat() if event.completed_at else None
    }

@router.get("/stats")
async def get_ingestion_stats(db: Session = Depends(get_db)):
    """
    Get overall ingestion statistics
    """
    total_events = db.query(IngestionEvent).count()
    completed = db.query(IngestionEvent).filter(
        IngestionEvent.status == "COMPLETED"
    ).count()
    pending = db.query(IngestionEvent).filter(
        IngestionEvent.status == "PENDING"
    ).count()
    failed = db.query(IngestionEvent).filter(
        IngestionEvent.status == "FAILED"
    ).count()
    
    manual_events = db.query(IngestionEvent).filter(
        IngestionEvent.source == "manual"
    ).count()
    
    total_chunks = db.query(DocumentChunk).count()
    indexed_tickers = db.query(DocumentChunk.ticker).distinct().count()
    
    return {
        "ingestion_events": {
            "total": total_events,
            "completed": completed,
            "pending": pending,
            "failed": failed,
            "manual": manual_events
        },
        "vector_db": {
            "total_chunks": total_chunks,
            "indexed_tickers": indexed_tickers
        }
    }
