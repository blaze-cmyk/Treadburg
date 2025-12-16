"""
Pytest configuration and fixtures
"""
import pytest
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import models FIRST to register them with Base
from models.chat import Chat, Message
from models.user import User

# Import after path setup
from app import app
from database import Base, get_db

# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    # Models are already imported above, so Base.metadata has all tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_chat_data():
    """Sample chat data for testing"""
    return {
        "prompt": "What's the price of AAPL?"
    }

@pytest.fixture
def sample_message_data():
    """Sample message data for testing"""
    return {
        "userPrompt": "Analyze BTC technical indicators"
    }

