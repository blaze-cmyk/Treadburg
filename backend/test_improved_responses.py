"""
Test the improved response formatting
Shows before/after comparison
"""

import requests
import json

API_URL = "http://localhost:8080/api/tradeberg/enforced/chat/completions"

def test_improved_response():
    """Test with a simple query to see improved formatting"""
    
    print("\n" + "="*60)
    print("TESTING IMPROVED RESPONSE FORMAT")
    print("="*60 + "\n")
    
    test_query = "What is the current Bitcoin price and should I buy?"
    
    print(f"📝 Query: {test_query}\n")
    print("⏳ Sending request...\n")
    
    try:
        response = requests.post(
            API_URL,
            json={
                "messages": [
                    {
                        "role": "user",
                        "content": test_query
                    }
                ]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            print("="*60)
            print("RESPONSE:")
            print("="*60)
            print(content)
            print("\n" + "="*60)
            
            # Check for improved features
            print("\n✅ QUALITY CHECKS:")
            print(f"  • Contains emojis: {'✅' if any(c in content for c in ['📊', '📈', '💡', '📚']) else '❌'}")
            print(f"  • Has sections: {'✅' if '##' in content else '❌'}")
            print(f"  • Has sources: {'✅' if 'Sources' in content or '📚' in content else '❌'}")
            print(f"  • Has related questions: {'✅' if 'You Might Also Ask' in content or '🔍' in content else '❌'}")
            print(f"  • Has tables: {'✅' if '|' in content else '❌'}")
            print(f"  • Response length: {len(content)} characters")
            
            # Save to file for review
            with open("improved_response_sample.txt", "w", encoding="utf-8") as f:
                f.write(content)
            print("\n📄 Full response saved to: improved_response_sample.txt")
            
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_improved_response()
