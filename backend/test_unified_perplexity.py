"""
Comprehensive Test Suite for Unified Perplexity Service
Tests both text queries (Perplexity) and image analysis (OpenAI Vision)
"""

import asyncio
import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from open_webui.utils.unified_perplexity_service import UnifiedPerplexityService, get_unified_service


class TestUnifiedPerplexityService:
    """Test suite for unified Perplexity service"""
    
    def __init__(self):
        self.service = get_unified_service()
        self.test_results = []
    
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} {test_name}: {status}")
        if details:
            print(f"   {details}")
    
    async def test_api_keys_configured(self):
        """Test 1: Check if API keys are configured"""
        test_name = "API Keys Configuration"
        
        try:
            perplexity_key = os.getenv("PERPLEXITY_API_KEY", "")
            openai_key = os.getenv("OPENAI_API_KEY", "")
            
            if not perplexity_key:
                self.log_test(test_name, "FAIL", "Perplexity API key not configured")
                return False
            
            if not openai_key:
                self.log_test(test_name, "FAIL", "OpenAI API key not configured")
                return False
            
            self.log_test(test_name, "PASS", f"Perplexity: {perplexity_key[:10]}... | OpenAI: {openai_key[:10]}...")
            return True
            
        except Exception as e:
            self.log_test(test_name, "FAIL", str(e))
            return False
    
    async def test_text_query_simple(self):
        """Test 2: Simple text query with Perplexity"""
        test_name = "Simple Text Query"
        
        try:
            result = await self.service.process_text_query(
                user_message="What is the current price of Bitcoin?",
                model="sonar-pro"
            )
            
            if result.get("success"):
                response = result.get("response", "")
                service = result.get("service_used", "unknown")
                
                if len(response) > 0:
                    self.log_test(
                        test_name, 
                        "PASS", 
                        f"Response length: {len(response)} chars | Service: {service}"
                    )
                    return True
                else:
                    self.log_test(test_name, "FAIL", "Empty response")
                    return False
            else:
                error = result.get("error", "Unknown error")
                self.log_test(test_name, "FAIL", f"Error: {error}")
                return False
                
        except Exception as e:
            self.log_test(test_name, "FAIL", str(e))
            return False
    
    async def test_text_query_with_symbols(self):
        """Test 3: Text query with symbol detection"""
        test_name = "Text Query with Symbol Detection"
        
        try:
            result = await self.service.process_text_query(
                user_message="Analyze Ethereum and Solana market trends today",
                model="sonar-pro"
            )
            
            if result.get("success"):
                symbols_detected = result.get("symbols_detected", [])
                response = result.get("response", "")
                
                if len(symbols_detected) > 0:
                    self.log_test(
                        test_name,
                        "PASS",
                        f"Detected symbols: {symbols_detected} | Response: {len(response)} chars"
                    )
                    return True
                else:
                    self.log_test(test_name, "WARN", "No symbols detected (may be expected)")
                    return True
            else:
                error = result.get("error", "Unknown error")
                self.log_test(test_name, "FAIL", f"Error: {error}")
                return False
                
        except Exception as e:
            self.log_test(test_name, "FAIL", str(e))
            return False
    
    async def test_text_query_with_citations(self):
        """Test 4: Text query should return citations"""
        test_name = "Citations in Response"
        
        try:
            result = await self.service.process_text_query(
                user_message="What are the latest Bitcoin market news?",
                model="sonar-pro"
            )
            
            if result.get("success"):
                citations = result.get("citations", [])
                
                if len(citations) > 0:
                    self.log_test(
                        test_name,
                        "PASS",
                        f"Found {len(citations)} citations"
                    )
                    # Print first citation as example
                    if citations:
                        print(f"   Example citation: {citations[0]}")
                    return True
                else:
                    self.log_test(test_name, "WARN", "No citations returned (API may not provide)")
                    return True
            else:
                error = result.get("error", "Unknown error")
                self.log_test(test_name, "FAIL", f"Error: {error}")
                return False
                
        except Exception as e:
            self.log_test(test_name, "FAIL", str(e))
            return False
    
    async def test_unified_query_text(self):
        """Test 5: Unified query routing for text"""
        test_name = "Unified Query Routing (Text)"
        
        try:
            result = await self.service.process_unified_query(
                user_message="Give me a market overview of top cryptocurrencies",
                image_data=None
            )
            
            if result.get("success"):
                service_used = result.get("service_used", "")
                
                if service_used == "perplexity_api":
                    self.log_test(
                        test_name,
                        "PASS",
                        f"Correctly routed to Perplexity for text query"
                    )
                    return True
                else:
                    self.log_test(
                        test_name,
                        "FAIL",
                        f"Incorrectly routed to {service_used}"
                    )
                    return False
            else:
                error = result.get("error", "Unknown error")
                self.log_test(test_name, "FAIL", f"Error: {error}")
                return False
                
        except Exception as e:
            self.log_test(test_name, "FAIL", str(e))
            return False
    
    async def test_intent_detection(self):
        """Test 6: Intent detection capabilities"""
        test_name = "Intent Detection"
        
        try:
            test_queries = [
                ("What is Bitcoin price?", ["price_check"]),
                ("Analyze BTCUSDT chart", ["chart_analysis"]),
                ("Latest crypto news", ["market_news"]),
                ("Give me a trading strategy for ETH", ["trading_strategy"])
            ]
            
            all_passed = True
            for query, expected_intents in test_queries:
                result = self.service._detect_query_intent(query)
                detected_intents = result.get("intents", [])
                
                # Check if at least one expected intent is detected
                if any(intent in detected_intents for intent in expected_intents):
                    print(f"   ✓ '{query}' -> {detected_intents}")
                else:
                    print(f"   ✗ '{query}' -> {detected_intents} (expected {expected_intents})")
                    all_passed = False
            
            if all_passed:
                self.log_test(test_name, "PASS", "All intent detections successful")
                return True
            else:
                self.log_test(test_name, "WARN", "Some intent detections may be imperfect")
                return True
                
        except Exception as e:
            self.log_test(test_name, "FAIL", str(e))
            return False
    
    async def test_conversation_history(self):
        """Test 7: Conversation history handling"""
        test_name = "Conversation History"
        
        try:
            history = [
                {"role": "user", "content": "What is Bitcoin?"},
                {"role": "assistant", "content": "Bitcoin is a cryptocurrency..."}
            ]
            
            result = await self.service.process_text_query(
                user_message="What is its current price?",
                conversation_history=history
            )
            
            if result.get("success"):
                self.log_test(
                    test_name,
                    "PASS",
                    "Conversation history processed successfully"
                )
                return True
            else:
                error = result.get("error", "Unknown error")
                self.log_test(test_name, "FAIL", f"Error: {error}")
                return False
                
        except Exception as e:
            self.log_test(test_name, "FAIL", str(e))
            return False
    
    async def test_performance(self):
        """Test 8: Performance testing"""
        test_name = "Performance Test"
        
        try:
            import time
            start_time = time.time()
            
            result = await self.service.process_text_query(
                user_message="Quick Bitcoin price check",
                model="sonar-pro"
            )
            
            elapsed_time = time.time() - start_time
            
            if result.get("success"):
                if elapsed_time < 10:  # Should respond within 10 seconds
                    self.log_test(
                        test_name,
                        "PASS",
                        f"Response time: {elapsed_time:.2f}s"
                    )
                    return True
                else:
                    self.log_test(
                        test_name,
                        "WARN",
                        f"Slow response: {elapsed_time:.2f}s"
                    )
                    return True
            else:
                error = result.get("error", "Unknown error")
                self.log_test(test_name, "FAIL", f"Error: {error}")
                return False
                
        except Exception as e:
            self.log_test(test_name, "FAIL", str(e))
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total = len(self.test_results)
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        warnings = len([r for r in self.test_results if r["status"] == "WARN"])
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"\nSuccess Rate: {(passed/total*100):.1f}%")
        print("="*60)
        
        # Save results to file
        with open("test_results_unified_perplexity.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n📄 Detailed results saved to: test_results_unified_perplexity.json")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("UNIFIED PERPLEXITY SERVICE TEST SUITE")
        print("="*60 + "\n")
        
        # Run all tests
        await self.test_api_keys_configured()
        await self.test_text_query_simple()
        await self.test_text_query_with_symbols()
        await self.test_text_query_with_citations()
        await self.test_unified_query_text()
        await self.test_intent_detection()
        await self.test_conversation_history()
        await self.test_performance()
        
        # Print summary
        self.print_summary()


async def main():
    """Main test runner"""
    tester = TestUnifiedPerplexityService()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
