#!/usr/bin/env python3
"""
Test Runner for TradeBerg Enhanced Perplexity System
"""

import sys
import os
import asyncio
from datetime import datetime

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

def test_query_type_detection():
    """Test query type detection"""
    print("🔍 Testing Query Type Detection...")
    
    from open_webui.utils.perplexity_enhanced_chat import QueryTypeDetector
    
    test_cases = [
        ("analyze BTCUSDT chart", ["chart_analysis"], ["BTCUSDT"]),
        ("current ETH price", ["price_check"], ["ETHUSDT"]),
        ("Bitcoin news today", ["market_research"], ["BTCUSDT"]),
        ("my portfolio balance", ["position_check"], ["BTCUSDT"]),
    ]
    
    passed = 0
    for query, expected_types, expected_symbols in test_cases:
        try:
            result = QueryTypeDetector.detect_query_type(query)
            
            # Check if at least one expected type is present
            type_match = any(t in result["query_types"] for t in expected_types)
            # Check if at least one expected symbol is present  
            symbol_match = any(s in result["symbols"] for s in expected_symbols)
            
            if type_match and symbol_match:
                print(f"  ✅ '{query}' -> {result['query_types']}, {result['symbols']}")
                passed += 1
            else:
                print(f"  ❌ '{query}' -> Expected {expected_types}, {expected_symbols} but got {result['query_types']}, {result['symbols']}")
                
        except Exception as e:
            print(f"  ❌ '{query}' -> Error: {e}")
    
    print(f"  📊 Query Detection: {passed}/{len(test_cases)} passed\n")
    return passed == len(test_cases)

def test_prompt_enhancement():
    """Test prompt enhancement"""
    print("✨ Testing Prompt Enhancement...")
    
    from open_webui.utils.perplexity_enhanced_chat import PromptEnhancer
    
    query_info = {
        "query_types": ["chart_analysis"],
        "symbols": ["BTCUSDT"],
        "timeframe": "15m",
        "original_query": "analyze BTC"
    }
    
    try:
        enhanced = PromptEnhancer.enhance_prompt(query_info)
        
        required_elements = [
            "Technical Analysis Table",
            "BTCUSDT",
            "15m",
            "markdown tables",
            "institutional language"
        ]
        
        missing = []
        for element in required_elements:
            if element not in enhanced:
                missing.append(element)
        
        if not missing:
            print(f"  ✅ Prompt enhancement successful")
            print(f"  📝 Enhanced prompt length: {len(enhanced)} chars")
            print(f"  📊 Prompt Enhancement: 1/1 passed\n")
            return True
        else:
            print(f"  ❌ Missing elements: {missing}")
            print(f"  📊 Prompt Enhancement: 0/1 passed\n")
            return False
            
    except Exception as e:
        print(f"  ❌ Prompt enhancement error: {e}")
        print(f"  📊 Prompt Enhancement: 0/1 passed\n")
        return False

def test_response_formatting():
    """Test response formatting"""
    print("📝 Testing Response Formatting...")
    
    from open_webui.utils.perplexity_enhanced_chat import ResponseFormatter
    
    try:
        content = "Bitcoin shows bullish momentum"
        citations = [{"title": "CoinDesk", "url": "https://coindesk.com"}]
        questions = ["What about Ethereum?"]
        
        formatted = ResponseFormatter.format_structured_response(
            content, citations, questions
        )
        
        required_sections = [
            "Bitcoin shows bullish momentum",
            "## 📚 Sources & Citations", 
            "## 💡 Related Questions",
            "[CoinDesk](https://coindesk.com)",
            "What about Ethereum?"
        ]
        
        missing = []
        for section in required_sections:
            if section not in formatted:
                missing.append(section)
        
        if not missing:
            print(f"  ✅ Response formatting successful")
            print(f"  📄 Formatted response length: {len(formatted)} chars")
            print(f"  📊 Response Formatting: 1/1 passed\n")
            return True
        else:
            print(f"  ❌ Missing sections: {missing}")
            print(f"  📊 Response Formatting: 0/1 passed\n")
            return False
            
    except Exception as e:
        print(f"  ❌ Response formatting error: {e}")
        print(f"  📊 Response Formatting: 0/1 passed\n")
        return False

def test_conversation_management():
    """Test conversation management"""
    print("💬 Testing Conversation Management...")
    
    from open_webui.utils.perplexity_enhanced_chat import ConversationManager
    
    try:
        manager = ConversationManager()
        session_id = "test_session"
        
        # Add messages
        manager.add_message(session_id, "user", "Hello")
        manager.add_message(session_id, "assistant", "Hi there!")
        
        # Get history
        history = manager.get_conversation_history(session_id)
        
        if len(history) == 2 and history[0]["content"] == "Hello":
            print(f"  ✅ Conversation management successful")
            print(f"  💾 History length: {len(history)} messages")
            
            # Test clearing
            manager.clear_conversation(session_id)
            cleared_history = manager.get_conversation_history(session_id)
            
            if len(cleared_history) == 0:
                print(f"  ✅ Conversation clearing successful")
                print(f"  📊 Conversation Management: 1/1 passed\n")
                return True
            else:
                print(f"  ❌ Conversation clearing failed")
                print(f"  📊 Conversation Management: 0/1 passed\n")
                return False
        else:
            print(f"  ❌ Conversation management failed")
            print(f"  📊 Conversation Management: 0/1 passed\n")
            return False
            
    except Exception as e:
        print(f"  ❌ Conversation management error: {e}")
        print(f"  📊 Conversation Management: 0/1 passed\n")
        return False

async def test_api_client():
    """Test API client (mock)"""
    print("🌐 Testing API Client...")
    
    from open_webui.utils.perplexity_enhanced_chat import PerplexityAPIClient
    
    try:
        client = PerplexityAPIClient()
        
        # Test client initialization
        if hasattr(client, 'api_key') and hasattr(client, 'base_url'):
            print(f"  ✅ API client initialization successful")
            print(f"  🔑 API key configured: {'Yes' if client.api_key else 'No'}")
            print(f"  🌐 Base URL: {client.base_url}")
            print(f"  📊 API Client: 1/1 passed\n")
            return True
        else:
            print(f"  ❌ API client missing required attributes")
            print(f"  📊 API Client: 0/1 passed\n")
            return False
            
    except Exception as e:
        print(f"  ❌ API client error: {e}")
        print(f"  📊 API Client: 0/1 passed\n")
        return False

def test_frontend_integration():
    """Test frontend TypeScript files exist and are valid"""
    print("🎨 Testing Frontend Integration...")
    
    frontend_files = [
        "src/lib/apis/tradeberg/enhanced-chat.ts",
        "src/lib/test/enhanced-chat.test.ts"
    ]
    
    passed = 0
    for file_path in frontend_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content) > 1000:  # Basic validation
                        print(f"  ✅ {file_path} exists and has content ({len(content)} chars)")
                        passed += 1
                    else:
                        print(f"  ❌ {file_path} exists but seems incomplete")
            except Exception as e:
                print(f"  ❌ {file_path} read error: {e}")
        else:
            print(f"  ❌ {file_path} not found")
    
    print(f"  📊 Frontend Integration: {passed}/{len(frontend_files)} passed\n")
    return passed == len(frontend_files)

async def run_all_tests():
    """Run all tests"""
    print("🧪 TradeBerg Enhanced Perplexity System - Test Suite")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Query Type Detection", test_query_type_detection),
        ("Prompt Enhancement", test_prompt_enhancement),
        ("Response Formatting", test_response_formatting),
        ("Conversation Management", test_conversation_management),
        ("API Client", test_api_client),
        ("Frontend Integration", test_frontend_integration),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed_tests += 1
                
        except Exception as e:
            print(f"  ❌ {test_name} failed with error: {e}\n")
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print(f"Total Test Categories: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {total_tests - passed_tests} ❌")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! System is ready for production.")
        print("\n🚀 Next Steps:")
        print("  1. Start the backend: python -m uvicorn main:app --reload --port 8080")
        print("  2. Access the enhanced chat at: http://localhost:8080")
        print("  3. Test with queries like: 'Analyze Bitcoin price action'")
        print("  4. Upload chart images for visual analysis")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test categories failed. Please review and fix issues.")
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return passed_tests == total_tests

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Test runner error: {e}")
        exit(1)
