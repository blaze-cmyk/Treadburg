"""
Test with explicit query that should trigger proper formatting
"""

import requests
import json

API_URL = "http://localhost:8080/api/tradeberg/enforced/chat/completions"

print("\n" + "="*70)
print("TESTING WITH EXPLICIT QUERY")
print("="*70 + "\n")

request_body = {
    "messages": [
        {
            "role": "user",
            "content": "Give me a detailed analysis of Bitcoin. Include current price, market trends, latest news with sources, and provide the response in a well-formatted structure with sections and bullet points."
        }
    ],
    "model": "tradeberg",
    "stream": False
}

print("📤 Query: Detailed Bitcoin analysis")
print("⏳ Waiting for response...\n")

try:
    response = requests.post(
        API_URL,
        json=request_body,
        headers={"Content-Type": "application/json"},
        timeout=60
    )
    
    print(f"📊 Status: {response.status_code}\n")
    
    if response.status_code == 200:
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        print("="*70)
        print("RESPONSE CONTENT:")
        print("="*70)
        print(content)
        print("\n" + "="*70)
        
        print(f"\n📏 Length: {len(content)} characters")
        print(f"📊 Has ##: {'##' in content}")
        print(f"🎨 Has emojis: {any(e in content for e in ['📊', '📈', '💡', '📚'])}")
        print(f"📚 Has Sources: {'Sources' in content or '📚' in content}")
        
        # Save for review
        with open("explicit_query_response.md", "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n✅ Saved to: explicit_query_response.md")
        
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "="*70 + "\n")
