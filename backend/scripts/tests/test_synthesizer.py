"""
Synthesizer Agent Verification Script
Tests parallel execution and response merging (MIXED_CONTEXT).
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

async def test_synthesizer():
    print("🧪 Testing Synthesizer Agent...")
    results = []
    
    async with aiohttp.ClientSession() as session:
        chat_id = await create_chat(session)
        
        # Test case: Mixed intent requiring both agents
        query = "Analyze AAPL fundamentals and chart structure"
        print(f"  Running mixed query: '{query}'...")
        
        t0 = time.time()
        payload = {
            "userPrompt": query,
            "chatId": chat_id
        }
        
        try:
            async with session.post(f"{API_URL}/{chat_id}/stream", json=payload) as resp:
                text = await resp.text()
                duration = time.time() - t0
                
                # Validation logic
                has_fundamentals = any(kw in text.lower() for kw in ["revenue", "earnings", "growth", "financial", "sales", "income"])
                has_technicals = any(kw in text.lower() for kw in ["chart", "zone", "level", "trend", "support", "resistance"])
                has_overlay = "overlay" in text
                
                status = "PASS" if (has_fundamentals and has_technicals) else "FAIL"
                
                if status == "FAIL":
                    print(f"    ⚠️ Response Preview: {text[:500]}...")
                
                result = {
                    "test": "Synthesizer Agent",
                    "query": query,
                    "duration": round(duration, 2),
                    "status": status,
                    "has_fundamentals": has_fundamentals,
                    "has_technicals": has_technicals,
                    "has_overlay": has_overlay,
                    "timestamp": datetime.now().isoformat()
                }
                results.append(result)
                print(f"  ✅ Mixed query finished in {duration:.2f}s - {status}")
                
        except Exception as e:
            print(f"  ❌ Mixed query failed: {e}")
            results.append({
                "test": "Synthesizer Agent",
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

    # Save logs
    filename = f"{LOG_DIR}/{datetime.now().strftime('%Y%m%d')}_synthesizer_test.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    print(f"📄 Results saved to {filename}\n")

if __name__ == "__main__":
    asyncio.run(test_synthesizer())
