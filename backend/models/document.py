from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from database import Base
import uuid

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String, index=True)
    content = Column(Text)
    embedding = Column(Vector(768))  # Gemini embeddings are 768 dimensions
    source = Column(String)  # e.g. "10-K FY2023"
    chunk_index = Column(Integer)
    metadata_ = Column("metadata", Text, nullable=True) # JSON string for flexibility (page, section, etc.)

    @property
    def meta(self):
        import json
        if self.metadata_:
            return json.loads(self.metadata_)
        return {}

    @meta.setter
    def meta(self, value):
        import json
        self.metadata_ = json.dumps(value)

    def __repr__(self):
        return f"<DocumentChunk(ticker={self.ticker}, source={self.source}, index={self.chunk_index})>"
