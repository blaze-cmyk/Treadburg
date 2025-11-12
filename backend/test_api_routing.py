"""
Test API Routing - Check if Perplexity or OpenAI is being called
This script tests the backend to see which API endpoints are actually being used
"""

import asyncio
import httpx
import json
from datetime import datetime

# Test configuration
BACKEND_URL = "http://localhost:8080"
TEST_QUERIES = [
    {
        "name": "Simple Price Query",
        "query": "what is btc rate in market now?",
        "expected_api": "Perplexity (text query)"
    },
    {
        "name": "Analysis Query",
        "query": "analyze bitcoin with latest news",
        "expected_api": "Perplexity (text query)"
    },
    {
        "name": "Market Update",
        "query": "give me market update",
        "expected_api": "Perplexity (text query)"
    }
]

async def test_api_call(query_name: str, query: str, expected_api: str):
    """Test a single query and track which API is called"""
    
    print(f"\n{'='*80}")
    print(f"TEST: {query_name}")
    print(f"{'='*80}")
    print(f"📝 Query: {query}")
    print(f"🎯 Expected API: {expected_api}")
    print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Prepare request
    payload = {
        "model": "tradeberg-unified",
        "messages": [
            {
                "role": "user",
                "content": query
            }
        ],
        "stream": False
    }
    
    try:
        print(f"\n📤 Sending request to: {BACKEND_URL}/api/tradeberg/enforced/chat/completions")
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Make the request
            start_time = asyncio.get_event_loop().time()
            response = await client.post(
                f"{BACKEND_URL}/api/tradeberg/enforced/chat/completions",
                json=payload
            )
            end_time = asyncio.get_event_loop().time()
            
            response_time = end_time - start_time
            
            print(f"\n📊 Response Status: {response.status_code}")
            print(f"⏱️  Response Time: {response_time:.2f} seconds")
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract response content
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                print(f"\n✅ SUCCESS!")
                print(f"📏 Content Length: {len(content)} characters")
                print(f"\n📄 Content Preview (first 500 chars):")
                print("-" * 80)
                print(content[:500])
                if len(content) > 500:
                    print(f"\n... (showing first 500 of {len(content)} chars)")
                print("-" * 80)
                
                # Analyze response to determine which API was used
                print(f"\n🔍 API DETECTION:")
                
                # Check for Perplexity indicators
                has_citations = "[1]" in content or "[2]" in content or "Sources:" in content
                has_structured_format = "##" in content or "|" in content
                has_emojis = any(emoji in content for emoji in ["📊", "📈", "📉", "💰", "🟢", "🔴"])
                
                # Check for OpenAI Vision indicators
                has_image_analysis = "chart" in content.lower() and "analysis" in content.lower()
                
                print(f"   Citations present: {'✅ YES' if has_citations else '❌ NO'}")
                print(f"   Structured format: {'✅ YES' if has_structured_format else '❌ NO'}")
                print(f"   Emojis present: {'✅ YES' if has_emojis else '❌ NO'}")
                print(f"   Image analysis: {'✅ YES' if has_image_analysis else '❌ NO'}")
                
                # Determine which API was likely used
                if has_citations or has_structured_format:
                    detected_api = "🟢 Perplexity API"
                elif has_image_analysis:
                    detected_api = "🔵 OpenAI Vision API"
                else:
                    detected_api = "⚠️  Unknown (possibly OpenAI GPT)"
                
                print(f"\n🎯 Detected API: {detected_api}")
                print(f"   Expected: {expected_api}")
                
                if "Perplexity" in detected_api and "Perplexity" in expected_api:
                    print(f"   ✅ CORRECT - Perplexity was called as expected!")
                elif "OpenAI" in detected_api and "OpenAI" in expected_api:
                    print(f"   ✅ CORRECT - OpenAI was called as expected!")
                else:
                    print(f"   ⚠️  MISMATCH - Different API than expected")
                
                # Check model info
                model_used = data.get("model", "unknown")
                print(f"\n📦 Model Info:")
                print(f"   Model ID: {model_used}")
                
                # Check usage/tokens
                usage = data.get("usage", {})
                if usage:
                    print(f"   Tokens: {usage.get('total_tokens', 'N/A')}")
                
                return {
                    "success": True,
                    "api_detected": detected_api,
                    "response_time": response_time,
                    "content_length": len(content),
                    "has_citations": has_citations,
                    "has_structured_format": has_structured_format
                }
                
            else:
                print(f"\n❌ ERROR Response")
                print(f"Status: {response.status_code}")
                print(f"Body: {response.text[:500]}")
                
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "response_time": response_time
                }
                
    except asyncio.TimeoutError:
        print(f"\n⏰ TIMEOUT - Request took longer than 120 seconds")
        return {
            "success": False,
            "error": "Timeout after 120s"
        }
    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

async def run_all_tests():
    """Run all test queries"""
    
    print("\n" + "="*80)
    print("🧪 TRADEBERG API ROUTING TEST")
    print("="*80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Tests: {len(TEST_QUERIES)}")
    
    results = []
    
    for test in TEST_QUERIES:
        result = await test_api_call(
            test["name"],
            test["query"],
            test["expected_api"]
        )
        results.append({
            "name": test["name"],
            "query": test["query"],
            **result
        })
        
        # Wait a bit between tests to avoid rate limits
        await asyncio.sleep(2)
    
    # Print summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    success_count = sum(1 for r in results if r.get("success"))
    total_count = len(results)
    
    print(f"\nTotal Tests: {total_count}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total_count - success_count}")
    
    print(f"\n{'Test Name':<30} {'Status':<15} {'API Detected':<30} {'Time':<10}")
    print("-" * 90)
    
    for result in results:
        status = "✅ PASS" if result.get("success") else "❌ FAIL"
        api = result.get("api_detected", result.get("error", "Unknown"))[:28]
        time_str = f"{result.get('response_time', 0):.2f}s" if result.get("response_time") else "N/A"
        
        print(f"{result['name']:<30} {status:<15} {api:<30} {time_str:<10}")
    
    # Check if Perplexity is being used
    perplexity_count = sum(1 for r in results if "Perplexity" in str(r.get("api_detected", "")))
    
    print("\n" + "="*80)
    print("🎯 VERDICT")
    print("="*80)
    
    if perplexity_count == total_count:
        print("✅ ALL QUERIES USING PERPLEXITY API - Perfect!")
    elif perplexity_count > 0:
        print(f"⚠️  MIXED - {perplexity_count}/{total_count} queries using Perplexity")
    else:
        print("❌ NO PERPLEXITY CALLS DETECTED - Check configuration!")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    print("\n🚀 Starting API Routing Tests...")
    print("Make sure backend is running on http://localhost:8080")
    print("\nPress Ctrl+C to cancel\n")
    
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
