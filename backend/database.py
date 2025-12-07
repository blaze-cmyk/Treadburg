"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from config import settings
import os

# Create database directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Create base for all models
Base = declarative_base()

# Create database engine only if not using Supabase REST API
USE_SUPABASE_REST = os.getenv("USE_SUPABASE_REST", "false").lower() == "true"

if USE_SUPABASE_REST:
    print("🔌 Using Supabase REST API (direct PostgreSQL connection disabled)")
    engine = None
    SessionLocal = None
else:
    DATABASE_URL = settings.DATABASE_URL
    engine = create_engine(
        DATABASE_URL,
        echo=False
    )
    print(f"🔌 Database configured: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'local'}")  # Log host/db only for security
    
    # Note: pgvector extension should be enabled via Supabase dashboard or migrations
    # The extension is already enabled via Supabase MCP
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Get database session"""
    if SessionLocal is None:
        # Return None when using Supabase REST API
        yield None
        return
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database - create all tables"""
    # Import models to register them with Base
    from models.chat import Chat, Message
    from models.user import User
    from models.document import DocumentChunk
    from models.ingestion import IngestionStatus
    
    # Create all tables
    Base.metadata.create_all(bind=engine)

