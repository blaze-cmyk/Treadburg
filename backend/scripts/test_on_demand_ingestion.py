"""
On-Demand Ingestion Smoke Test
Tests multiple tickers to verify auto-ingestion works end-to-end
"""
import asyncio
import aiohttp
import time
from typing import List, Dict

# Mix of big caps (proven) and mid-caps with confirmed 2024 filings
TICKERS = [
    # Big caps (already proven)
    "AAPL", "F", "TSLA",
    
    # Mid-caps with recent 10-K filings
    "ADBE", "CRM", "TMUS", "LUV", "KHC",
    "WBD", "PARA", "EXPE", "GIS", "KR",
    "RCL", "UAL", "OXY", "BX", "NEM"
]
CREATE_CHAT_URL = "http://localhost:8080/api/chat/create"
CHAT_STREAM_URL = "http://localhost:8080/api/chat/{chat_id}/stream"

async def create_chat(session: aiohttp.ClientSession) -> str:
    """Create a test chat and return its ID"""
    async with session.post(CREATE_CHAT_URL, json={"prompt": ""}) as response:
        data = await response.json()
        return data["chatId"]

async def test_ticker(ticker: str, chat_id: str, session: aiohttp.ClientSession) -> Dict:
    """Test a single ticker and measure latency"""
    payload = {
        "userPrompt": f"What is {ticker} revenue for 2024?",
        "chatId": chat_id
    }
    
    api_url = CHAT_STREAM_URL.format(chat_id=chat_id)
    t0 = time.time()
    try:
        async with session.post(api_url, json=payload) as response:
            text = await response.text()
            latency = round(time.time() - t0, 2)
            
            # Check response quality with numeric detection
            has_numeric_data = "$" in text or "billion" in text.lower() or "million" in text.lower()
            has_data_unavailable = "Data not available" in text
            
            if has_data_unavailable and not has_numeric_data:
                status = "⚠️  NO_DATA"  # Correct "no data" response
            elif has_numeric_data:
                status = "✅ PASS"  # Found revenue numbers
            elif "10-K" in text:
                status = "✅ PASS"  # Has filing references
            else:
                status = "❌ FAIL"  # Unexpected response
            
            preview = text[:120].replace("\n", " ")
            
            return {
                "ticker": ticker,
                "latency": latency,
                "status": status,
                "preview": preview
            }
    except Exception as e:
        return {
            "ticker": ticker,
            "latency": round(time.time() - t0, 2),
            "status": "❌ FAIL",
            "preview": str(e)[:100]
        }

async def run_smoke_test():
    """Run smoke test for all tickers"""
    print("🧪 TradeBerg On-Demand Ingestion Smoke Test\n")
    print("=" * 80)
    
    async with aiohttp.ClientSession() as session:
        # Create a test chat first
        print("Creating test chat...")
        try:
            chat_id = await create_chat(session)
            print(f"✅ Chat created: {chat_id}\n")
        except Exception as e:
            print(f"❌ Failed to create chat: {e}")
            return
        
        # Run tests in parallel
        results = await asyncio.gather(*[
            test_ticker(ticker, chat_id, session) for ticker in TICKERS
        ])
    
    # Print results table
    print(f"\n{'Ticker':<8} {'Latency':<10} {'Status':<12} {'Response Preview'}")
    print("-" * 80)
    
    total_latency = 0
    passed = 0
    no_data = 0
    failed = 0
    
    for result in results:
        print(f"{result['ticker']:<8} {result['latency']}s{' ' * (8-len(str(result['latency'])))} "
              f"{result['status']:<12} {result['preview']}")
        total_latency += result['latency']
        if result['status'] == "✅ PASS":
            passed += 1
        elif result['status'] == "⚠️  NO_DATA":
            no_data += 1
        else:
            failed += 1
    
    # Summary
    print("=" * 80)
    print(f"\n📊 Summary:")
    print(f"   Total Tests: {len(TICKERS)}")
    print(f"   ✅ Passed (with data): {passed}")
    print(f"   ⚠️  No Data (correct): {no_data}")
    print(f"   ❌ Failed: {failed}")
    print(f"   Avg Latency: {round(total_latency/len(TICKERS), 2)}s")
    print(f"   Total Time: {round(total_latency, 2)}s")
    
    if failed == 0:
        print(f"\n✅ All tests passed! On-demand ingestion is fully operational.")
        print(f"   ({passed} tickers returned data, {no_data} correctly reported no data)")
    else:
        print(f"\n⚠️  {failed} tests failed. Check backend logs.")

if __name__ == "__main__":
    asyncio.run(run_smoke_test())
