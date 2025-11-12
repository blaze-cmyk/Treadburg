"""
Test Perplexity API directly
"""

import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load .env
backend_dir = Path(__file__).parent
load_dotenv(backend_dir / ".env")

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")

print("\n" + "="*70)
print("TESTING PERPLEXITY API DIRECTLY")
print("="*70 + "\n")

if not PERPLEXITY_API_KEY:
    print("❌ PERPLEXITY_API_KEY not found in .env!")
    exit(1)

print(f"✅ API Key: {PERPLEXITY_API_KEY[:20]}...\n")

# Test query
print("📝 Query: What is Bitcoin?")
print("⏳ Calling Perplexity API...\n")

try:
    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Provide concise answers."
                },
                {
                    "role": "user",
                    "content": "What is Bitcoin in 2-3 sentences?"
                }
            ],
            "temperature": 0.2,
            "max_tokens": 500,
            "return_citations": True,
            "return_related_questions": True
        },
        timeout=30
    )
    
    print(f"📊 Status: {response.status_code}\n")
    
    if response.status_code == 200:
        data = response.json()
        
        # Extract content
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        citations = data.get("citations", [])
        
        print("="*70)
        print("RESPONSE:")
        print("="*70)
        print(content)
        
        if citations:
            print("\n📚 Citations:")
            for i, citation in enumerate(citations[:3], 1):
                print(f"  {i}. {citation}")
        
        print("\n✅ Perplexity API is WORKING!")
        
    elif response.status_code == 401:
        print("❌ Authentication Error: Invalid API key!")
        print(f"   Key used: {PERPLEXITY_API_KEY[:20]}...")
    elif response.status_code == 429:
        print("❌ Rate Limit Error: Too many requests!")
    else:
        print(f"❌ Error: HTTP {response.status_code}")
        print(response.text[:500])
        
except requests.exceptions.Timeout:
    print("❌ Timeout: Perplexity API did not respond in 30 seconds")
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "="*70 + "\n")
