"""
Test Frontend Request - Simulate exact frontend request to debug the issue
"""
import requests
import json

print("\n" + "="*80)
print("🔍 TESTING FRONTEND REQUEST - Debugging OpenAI Error")
print("="*80 + "\n")

# Simulate exact frontend request
payload = {
    "model": "tradeberg",
    "messages": [
        {
            "role": "user",
            "content": "what is the price of btc?"
        }
    ],
    "stream": False
}

print("📝 Request Payload:")
print(json.dumps(payload, indent=2))
print()

print("📤 Sending to: http://localhost:8080/api/tradeberg/enforced/chat/completions")
print()

try:
    response = requests.post(
        "http://localhost:8080/api/tradeberg/enforced/chat/completions",
        json=payload,
        timeout=60
    )
    
    print(f"📊 Response Status: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        
        print("✅ SUCCESS!")
        print(f"Response length: {len(content)} characters")
        print()
        print("="*80)
        print("RESPONSE PREVIEW:")
        print("="*80)
        print(content[:800])
        if len(content) > 800:
            print(f"\n... (showing first 800 of {len(content)} chars)")
        print("="*80)
        print()
        
        # Check indicators
        has_citations = any(f"[{i}]" in content for i in range(1,6))
        has_tables = "|" in content
        
        print("🔍 ANALYSIS:")
        print(f"  Citations: {'✅' if has_citations else '❌'}")
        print(f"  Tables: {'✅' if has_tables else '❌'}")
        print()
        
        if has_citations:
            print("🎯 VERDICT: ✅ Using Perplexity API correctly!")
        else:
            print("🎯 VERDICT: ⚠️  Not using Perplexity")
            
    elif response.status_code == 400:
        print("❌ ERROR 400 - Bad Request")
        print()
        error_data = response.json()
        print("Error Response:")
        print(json.dumps(error_data, indent=2))
        print()
        
        error_msg = str(error_data)
        
        if "insufficient_quota" in error_msg or "429" in error_msg:
            print("🔍 DIAGNOSIS: OpenAI API quota exceeded")
            print()
            print("❌ PROBLEM FOUND:")
            print("   The system is calling OpenAI API instead of Perplexity!")
            print()
            print("💡 POSSIBLE CAUSES:")
            print("   1. Image data is being passed when it shouldn't be")
            print("   2. Routing logic is incorrect")
            print("   3. OpenAI is being called as fallback")
            print()
            print("🔧 SOLUTION:")
            print("   Need to check why OpenAI is being called for text queries")
        else:
            print("🔍 DIAGNOSIS: Different error")
            print(f"   Error: {error_msg}")
            
    else:
        print(f"❌ ERROR {response.status_code}")
        print(response.text[:500])
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to backend")
    print("   Make sure backend is running on port 8080")
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "="*80)

# Now check backend logs
print("\n📋 NEXT STEPS:")
print("   1. Check backend terminal logs for routing decision")
print("   2. Look for: 'Image: True' or 'Image: False'")
print("   3. Should see: 'Processing text query with Perplexity'")
print("   4. If you see 'OpenAI Vision', that's the problem!")
print()
print("="*80 + "\n")
