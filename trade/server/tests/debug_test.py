"""Debug script to check test errors"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app import app
from database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.chat import Chat, Message

# Setup test database
engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False})
Base.metadata.create_all(bind=engine)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = TestingSessionLocal()

def override_get_db():
    yield db

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# Test the endpoint
response = client.get('/api/chat')
print(f'Status: {response.status_code}')
print(f'Response: {response.text}')
if response.status_code != 200:
    try:
        print(f'JSON: {response.json()}')
    except:
        pass

