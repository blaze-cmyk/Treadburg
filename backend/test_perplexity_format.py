"""
Test Perplexity-style response formatting
"""
import asyncio
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_perplexity_format():
    """Test the new Perplexity-style format"""
    
    url = "http://localhost:8080/api/tradeberg/enforced/chat/completions"
    
    # Test query
    payload = {
        "model": "tradeberg-unified",
        "messages": [
            {
                "role": "user",
                "content": "what is btc rate in market now?"
            }
        ],
        "stream": False
    }
    
    print("🧪 Testing Perplexity-style format...")
    print(f"📤 Query: {payload['messages'][0]['content']}\n")
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                print("✅ Response received!\n")
                print("=" * 80)
                print(content)
                print("=" * 80)
                
                # Check for expected format elements
                checks = {
                    "Price Card": "**$" in content or "Price:" in content,
                    "Market Overview": "##" in content or "Market" in content,
                    "Table": "|" in content,
                    "Citations": "[" in content and "]" in content,
                    "Emojis": any(emoji in content for emoji in ["📊", "📈", "📉", "💰", "🟢", "🔴"])
                }
                
                print("\n📋 Format Check:")
                for check, passed in checks.items():
                    status = "✅" if passed else "❌"
                    print(f"{status} {check}: {'Present' if passed else 'Missing'}")
                
                # Show citations if present
                if "citations" in data.get("choices", [{}])[0].get("message", {}):
                    citations = data["choices"][0]["message"]["citations"]
                    print(f"\n🔗 Citations found: {len(citations)}")
                    for i, citation in enumerate(citations[:3], 1):
                        print(f"  [{i}] {citation}")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_perplexity_format())
