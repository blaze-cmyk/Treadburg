"""
Test with detailed logging to see what's happening
"""

import requests
import json

API_URL = "http://localhost:8080/api/tradeberg/enforced/chat/completions"

print("\n" + "="*70)
print("TESTING WITH DETAILED REQUEST/RESPONSE")
print("="*70 + "\n")

request_body = {
    "messages": [
        {
            "role": "user",
            "content": "What is Bitcoin's current price? Include data, sources, and analysis."
        }
    ],
    "model": "tradeberg",
    "stream": False
}

print("📤 REQUEST:")
print(json.dumps(request_body, indent=2))
print("\n" + "="*70 + "\n")

try:
    response = requests.post(
        API_URL,
        json=request_body,
        headers={"Content-Type": "application/json"},
        timeout=90
    )
    
    print(f"📊 Status: {response.status_code}")
    print(f"📦 Content-Type: {response.headers.get('content-type')}")
    print(f"📏 Content-Length: {response.headers.get('content-length')} bytes\n")
    
    if response.status_code == 200:
        data = response.json()
        
        print("="*70)
        print("RESPONSE DATA:")
        print("="*70)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Extract and display content
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        print("\n" + "="*70)
        print("CONTENT ONLY (for readability):")
        print("="*70)
        print(content)
        
        # Analysis
        print("\n" + "="*70)
        print("ANALYSIS:")
        print("="*70)
        print(f"✅ Content length: {len(content)} characters")
        print(f"✅ Has emojis: {any(e in content for e in ['📊', '📈', '💡', '📚', '🔍'])}")
        print(f"✅ Has headers (##): {'##' in content}")
        print(f"✅ Has tables (|): {'|' in content}")
        print(f"✅ Has sources: {'Sources' in content or '📚' in content}")
        print(f"✅ Has related questions: {'You Might Also Ask' in content or '🔍' in content}")
        
        # Check if it's actually using Perplexity
        if len(content) < 300:
            print("\n⚠️  WARNING: Response is very short - might not be using Perplexity!")
            print("   Expected: 500-2000 characters with structured formatting")
            print(f"   Actual: {len(content)} characters")
        
    else:
        print(f"❌ Error Response:")
        print(response.text)
        
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "="*70 + "\n")
