"""
Test frontend response format - Check if responses display correctly in the UI
"""

import requests
import json
import time

API_URL = "http://localhost:8080/api/tradeberg/enforced/chat/completions"

def test_response_format():
    """Test if response is in correct format for frontend display"""
    
    print("\n" + "="*70)
    print("TESTING FRONTEND RESPONSE FORMAT")
    print("="*70 + "\n")
    
    # Test query
    test_query = "What is the current Bitcoin price?"
    
    print(f"📝 Query: {test_query}\n")
    print("⏳ Sending request to: /api/tradeberg/enforced/chat/completions\n")
    
    try:
        response = requests.post(
            API_URL,
            json={
                "messages": [
                    {
                        "role": "user",
                        "content": test_query
                    }
                ],
                "model": "tradeberg",
                "stream": False
            },
            headers={
                "Content-Type": "application/json"
            },
            timeout=60
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📦 Content-Type: {response.headers.get('content-type')}\n")
        
        if response.status_code == 200:
            # Parse JSON
            try:
                data = response.json()
                
                print("="*70)
                print("RESPONSE STRUCTURE CHECK")
                print("="*70)
                
                # Check OpenAI format
                checks = {
                    "Has 'id' field": "id" in data,
                    "Has 'object' field": "object" in data,
                    "Has 'created' field": "created" in data,
                    "Has 'model' field": "model" in data,
                    "Has 'choices' array": "choices" in data and isinstance(data.get("choices"), list),
                    "Choices not empty": len(data.get("choices", [])) > 0,
                }
                
                for check, result in checks.items():
                    icon = "✅" if result else "❌"
                    print(f"{icon} {check}")
                
                # Extract message content
                if data.get("choices") and len(data["choices"]) > 0:
                    choice = data["choices"][0]
                    message = choice.get("message", {})
                    content = message.get("content", "")
                    
                    print("\n" + "="*70)
                    print("MESSAGE CONTENT")
                    print("="*70)
                    print(f"✅ Role: {message.get('role', 'N/A')}")
                    print(f"✅ Content Length: {len(content)} characters")
                    print(f"✅ Finish Reason: {choice.get('finish_reason', 'N/A')}")
                    
                    print("\n" + "="*70)
                    print("CONTENT PREVIEW")
                    print("="*70)
                    print(content[:500])
                    if len(content) > 500:
                        print(f"\n... (truncated, total {len(content)} chars)")
                    
                    # Check for formatting elements
                    print("\n" + "="*70)
                    print("FORMATTING CHECK")
                    print("="*70)
                    format_checks = {
                        "Contains headers (##)": "##" in content,
                        "Contains emojis": any(emoji in content for emoji in ["📊", "📈", "💡", "📚", "🔍"]),
                        "Contains bullet points": "- " in content or "• " in content,
                        "Contains bold text (**...)": "**" in content,
                        "Contains table (|)": "|" in content,
                        "Contains sections (###)": "###" in content,
                    }
                    
                    for check, result in format_checks.items():
                        icon = "✅" if result else "⚠️"
                        print(f"{icon} {check}")
                    
                    # Save full response for review
                    with open("frontend_response_test.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    with open("frontend_response_content.md", "w", encoding="utf-8") as f:
                        f.write(content)
                    
                    print("\n" + "="*70)
                    print("FILES SAVED")
                    print("="*70)
                    print("✅ Full JSON: frontend_response_test.json")
                    print("✅ Content only: frontend_response_content.md")
                    
                    # Final verdict
                    print("\n" + "="*70)
                    print("VERDICT")
                    print("="*70)
                    
                    if all(checks.values()):
                        print("✅ Response format is CORRECT for frontend display")
                        print("✅ Should work in browser!")
                    else:
                        print("❌ Response format has issues")
                        print("   Check the failed items above")
                    
                else:
                    print("\n❌ No choices in response")
                    print(json.dumps(data, indent=2))
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON Parsing Error: {e}")
                print(f"\nRaw Response:\n{response.text[:1000]}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout (>60s)")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    test_response_format()
