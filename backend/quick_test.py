"""Quick API test with retry"""
import requests
import time

API_URL = "http://localhost:8080/api/tradeberg/test"
CHAT_URL = "http://localhost:8080/api/tradeberg/enforced/chat/completions"

print("\n🔍 Testing TradeBerg API...\n")

# Test 1: Health check
print("1. Testing backend health...")
for i in range(5):
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Backend is running: {response.json()}")
            break
    except Exception as e:
        print(f"   ⏳ Attempt {i+1}/5: Waiting for backend...")
        time.sleep(2)
else:
    print("   ❌ Backend not responding after 5 attempts")
    exit(1)

# Test 2: Chat with Perplexity
print("\n2. Testing Perplexity integration...")
try:
    response = requests.post(
        CHAT_URL,
        json={
            "messages": [
                {
                    "role": "user",
                    "content": "What is Bitcoin's current price in one sentence?"
                }
            ]
        },
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"   ✅ Response received ({len(content)} chars)")
        print(f"\n   Preview:\n   {content[:200]}...\n")
    else:
        print(f"   ❌ Error: HTTP {response.status_code}")
        print(f"   {response.text[:500]}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n✅ Tests complete!\n")
