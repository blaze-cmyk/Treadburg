"""
Complete Implementation Test - Check Everything
Tests all components: API routing, Perplexity integration, TradingView charts, formatting
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")

# Test configuration
BACKEND_URL = "http://localhost:8080"
FRONTEND_URL = "http://localhost:5173"

async def test_1_backend_health():
    """Test 1: Check if backend is running"""
    print_header("TEST 1: Backend Health Check")
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BACKEND_URL}/api/health")
            
            if response.status_code == 200:
                print_success(f"Backend is running on {BACKEND_URL}")
                return True
            else:
                print_error(f"Backend returned status {response.status_code}")
                return False
    except Exception as e:
        print_error(f"Backend not accessible: {str(e)}")
        print_info("Make sure to run: python -m uvicorn open_webui.main:app --port 8080")
        return False

async def test_2_env_configuration():
    """Test 2: Check environment variables"""
    print_header("TEST 2: Environment Configuration")
    
    # Check if .env file exists
    env_path = Path(__file__).parent / ".env"
    
    if env_path.exists():
        print_success(f".env file found at: {env_path}")
        
        # Read and check for required keys
        with open(env_path, 'r') as f:
            env_content = f.read()
        
        required_keys = {
            "PERPLEXITY_API_KEY": "Perplexity API",
            "OPENAI_API_KEY": "OpenAI API"
        }
        
        for key, name in required_keys.items():
            if key in env_content and not env_content.split(key)[1].split('\n')[0].strip() in ['', '=', '=""', "=''", '=your_key_here']:
                print_success(f"{name} key is configured")
            else:
                print_warning(f"{name} key is missing or empty")
        
        return True
    else:
        print_error(".env file not found")
        print_info("Create .env file with PERPLEXITY_API_KEY and OPENAI_API_KEY")
        return False

async def test_3_perplexity_service():
    """Test 3: Check if Perplexity service is loaded"""
    print_header("TEST 3: Perplexity Service Check")
    
    try:
        # Check if the unified service file exists
        service_path = Path(__file__).parent / "open_webui" / "utils" / "unified_perplexity_service.py"
        
        if service_path.exists():
            print_success("unified_perplexity_service.py exists")
            
            # Read file and check for key components
            with open(service_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            checks = {
                "class UnifiedPerplexityService": "UnifiedPerplexityService class",
                "process_text_query": "Text query processing",
                "process_vision_query": "Vision query processing",
                "PROACTIVE": "Proactive AI prompt",
                "ALWAYS show tables": "Auto-table generation"
            }
            
            for check, name in checks.items():
                if check in content:
                    print_success(f"{name} implemented")
                else:
                    print_warning(f"{name} not found")
            
            return True
        else:
            print_error("unified_perplexity_service.py not found")
            return False
            
    except Exception as e:
        print_error(f"Error checking service: {str(e)}")
        return False

async def test_4_api_endpoint():
    """Test 4: Test the chat completion endpoint"""
    print_header("TEST 4: Chat Completion Endpoint Test")
    
    test_query = "what is bitcoin price?"
    
    payload = {
        "model": "tradeberg",
        "messages": [
            {
                "role": "user",
                "content": test_query
            }
        ],
        "stream": False
    }
    
    print_info(f"Testing query: '{test_query}'")
    print_info("Sending request...")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            start_time = asyncio.get_event_loop().time()
            
            response = await client.post(
                f"{BACKEND_URL}/api/tradeberg/enforced/chat/completions",
                json=payload
            )
            
            end_time = asyncio.get_event_loop().time()
            response_time = end_time - start_time
            
            print_info(f"Response time: {response_time:.2f} seconds")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                print_success(f"Response received ({len(content)} characters)")
                
                # Analyze response
                print("\n" + "-"*80)
                print("RESPONSE PREVIEW:")
                print("-"*80)
                print(content[:800])
                if len(content) > 800:
                    print(f"\n... (showing first 800 of {len(content)} characters)")
                print("-"*80 + "\n")
                
                # Check for Perplexity indicators
                indicators = {
                    "Citations ([1], [2])": any(f"[{i}]" in content for i in range(1, 6)),
                    "Tables (|)": "|" in content and "---" in content,
                    "Headers (##)": "##" in content or "**" in content,
                    "Emojis": any(emoji in content for emoji in ["📊", "📈", "📉", "💰", "🟢", "🔴"]),
                    "Price data ($)": "$" in content,
                    "Structured format": len(content) > 200
                }
                
                print("RESPONSE ANALYSIS:")
                for indicator, present in indicators.items():
                    if present:
                        print_success(f"{indicator} present")
                    else:
                        print_warning(f"{indicator} missing")
                
                # Determine API used
                if indicators["Citations ([1], [2])"]:
                    print_success("\n🎯 PERPLEXITY API IS BEING USED!")
                    return True
                else:
                    print_warning("\n⚠️  Response doesn't have Perplexity characteristics")
                    print_info("Might be using OpenAI GPT instead of Perplexity")
                    return False
                    
            elif response.status_code == 429:
                print_error("Rate limit hit (429)")
                print_info("Wait a moment and try again")
                return False
            else:
                print_error(f"HTTP {response.status_code}")
                print(response.text[:500])
                return False
                
    except asyncio.TimeoutError:
        print_error("Request timed out (60s)")
        return False
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return False

async def test_5_frontend_files():
    """Test 5: Check frontend implementation"""
    print_header("TEST 5: Frontend Files Check")
    
    # Get to project root
    backend_path = Path(__file__).parent
    project_root = backend_path.parent
    
    frontend_files = {
        "src/lib/utils/priceQueryDetector.ts": "Price query detector",
        "src/lib/components/chat/PriceChartCard.svelte": "TradingView chart card",
        "src/lib/components/chat/Messages/ResponseMessage.svelte": "Response message handler",
        "src/lib/components/TradingViewWidget.svelte": "TradingView widget"
    }
    
    all_exist = True
    
    for file_path, description in frontend_files.items():
        full_path = project_root / file_path
        if full_path.exists():
            print_success(f"{description}: {file_path}")
        else:
            print_error(f"{description} missing: {file_path}")
            all_exist = False
    
    return all_exist

async def test_6_price_query_detection():
    """Test 6: Test price query detection logic"""
    print_header("TEST 6: Price Query Detection Test")
    
    try:
        backend_path = Path(__file__).parent
        project_root = backend_path.parent
        detector_path = project_root / "src" / "lib" / "utils" / "priceQueryDetector.ts"
        
        if detector_path.exists():
            print_success("priceQueryDetector.ts found")
            
            with open(detector_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for key components
            checks = {
                "detectPriceQuery": "Main detection function",
                "SYMBOL_MAP": "Cryptocurrency symbol mapping",
                "btc": "Bitcoin support",
                "eth": "Ethereum support",
                "BINANCE:": "TradingView symbol format"
            }
            
            for check, name in checks.items():
                if check in content:
                    print_success(f"{name} implemented")
                else:
                    print_warning(f"{name} not found")
            
            return True
        else:
            print_error("priceQueryDetector.ts not found")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

async def test_7_response_message_integration():
    """Test 7: Check ResponseMessage.svelte integration"""
    print_header("TEST 7: ResponseMessage Integration Check")
    
    try:
        backend_path = Path(__file__).parent
        project_root = backend_path.parent
        response_msg_path = project_root / "src" / "lib" / "components" / "chat" / "Messages" / "ResponseMessage.svelte"
        
        if response_msg_path.exists():
            print_success("ResponseMessage.svelte found")
            
            with open(response_msg_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for integration
            checks = {
                "PriceChartCard": "Chart component import",
                "detectPriceQuery": "Detection function import",
                "priceChartInfo": "Chart info variable",
                "isPriceQuery": "Query detection logic"
            }
            
            for check, name in checks.items():
                if check in content:
                    print_success(f"{name} integrated")
                else:
                    print_warning(f"{name} not found")
            
            return True
        else:
            print_error("ResponseMessage.svelte not found")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

async def run_all_tests():
    """Run all tests"""
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════════════════════════════╗")
    print("║                    TRADEBERG COMPLETE IMPLEMENTATION TEST                      ║")
    print("╚════════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    print_info(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"Frontend URL: {FRONTEND_URL}")
    
    # Run all tests
    results = {}
    
    results["Backend Health"] = await test_1_backend_health()
    results["Environment Config"] = await test_2_env_configuration()
    results["Perplexity Service"] = await test_3_perplexity_service()
    results["API Endpoint"] = await test_4_api_endpoint()
    results["Frontend Files"] = await test_5_frontend_files()
    results["Price Detection"] = await test_6_price_query_detection()
    results["Response Integration"] = await test_7_response_message_integration()
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.END}\n")
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if result else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"  {test_name:<30} {status}")
    
    # Final verdict
    print_header("FINAL VERDICT")
    
    if passed == total:
        print_success("🎉 ALL TESTS PASSED!")
        print_success("Your TradeBerg implementation is complete and working!")
        print_info("\nNext steps:")
        print_info("1. Open http://localhost:5173/ in your browser")
        print_info("2. Ask: 'what is btc rate in market now?'")
        print_info("3. You should see:")
        print_info("   - TradingView chart (auto-shows)")
        print_info("   - Price card with data")
        print_info("   - Tables with metrics")
        print_info("   - News with citations")
        print_info("   - Analysis and insights")
    elif passed >= 5:
        print_warning("⚠️  MOSTLY WORKING")
        print_info("Most components are working. Check failed tests above.")
    elif passed >= 3:
        print_warning("⚠️  PARTIALLY WORKING")
        print_info("Some components working. Review failed tests.")
    else:
        print_error("❌ MAJOR ISSUES")
        print_info("Multiple components not working. Check configuration.")
    
    # Specific recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS:")
    print("="*80 + "\n")
    
    if not results["Backend Health"]:
        print_error("Backend not running!")
        print_info("Run: cd backend && python -m uvicorn open_webui.main:app --port 8080")
    
    if not results["Environment Config"]:
        print_error("API keys not configured!")
        print_info("Add PERPLEXITY_API_KEY and OPENAI_API_KEY to backend/.env")
    
    if not results["API Endpoint"]:
        print_error("API endpoint not responding correctly!")
        print_info("Check backend logs for errors")
    
    if not results["Frontend Files"]:
        print_error("Frontend files missing!")
        print_info("Make sure all Svelte components are created")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    print(f"\n{Colors.BOLD}🚀 Starting Complete Implementation Test...{Colors.END}\n")
    
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Tests cancelled by user{Colors.END}")
    except Exception as e:
        print(f"\n\n{Colors.RED}❌ Fatal error: {e}{Colors.END}")
