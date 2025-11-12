"""
Simple API Test for Unified Perplexity Integration
Tests the API endpoint directly without heavy imports
"""

import requests
import json
import time
import os
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

API_BASE_URL = "http://localhost:8080/api/tradeberg"

class SimpleAPITester:
    def __init__(self):
        self.results = []
        self.base_url = API_BASE_URL
    
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} {test_name}: {status}")
        if details:
            print(f"   {details}")
    
    def test_backend_running(self):
        """Test 1: Check if backend is running"""
        test_name = "Backend Server Status"
        
        try:
            response = requests.get(f"{self.base_url}/test", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(test_name, "PASS", f"Backend is running: {data.get('message', 'OK')}")
                return True
            else:
                self.log_test(test_name, "FAIL", f"HTTP {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.log_test(test_name, "FAIL", "Cannot connect to backend. Is it running on port 8080?")
            return False
        except Exception as e:
            self.log_test(test_name, "FAIL", str(e))
            return False
    
    def test_api_keys(self):
        """Test 2: Check if API keys are configured"""
        test_name = "API Keys Configuration"
        
        perplexity_key = os.getenv("PERPLEXITY_API_KEY", "")
        openai_key = os.getenv("OPENAI_API_KEY", "")
        
        if not perplexity_key:
            self.log_test(test_name, "FAIL", "PERPLEXITY_API_KEY not found in .env")
            return False
        
        if not openai_key:
            self.log_test(test_name, "FAIL", "OPENAI_API_KEY not found in .env")
            return False
        
        self.log_test(test_name, "PASS", f"Keys configured: Perplexity={perplexity_key[:10]}... OpenAI={openai_key[:10]}...")
        return True
    
    def test_text_query(self):
        """Test 3: Simple text query (should use Perplexity)"""
        test_name = "Text Query (Perplexity)"
        
        try:
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": "What is the current price of Bitcoin?"
                    }
                ],
                "model": "gpt-4o"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/enforced/chat/completions",
                json=payload,
                timeout=30
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if content:
                    # Check if it's using Perplexity
                    is_perplexity = "Perplexity Api" in content or "📊" in content
                    
                    self.log_test(
                        test_name,
                        "PASS",
                        f"Response received in {elapsed:.2f}s | Length: {len(content)} chars | Perplexity: {is_perplexity}"
                    )
                    print(f"   Preview: {content[:100]}...")
                    return True
                else:
                    self.log_test(test_name, "FAIL", "Empty response")
                    return False
            else:
                error = response.json() if response.headers.get('content-type') == 'application/json' else response.text
                self.log_test(test_name, "FAIL", f"HTTP {response.status_code}: {error}")
                return False
                
        except requests.exceptions.Timeout:
            self.log_test(test_name, "FAIL", "Request timeout (>30s)")
            return False
        except Exception as e:
            self.log_test(test_name, "FAIL", str(e))
            return False
    
    def test_financial_query(self):
        """Test 4: Financial query with expected citations"""
        test_name = "Financial Query with Citations"
        
        try:
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": "Give me the latest Bitcoin market news and price analysis"
                    }
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/enforced/chat/completions",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # Check for citations
                has_citations = "📚 Sources:" in content or "Sources:" in content
                has_related = "🔍 Related Questions:" in content or "Related Questions:" in content
                
                details = f"Citations: {has_citations} | Related Questions: {has_related}"
                
                if content:
                    self.log_test(test_name, "PASS", details)
                    return True
                else:
                    self.log_test(test_name, "FAIL", "Empty response")
                    return False
            else:
                self.log_test(test_name, "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test(test_name, "FAIL", str(e))
            return False
    
    def test_conversation_context(self):
        """Test 5: Multi-turn conversation"""
        test_name = "Conversation Context"
        
        try:
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": "What is Ethereum?"
                    },
                    {
                        "role": "assistant",
                        "content": "Ethereum is a blockchain platform..."
                    },
                    {
                        "role": "user",
                        "content": "What is its current price?"
                    }
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/enforced/chat/completions",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if content:
                    self.log_test(test_name, "PASS", "Context-aware response received")
                    return True
                else:
                    self.log_test(test_name, "FAIL", "Empty response")
                    return False
            else:
                self.log_test(test_name, "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test(test_name, "FAIL", str(e))
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total = len(self.results)
        passed = len([r for r in self.results if r["status"] == "PASS"])
        failed = len([r for r in self.results if r["status"] == "FAIL"])
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"\nSuccess Rate: {(passed/total*100):.1f}%")
        print("="*60)
        
        # Save results
        with open("test_results_simple.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Results saved to: test_results_simple.json")
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("UNIFIED PERPLEXITY API TEST SUITE")
        print("="*60 + "\n")
        
        # Run tests
        if not self.test_backend_running():
            print("\n❌ Backend not running. Please start it first:")
            print("   cd backend")
            print("   python -m uvicorn open_webui.main:app --reload --port 8080")
            return
        
        self.test_api_keys()
        self.test_text_query()
        self.test_financial_query()
        self.test_conversation_context()
        
        # Print summary
        self.print_summary()


if __name__ == "__main__":
    tester = SimpleAPITester()
    tester.run_all_tests()
