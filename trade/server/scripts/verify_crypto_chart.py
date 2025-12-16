import requests
import json
import sys

BASE_URL = "http://localhost:8080/api"

def verify_crypto_chart():
    # 1. Create Chat
    print("1️⃣  Creating Chat...")
    resp = requests.post(f"{BASE_URL}/chat")
    if resp.status_code != 200:
        print(f"❌ Failed to create chat: {resp.text}")
        sys.exit(1)
    
    chat_id = resp.json()["chatId"]
    print(f"   ✅ Chat Created: {chat_id}")

    # 2. Stream Message
    print("2️⃣  Streaming Message (BTC/USDT)...")
    url = f"{BASE_URL}/chat/{chat_id}/stream"
    payload = {
        "userPrompt": "Analyze BTC/USDT chart structure",
        "chatId": chat_id
    }
    
    # We need to handle streaming response
    full_response = ""
    with requests.post(url, json=payload, stream=True) as r:
        if r.status_code != 200:
            print(f"❌ Stream failed: {r.text}")
            sys.exit(1)
            
        for chunk in r.iter_content(chunk_size=None):
            if chunk:
                full_response += chunk.decode('utf-8')

    print("   ✅ Response Received")
    
    # 3. Verify Content
    print("3️⃣  Verifying Content...")
    
    # Check for json-chart block
    if "```json-chart" in full_response:
        print("   ✅ Found `json-chart` block")
    else:
        print("   ❌ Missing `json-chart` block")
        print(f"DEBUG RESPONSE START:\n{full_response[:500]}\nDEBUG RESPONSE END")
        
    # Check for overlay JSON
    if '"overlay":' in full_response or '"supply_zones":' in full_response:
        print("   ✅ Found `overlay` JSON")
    else:
        print("   ❌ Missing `overlay` JSON")
        
    if "```json-chart" in full_response and '"overlay":' in full_response:
        print("\n🎉 SUCCESS: Crypto Chart & Overlay Verified!")
    else:
        print("\n⚠️  PARTIAL FAILURE: Check logs above.")

if __name__ == "__main__":
    verify_crypto_chart()
