"""
Test Perplexity API connection
"""
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def test_perplexity():
    """Test if Perplexity API is working"""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    
    if not api_key:
        print("❌ PERPLEXITY_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar-pro",
                    "messages": [
                        {
                            "role": "user",
                            "content": "What is the current Bitcoin price?"
                        }
                    ],
                    "max_tokens": 100,
                    "temperature": 0.2
                }
            )
            
            if response.status_code == 200:
                print("✅ Perplexity API is working!")
                result = response.json()
                print(f"📝 Response: {result['choices'][0]['message']['content'][:100]}...")
                return True
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"📝 Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing Perplexity API: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Perplexity API connection...")
    result = asyncio.run(test_perplexity())
    if result:
        print("\n✅ Perplexity API is configured correctly!")
    else:
        print("\n❌ Perplexity API test failed. Check your API key.")
