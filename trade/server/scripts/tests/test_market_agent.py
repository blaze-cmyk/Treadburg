"""
Market Agent Verification Script
Tests market structure analysis and overlay generation.
"""
import asyncio
import aiohttp
import json
import time
import os
from datetime import datetime

API_URL = "http://localhost:8080/api/chat"
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

async def create_chat(session):
    async with session.post(f"{API_URL}/create", json={"prompt": ""}) as resp:
        data = await resp.json()
        return data["chatId"]

async def test_market_agent():
    print("🧪 Testing Market Agent...")
    results = []
    
    async with aiohttp.ClientSession() as session:
        chat_id = await create_chat(session)
        
        # Test cases: Crypto (has historical data) vs Stock (live only)
        test_cases = [
            {"ticker": "BTC", "query": "Analyze BTC chart structure and key levels"},
            {"ticker": "BTC", "query": "Generate a chart for BTC and identify supply zones"}
        ]
        
        for case in test_cases:
            print(f"  Running case: {case['ticker']}...")
            t0 = time.time()
            
            payload = {
                "userPrompt": case['query'],
                "chatId": chat_id
            }
            
            try:
                async with session.post(f"{API_URL}/{chat_id}/stream", json=payload) as resp:
                    text = await resp.text()
                    duration = time.time() - t0
                    
                    # Validation logic
                    has_overlay = "overlay" in text or "supply_zones" in text
                    has_chart = "json-chart" in text
                    
                    status = "PASS" if has_overlay else "FAIL"
                    
                    if status == "FAIL":
                        print(f"    ⚠️ Response Preview: {text[:500]}...")
                    
                    result = {
                        "test": "Market Agent",
                        "ticker": case['ticker'],
                        "duration": round(duration, 2),
                        "status": status,
                        "has_overlay": has_overlay,
                        "has_chart": has_chart,
                        "timestamp": datetime.now().isoformat()
                    }
                    results.append(result)
                    print(f"  ✅ {case['ticker']} finished in {duration:.2f}s - {status}")
                    
            except Exception as e:
                print(f"  ❌ {case['ticker']} failed: {e}")
                results.append({
                    "test": "Market Agent",
                    "ticker": case['ticker'],
                    "status": "ERROR",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })

    # Save logs
    filename = f"{LOG_DIR}/{datetime.now().strftime('%Y%m%d')}_market_test.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    print(f"📄 Results saved to {filename}\n")

if __name__ == "__main__":
    asyncio.run(test_market_agent())
