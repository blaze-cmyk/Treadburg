"""
Tests for chat service
"""
import pytest
from services.chat_service import ChatService

class TestChatService:
    """Test chat service functionality"""
    
    @pytest.fixture
    def chat_service(self):
        """Create chat service instance"""
        return ChatService()
    
    @pytest.mark.asyncio
    async def test_stream_response_fallback(self, chat_service):
        """Test streaming fallback response"""
        chunks = []
        async for chunk in chat_service.stream_response("Test prompt"):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        # Join chunks and verify content
        content = "".join(chunks)
        assert len(content) > 0
        assert "TradeBerg" in content or "trading" in content.lower()
    
    @pytest.mark.asyncio
    async def test_stream_response_with_history(self, chat_service):
        """Test streaming with conversation history"""
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        chunks = []
        async for chunk in chat_service.stream_response("What's next?", history):
            chunks.append(chunk)
        
        assert len(chunks) > 0
    
    def test_fallback_response_price_query(self, chat_service):
        """Test fallback response for price queries"""
        response = chat_service._get_fallback_response("What's the price of AAPL?")
        assert "price" in response.lower() or "market" in response.lower()
    
    def test_fallback_response_chart_query(self, chat_service):
        """Test fallback response for chart queries"""
        response = chat_service._get_fallback_response("Show me a chart")
        assert "chart" in response.lower() or "technical" in response.lower()
    
    def test_fallback_response_general_query(self, chat_service):
        """Test fallback response for general queries"""
        response = chat_service._get_fallback_response("Hello")
        assert len(response) > 0
        assert "TradeBerg" in response or "trading" in response.lower()

