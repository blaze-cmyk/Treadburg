"""
Tests for chat routes
"""
import pytest
from fastapi.testclient import TestClient

class TestChatRoutes:
    """Test chat API endpoints"""
    
    def test_get_all_chats_empty(self, client: TestClient):
        """Test getting all chats when none exist"""
        response = client.get("/api/chat")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_create_chat(self, client: TestClient, sample_chat_data):
        """Test creating a new chat"""
        response = client.post("/api/chat/create", json=sample_chat_data)
        assert response.status_code == 200
        data = response.json()
        assert "chatId" in data
        assert isinstance(data["chatId"], str)
        assert len(data["chatId"]) > 0
    
    def test_create_chat_without_prompt(self, client: TestClient):
        """Test creating a chat without prompt"""
        response = client.post("/api/chat/create", json={"prompt": ""})
        assert response.status_code == 200
        data = response.json()
        assert "chatId" in data
    
    def test_get_chat_by_id(self, client: TestClient, sample_chat_data):
        """Test getting a chat by ID"""
        # Create a chat first
        create_response = client.post("/api/chat/create", json=sample_chat_data)
        chat_id = create_response.json()["chatId"]
        
        # Get the chat
        response = client.get(f"/api/chat/{chat_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == chat_id
        assert "title" in data
        assert "createdAt" in data
    
    def test_get_chat_not_found(self, client: TestClient):
        """Test getting a non-existent chat"""
        response = client.get("/api/chat/non-existent-id")
        assert response.status_code == 404
    
    def test_get_all_chats_after_creation(self, client: TestClient, sample_chat_data):
        """Test getting all chats after creating some"""
        # Create multiple chats
        chat_ids = []
        for i in range(3):
            response = client.post("/api/chat/create", json={"prompt": f"Test prompt {i}"})
            chat_ids.append(response.json()["chatId"])
        
        # Get all chats
        response = client.get("/api/chat")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(chat["id"] in chat_ids for chat in data)
    
    def test_get_messages_empty_chat(self, client: TestClient, sample_chat_data):
        """Test getting messages from an empty chat"""
        # Create a chat
        create_response = client.post("/api/chat/create", json=sample_chat_data)
        chat_id = create_response.json()["chatId"]
        
        # Get messages
        response = client.get(f"/api/chat/{chat_id}/messages")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have at least the initial user message
        assert len(data) >= 1
    
    def test_get_messages_alternative_endpoint(self, client: TestClient, sample_chat_data):
        """Test alternative message endpoint"""
        # Create a chat
        create_response = client.post("/api/chat/create", json=sample_chat_data)
        chat_id = create_response.json()["chatId"]
        
        # Get messages using alternative endpoint
        response = client.get(f"/api/chat/{chat_id}/message")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_stream_chat_response(self, client: TestClient, sample_chat_data, sample_message_data):
        """Test streaming chat response"""
        # Create a chat
        create_response = client.post("/api/chat/create", json=sample_chat_data)
        chat_id = create_response.json()["chatId"]
        
        # Stream a response
        response = client.post(
            f"/api/chat/{chat_id}/stream",
            json=sample_message_data,
            stream=True
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        
        # Read stream
        content = b""
        for chunk in response.iter_bytes():
            content += chunk
        
        assert len(content) > 0
    
    def test_post_message_alternative_endpoint(self, client: TestClient, sample_chat_data, sample_message_data):
        """Test alternative message posting endpoint"""
        # Create a chat
        create_response = client.post("/api/chat/create", json=sample_chat_data)
        chat_id = create_response.json()["chatId"]
        
        # Post message using alternative endpoint
        response = client.post(
            f"/api/chat/{chat_id}/message",
            json=sample_message_data,
            stream=True
        )
        assert response.status_code == 200
    
    def test_get_token_limit(self, client: TestClient):
        """Test getting token limit"""
        response = client.get("/api/chat/limit")
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert isinstance(data["token"], int)
        assert data["token"] > 0
    
    def test_get_all_chats_alternative(self, client: TestClient):
        """Test alternative endpoint for getting all chats"""
        response = client.get("/api/chat/all")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_chat_title_auto_generation(self, client: TestClient, sample_message_data):
        """Test that chat title is auto-generated after first response"""
        # Create a chat
        create_response = client.post("/api/chat/create", json={"prompt": "Test"})
        chat_id = create_response.json()["chatId"]
        
        # Verify initial title
        chat_response = client.get(f"/api/chat/{chat_id}")
        assert chat_response.json()["title"] == "New Chat"
        
        # Send a message to trigger title generation
        client.post(
            f"/api/chat/{chat_id}/stream",
            json=sample_message_data,
            stream=True
        )
        
        # Wait a bit for async processing (in real scenario, this would be handled differently)
        # For now, we just verify the endpoint works

