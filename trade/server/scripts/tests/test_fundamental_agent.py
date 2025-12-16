"""
Fundamental Agent Verification Script
Tests on-demand ingestion, RAG retrieval, and response formatting.
"""
import asyncio
import aiohttp
import json
import time
import os
from datetime import datetime

API_URL = "http://localhost:8080/api/chat"
LOG_DIR = "logs"

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

async def create_chat(session):
    async with session.post(f"{API_URL}/create", json={"prompt": ""}) as resp:
        data = await resp.json()
        return data["chatId"]

async def test_fundamental_agent():
    print("🧪 Testing Fundamental Agent...")
    results = []
    
    async with aiohttp.ClientSession() as session:
        chat_id = await create_chat(session)
        
        # Test cases: Known indexed ticker vs New ticker
        test_cases = [
            {"ticker": "AAPL", "query": "What is AAPL revenue for 2024?"},
            {"ticker": "KHC", "query": "What is Kraft Heinz revenue for 2024?"} # Mid-cap test
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
                    has_data = "$" in text or "billion" in text.lower() or "million" in text.lower()
                    has_citations = "Source:" in text or "10-K" in text
                    is_no_data = "Data not available" in text
                    
                    status = "PASS" if (has_data and has_citations) or is_no_data else "FAIL"
                    
                    result = {
                        "test": "Fundamental Agent",
                        "ticker": case['ticker'],
                        "duration": round(duration, 2),
                        "status": status,
                        "response_preview": text[:100].replace("\n", " "),
                        "timestamp": datetime.now().isoformat()
                    }
                    results.append(result)
                    print(f"  ✅ {case['ticker']} finished in {duration:.2f}s - {status}")
                    
            except Exception as e:
                print(f"  ❌ {case['ticker']} failed: {e}")
                results.append({
                    "test": "Fundamental Agent",
                    "ticker": case['ticker'],
                    "status": "ERROR",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })

    # Save logs
    filename = f"{LOG_DIR}/{datetime.now().strftime('%Y%m%d')}_fundamental_test.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    print(f"📄 Results saved to {filename}\n")

if __name__ == "__main__":
    asyncio.run(test_fundamental_agent())
