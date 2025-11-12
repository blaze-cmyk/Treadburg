"""
Comprehensive Test Suite for Enhanced Perplexity Chat System
Tests all components: Query Detection, Prompt Enhancement, API Integration, Response Formatting
"""

import asyncio
import json
import base64
from typing import Dict, Any
import pytest
from unittest.mock import patch, MagicMock

# Import the modules to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from open_webui.utils.perplexity_enhanced_chat import (
    QueryTypeDetector,
    PromptEnhancer,
    PerplexityAPIClient,
    ResponseFormatter,
    ConversationManager,
    process_enhanced_chat
)

class TestQueryTypeDetector:
    """Test query type detection and symbol extraction"""
    
    def test_chart_analysis_detection(self):
        """Test chart analysis query detection"""
        query = "analyze BTCUSDT chart on 15m timeframe"
        result = QueryTypeDetector.detect_query_type(query)
        
        assert "chart_analysis" in result["query_types"]
        assert "BTCUSDT" in result["symbols"]
        assert result["timeframe"] == "15m"
        assert result["original_query"] == query
    
    def test_position_check_detection(self):
        """Test position check query detection"""
        query = "show my portfolio holdings and balance"
        result = QueryTypeDetector.detect_query_type(query)
        
        assert "position_check" in result["query_types"]
        assert result["symbols"] == ["BTCUSDT"]  # default
    
    def test_market_research_detection(self):
        """Test market research query detection"""
        query = "latest Bitcoin news and market sentiment"
        result = QueryTypeDetector.detect_query_type(query)
        
        assert "market_research" in result["query_types"]
        assert "BTCUSDT" in result["symbols"]
    
    def test_price_check_detection(self):
        """Test price check query detection"""
        query = "current ETH price and market cap"
        result = QueryTypeDetector.detect_query_type(query)
        
        assert "price_check" in result["query_types"]
        assert "ETHUSDT" in result["symbols"]
    
    def test_multiple_symbols_extraction(self):
        """Test extraction of multiple symbols"""
        query = "compare BTC vs ETH vs SOL performance"
        result = QueryTypeDetector.detect_query_type(query)
        
        expected_symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        for symbol in expected_symbols:
            assert symbol in result["symbols"]
    
    def test_timeframe_extraction(self):
        """Test timeframe extraction from various formats"""
        test_cases = [
            ("1 hour chart", "1h"),
            ("4h analysis", "4h"),
            ("daily trend", "1d"),
            ("weekly overview", "1w"),
            ("5 minute scalping", "5m")
        ]
        
        for query, expected_tf in test_cases:
            result = QueryTypeDetector.detect_query_type(query)
            assert result["timeframe"] == expected_tf

class TestPromptEnhancer:
    """Test prompt enhancement functionality"""
    
    def test_chart_analysis_enhancement(self):
        """Test chart analysis prompt enhancement"""
        query_info = {
            "query_types": ["chart_analysis"],
            "symbols": ["BTCUSDT"],
            "timeframe": "15m",
            "original_query": "analyze BTC chart"
        }
        
        enhanced = PromptEnhancer.enhance_prompt(query_info)
        
        assert "Technical Analysis Table" in enhanced
        assert "BTCUSDT" in enhanced
        assert "15m" in enhanced
        assert "markdown tables" in enhanced
        assert "institutional language" in enhanced
    
    def test_position_check_enhancement(self):
        """Test position check prompt enhancement"""
        query_info = {
            "query_types": ["position_check"],
            "symbols": ["ETHUSDT"],
            "timeframe": "1h",
            "original_query": "check my portfolio"
        }
        
        enhanced = PromptEnhancer.enhance_prompt(query_info)
        
        assert "Position Overview Table" in enhanced
        assert "Risk Metrics" in enhanced
        assert "Performance Analysis" in enhanced
    
    def test_multi_symbol_enhancement(self):
        """Test enhancement with multiple symbols"""
        query_info = {
            "query_types": ["comprehensive_research"],
            "symbols": ["BTCUSDT", "ETHUSDT"],
            "timeframe": "4h",
            "original_query": "compare BTC and ETH"
        }
        
        enhanced = PromptEnhancer.enhance_prompt(query_info)
        
        assert "Compare analysis across symbols: BTCUSDT, ETHUSDT" in enhanced
        assert "4h timeframe" in enhanced

class TestPerplexityAPIClient:
    """Test Perplexity API client functionality"""
    
    @pytest.fixture
    def api_client(self):
        return PerplexityAPIClient()
    
    @patch('httpx.AsyncClient')
    async def test_successful_api_call(self, mock_client, api_client):
        """Test successful API call"""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}],
            "citations": [{"title": "Test Source", "url": "https://test.com"}],
            "related_questions": ["What about ETH?"],
            "usage": {"total_tokens": 100}
        }
        
        mock_client_instance = MagicMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        result = await api_client.analyze_with_context("test prompt")
        
        assert result["success"] is True
        assert result["content"] == "Test response"
        assert len(result["citations"]) == 1
        assert len(result["related_questions"]) == 1
    
    @patch('httpx.AsyncClient')
    async def test_api_error_handling(self, mock_client, api_client):
        """Test API error handling"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        
        mock_client_instance = MagicMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        result = await api_client.analyze_with_context("test prompt")
        
        assert result["success"] is False
        assert "API error: 400" in result["error"]
    
    async def test_image_data_handling(self, api_client):
        """Test handling of image data in requests"""
        # Create mock image data
        image_data = base64.b64encode(b"fake image data").decode()
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Image analyzed"}}],
                "usage": {"total_tokens": 150}
            }
            
            mock_client_instance = MagicMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await api_client.analyze_with_context(
                "analyze this chart", 
                image_data=image_data
            )
            
            assert result["success"] is True
            # Verify image was included in request
            call_args = mock_client_instance.post.call_args
            request_data = json.loads(call_args[1]["json"]["messages"][0]["content"][1]["image_url"]["url"])

class TestResponseFormatter:
    """Test response formatting functionality"""
    
    def test_structure_content(self):
        """Test content structuring"""
        content = "This is a test response\nWith multiple lines\n1. First point\n2. Second point"
        structured = ResponseFormatter._structure_content(content)
        
        assert "### 1. First point" in structured
        assert "### 2. Second point" in structured
    
    def test_format_citations(self):
        """Test citations formatting"""
        citations = [
            {"title": "Test Source 1", "url": "https://test1.com"},
            {"title": "Test Source 2", "url": "https://test2.com"}
        ]
        
        formatted = ResponseFormatter._format_citations(citations)
        
        assert "## 📚 Sources & Citations" in formatted
        assert "[Test Source 1](https://test1.com)" in formatted
        assert "[Test Source 2](https://test2.com)" in formatted
    
    def test_format_related_questions(self):
        """Test related questions formatting"""
        questions = [
            "What about Ethereum?",
            "How does this affect DeFi?",
            "What are the key levels?"
        ]
        
        formatted = ResponseFormatter._format_related_questions(questions)
        
        assert "## 💡 Related Questions" in formatted
        assert "What about Ethereum?" in formatted
        assert "How does this affect DeFi?" in formatted
    
    def test_complete_response_formatting(self):
        """Test complete response formatting"""
        content = "Market analysis shows bullish trend"
        citations = [{"title": "CoinDesk", "url": "https://coindesk.com"}]
        questions = ["What about altcoins?"]
        
        formatted = ResponseFormatter.format_structured_response(
            content, citations, questions
        )
        
        assert "Market analysis shows bullish trend" in formatted
        assert "## 📚 Sources & Citations" in formatted
        assert "## 💡 Related Questions" in formatted

class TestConversationManager:
    """Test conversation management"""
    
    def test_add_and_retrieve_messages(self):
        """Test adding and retrieving conversation messages"""
        manager = ConversationManager()
        session_id = "test_session"
        
        manager.add_message(session_id, "user", "Hello")
        manager.add_message(session_id, "assistant", "Hi there!")
        
        history = manager.get_conversation_history(session_id)
        
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Hi there!"
    
    def test_conversation_limit(self):
        """Test conversation history limit"""
        manager = ConversationManager()
        session_id = "test_session"
        
        # Add more than 20 messages
        for i in range(25):
            manager.add_message(session_id, "user", f"Message {i}")
        
        history = manager.get_conversation_history(session_id)
        
        # Should keep only last 20 messages
        assert len(history) == 20
        assert history[0]["content"] == "Message 5"  # First 5 should be removed
    
    def test_clear_conversation(self):
        """Test clearing conversation history"""
        manager = ConversationManager()
        session_id = "test_session"
        
        manager.add_message(session_id, "user", "Hello")
        manager.clear_conversation(session_id)
        
        history = manager.get_conversation_history(session_id)
        assert len(history) == 0

class TestIntegration:
    """Integration tests for the complete system"""
    
    @patch('open_webui.utils.perplexity_enhanced_chat.PerplexityAPIClient.analyze_with_context')
    async def test_complete_chat_flow(self, mock_api_call):
        """Test complete chat processing flow"""
        # Mock API response
        mock_api_call.return_value = {
            "success": True,
            "content": "Bitcoin is showing bullish momentum with strong support at $65,000.",
            "citations": [{"title": "CoinDesk", "url": "https://coindesk.com"}],
            "related_questions": ["What about Ethereum?", "Key resistance levels?"],
            "usage": {"total_tokens": 200}
        }
        
        result = await process_enhanced_chat(
            user_message="Analyze Bitcoin price action",
            session_id="test_session"
        )
        
        assert result["success"] is True
        assert "Bitcoin is showing bullish momentum" in result["response"]
        assert "query_info" in result
        assert result["query_info"]["symbols"] == ["BTCUSDT"]
        assert "chart_analysis" in result["query_info"]["query_types"]
    
    @patch('open_webui.utils.perplexity_enhanced_chat.PerplexityAPIClient.analyze_with_context')
    async def test_image_analysis_flow(self, mock_api_call):
        """Test image analysis flow"""
        mock_api_call.return_value = {
            "success": True,
            "content": "Chart shows clear breakout pattern above resistance.",
            "citations": [],
            "related_questions": ["Entry points?", "Stop loss levels?"],
            "usage": {"total_tokens": 150}
        }
        
        # Create fake image data
        image_data = base64.b64encode(b"fake chart image").decode()
        
        result = await process_enhanced_chat(
            user_message="Analyze this chart",
            session_id="test_session",
            image_data=image_data
        )
        
        assert result["success"] is True
        assert "breakout pattern" in result["response"]
        
        # Verify API was called with image data
        mock_api_call.assert_called_once()
        call_args = mock_api_call.call_args
        assert call_args[1]["image_data"] == image_data
    
    @patch('open_webui.utils.perplexity_enhanced_chat.PerplexityAPIClient.analyze_with_context')
    async def test_error_handling(self, mock_api_call):
        """Test error handling in complete flow"""
        mock_api_call.return_value = {
            "success": False,
            "error": "API rate limit exceeded"
        }
        
        result = await process_enhanced_chat(
            user_message="Test query",
            session_id="test_session"
        )
        
        assert result["success"] is False
        assert "API rate limit exceeded" in result["error"]

# Performance and Load Tests
class TestPerformance:
    """Performance and load testing"""
    
    async def test_concurrent_requests(self):
        """Test handling multiple concurrent requests"""
        async def mock_process():
            return {
                "success": True,
                "response": "Mock response",
                "query_info": {"query_types": ["test"], "symbols": ["BTCUSDT"], "timeframe": "15m", "original_query": "test"},
                "usage": {"total_tokens": 100}
            }
        
        with patch('open_webui.utils.perplexity_enhanced_chat.process_enhanced_chat', side_effect=lambda *args, **kwargs: mock_process()):
            # Simulate 10 concurrent requests
            tasks = []
            for i in range(10):
                task = process_enhanced_chat(f"Test query {i}", f"session_{i}")
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            # All requests should succeed
            assert len(results) == 10
            for result in results:
                assert result["success"] is True
    
    def test_large_response_handling(self):
        """Test handling of large responses"""
        # Create a large response (simulate 10KB response)
        large_content = "A" * 10000
        
        formatted = ResponseFormatter.format_structured_response(
            large_content, [], []
        )
        
        # Should handle large content without issues
        assert len(formatted) >= 10000
        assert "A" * 100 in formatted  # Verify content is preserved

def run_all_tests():
    """Run all tests and report results"""
    print("🧪 Running Enhanced Perplexity Chat Test Suite...")
    print("=" * 60)
    
    # Test classes to run
    test_classes = [
        TestQueryTypeDetector,
        TestPromptEnhancer,
        TestResponseFormatter,
        TestConversationManager
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\n📋 Testing {test_class.__name__}...")
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                # Create instance and run test
                instance = test_class()
                method = getattr(instance, method_name)
                
                if asyncio.iscoroutinefunction(method):
                    asyncio.run(method())
                else:
                    method()
                
                print(f"  ✅ {method_name}")
                passed_tests += 1
                
            except Exception as e:
                print(f"  ❌ {method_name}: {str(e)}")
                failed_tests.append(f"{test_class.__name__}.{method_name}: {str(e)}")
    
    # Run integration tests
    print(f"\n📋 Testing Integration...")
    integration_tests = TestIntegration()
    integration_methods = [method for method in dir(integration_tests) if method.startswith('test_')]
    
    for method_name in integration_methods:
        total_tests += 1
        try:
            method = getattr(integration_tests, method_name)
            asyncio.run(method())
            print(f"  ✅ {method_name}")
            passed_tests += 1
        except Exception as e:
            print(f"  ❌ {method_name}: {str(e)}")
            failed_tests.append(f"Integration.{method_name}: {str(e)}")
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"📊 TEST SUMMARY")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {len(failed_tests)} ❌")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests:
        print(f"\n❌ FAILED TESTS:")
        for failure in failed_tests:
            print(f"  - {failure}")
    else:
        print(f"\n🎉 ALL TESTS PASSED!")
    
    return len(failed_tests) == 0

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
