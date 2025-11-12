"""
Diagnose why chat is stuck on loading spinner
"""

import requests
import json
import time

API_URL = "http://localhost:8080/api/tradeberg/enforced/chat/completions"

print("\n" + "="*70)
print("DIAGNOSING STUCK LOADING ISSUE")
print("="*70 + "\n")

# Test with the exact same query from the screenshot
request_body = {
    "messages": [
        {
            "role": "user",
            "content": "Build a trading plan for JASMYUSDT 15m with risk management"
        }
    ],
    "model": "tradeberg",
    "stream": False  # Important: non-streaming
}

print("📤 Sending request...")
print(f"Query: {request_body['messages'][0]['content']}")
print(f"Stream: {request_body['stream']}")
print()

start_time = time.time()

try:
    response = requests.post(
        API_URL,
        json=request_body,
        headers={"Content-Type": "application/json"},
        timeout=120  # 2 minute timeout
    )
    
    elapsed = time.time() - start_time
    
    print(f"⏱️  Response time: {elapsed:.1f} seconds")
    print(f"📊 Status: {response.status_code}")
    print(f"📦 Content-Type: {response.headers.get('content-type')}\n")
    
    if response.status_code == 200:
        data = response.json()
        
        print("="*70)
        print("RESPONSE STRUCTURE:")
        print("="*70)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Check if it matches expected format
        print("\n" + "="*70)
        print("FORMAT VALIDATION:")
        print("="*70)
        
        has_choices = "choices" in data
        has_content = False
        content = ""
        
        if has_choices and len(data.get("choices", [])) > 0:
            message = data["choices"][0].get("message", {})
            content = message.get("content", "")
            has_content = bool(content)
        
        print(f"✅ Has 'choices': {has_choices}")
        print(f"✅ Has content: {has_content}")
        print(f"📏 Content length: {len(content)} chars")
        
        if has_content:
            print("\n" + "="*70)
            print("CONTENT:")
            print("="*70)
            print(content[:1000])
            if len(content) > 1000:
                print(f"\n... (showing first 1000 of {len(content)} chars)")
            
            print("\n" + "="*70)
            print("DIAGNOSIS:")
            print("="*70)
            print("✅ Response is VALID and should display")
            print("✅ Frontend should show this content")
            print("\n⚠️  If not displaying, issue is in:")
            print("   1. Frontend JavaScript not reading response correctly")
            print("   2. Browser console shows errors")
            print("   3. Response handling in Chat.svelte")
        else:
            print("\n❌ PROBLEM: No content in response!")
            print("   This will cause loading spinner to stick")
            
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.Timeout:
    elapsed = time.time() - start_time
    print(f"❌ TIMEOUT after {elapsed:.1f} seconds")
    print("   This is why the loading spinner is stuck!")
    print("   Frontend is waiting for response that never comes")
    
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "="*70)
print("NEXT STEPS:")
print("="*70)
print("1. Open browser DevTools (F12)")
print("2. Go to Console tab")
print("3. Look for errors or warnings")
print("4. Check Network tab for the request status")
print("="*70 + "\n")
