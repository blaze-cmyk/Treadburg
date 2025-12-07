"""
Integration tests for full chat flow
"""
import pytest
from fastapi.testclient import TestClient

class TestChatIntegration:
    """Integration tests for complete chat workflows"""
    
    def test_complete_chat_flow(self, client: TestClient):
        """Test complete chat creation and messaging flow"""
        # 1. Create a chat
        create_response = client.post(
            "/api/chat/create",
            json={"prompt": "What's the price of AAPL?"}
        )
        assert create_response.status_code == 200
        chat_id = create_response.json()["chatId"]
        
        # 2. Get the chat
        get_chat_response = client.get(f"/api/chat/{chat_id}")
        assert get_chat_response.status_code == 200
        chat_data = get_chat_response.json()
        assert chat_data["id"] == chat_id
        assert chat_data["title"] == "New Chat"
        
        # 3. Get initial messages
        messages_response = client.get(f"/api/chat/{chat_id}/messages")
        assert messages_response.status_code == 200
        messages = messages_response.json()
        assert len(messages) >= 1  # At least the initial user message
        assert messages[0]["role"] == "user"
        
        # 4. Send a message and get streaming response
        stream_response = client.post(
            f"/api/chat/{chat_id}/stream",
            json={"userPrompt": "Analyze BTC technical indicators"},
            stream=True
        )
        assert stream_response.status_code == 200
        
        # Read the stream
        content = b""
        for chunk in stream_response.iter_bytes():
            content += chunk
        
        assert len(content) > 0
        
        # 5. Get updated messages (should include assistant response)
        updated_messages_response = client.get(f"/api/chat/{chat_id}/messages")
        assert updated_messages_response.status_code == 200
        updated_messages = updated_messages_response.json()
        assert len(updated_messages) >= 2  # User + Assistant
        
        # Verify roles
        roles = [msg["role"] for msg in updated_messages]
        assert "user" in roles
        assert "assistant" in roles
    
    def test_multiple_chats_isolation(self, client: TestClient):
        """Test that multiple chats are isolated"""
        # Create two chats
        chat1_response = client.post("/api/chat/create", json={"prompt": "Chat 1"})
        chat2_response = client.post("/api/chat/create", json={"prompt": "Chat 2"})
        
        chat1_id = chat1_response.json()["chatId"]
        chat2_id = chat2_response.json()["chatId"]
        
        assert chat1_id != chat2_id
        
        # Send messages to each
        client.post(
            f"/api/chat/{chat1_id}/stream",
            json={"userPrompt": "Message to chat 1"},
            stream=True
        )
        client.post(
            f"/api/chat/{chat2_id}/stream",
            json={"userPrompt": "Message to chat 2"},
            stream=True
        )
        
        # Verify messages are isolated
        messages1 = client.get(f"/api/chat/{chat1_id}/messages").json()
        messages2 = client.get(f"/api/chat/{chat2_id}/messages").json()
        
        # Each chat should have its own messages
        assert len(messages1) >= 2
        assert len(messages2) >= 2
        
        # Messages should be different
        assert messages1 != messages2
    
    def test_chat_listing_order(self, client: TestClient):
        """Test that chats are listed in correct order (newest first)"""
        # Create multiple chats
        chat_ids = []
        for i in range(3):
            response = client.post("/api/chat/create", json={"prompt": f"Chat {i}"})
            chat_ids.append(response.json()["chatId"])
        
        # Get all chats
        all_chats = client.get("/api/chat").json()
        
        # Verify order (should be newest first)
        assert len(all_chats) == 3
        # The last created chat should be first
        assert all_chats[0]["id"] == chat_ids[2]

