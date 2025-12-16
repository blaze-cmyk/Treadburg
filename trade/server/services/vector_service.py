from sqlalchemy import select
from models.document import DocumentChunk
from services.gemini_service import gemini_service
from database import SessionLocal
from typing import List

class VectorService:
    async def search(self, query: str, ticker: str, limit: int = 3) -> List[DocumentChunk]:
        """
        Search for relevant document chunks using semantic similarity.
        """
        # 1. Embed query
        embedding = await gemini_service.embed_content(query)
        if not embedding:
            return []
            
        # 2. Search DB
        db = SessionLocal()
        try:
            # Use pgvector cosine distance operator <=>
            # Order by distance ascending (closest first)
            stmt = select(DocumentChunk).filter(
                DocumentChunk.ticker == ticker
            ).order_by(
                DocumentChunk.embedding.cosine_distance(embedding)
            ).limit(limit)
            
            results = db.execute(stmt).scalars().all()
            return results
        except Exception as e:
            print(f"Vector search error: {e}")
            return []
        finally:
            db.close()

vector_service = VectorService()
