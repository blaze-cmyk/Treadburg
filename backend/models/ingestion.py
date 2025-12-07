from sqlalchemy import Column, String, DateTime, Text, Enum, Boolean
from database import Base
import enum
import uuid
from datetime import datetime

print("🔄 Loading models/ingestion.py with source/is_priority columns")

class IngestionStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class IngestionStatus(Base):
    __tablename__ = "ingestion_status"

    ticker = Column(String, primary_key=True, index=True)
    cik = Column(String, nullable=True)
    status = Column(String, default=IngestionStatusEnum.PENDING)
    last_ingested_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<IngestionStatus(ticker={self.ticker}, status={self.status})>"

class IngestionEvent(Base):
    __tablename__ = "ingestion_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ticker = Column(String, index=True)
    cik = Column(String, nullable=True)
    filing_url = Column(String, nullable=False)
    form_type = Column(String, nullable=False)
    filed_at = Column(DateTime, nullable=True)
    
    status = Column(String, default=IngestionStatusEnum.PENDING)
    error_message = Column(Text, nullable=True)
    
    # Priority and source tracking
    source = Column(String, default="rss")  # rss, manual, backfill
    is_priority = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<IngestionEvent(ticker={self.ticker}, form={self.form_type}, status={self.status})>"
