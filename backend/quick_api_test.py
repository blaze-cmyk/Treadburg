"""Quick API Test - Test Perplexity Integration Now"""
import requests
import json
import time

print("\n" + "="*80)
print("🧪 QUICK API TEST - Testing Perplexity Integration")
print("="*80 + "\n")

# Test query
query = "what is bitcoin price now?"
print(f"📝 Query: {query}\n")

# Prepare request
payload = {
    "model": "tradeberg",
    "messages": [{"role": "user", "content": query}],
    "stream": False
}

print("📤 Sending request to backend...")
start = time.time()

try:
    response = requests.post(
        "http://localhost:8080/api/tradeberg/enforced/chat/completions",
        json=payload,
        timeout=60
    )
    
    elapsed = time.time() - start
    
    print(f"⏱️  Response time: {elapsed:.2f}s")
    print(f"📊 Status: {response.status_code}\n")
    
    if response.status_code == 200:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        
        print("="*80)
        print("RESPONSE:")
        print("="*80)
        print(content[:1000])
        if len(content) > 1000:
            print(f"\n... (showing first 1000 of {len(content)} chars)")
        print("="*80 + "\n")
        
        # Check for Perplexity indicators
        print("🔍 ANALYSIS:")
        checks = {
            "Has citations [1], [2]": any(f"[{i}]" in content for i in range(1,6)),
            "Has tables (|)": "|" in content,
            "Has headers (##)": "##" in content or "**" in content,
            "Has emojis": any(e in content for e in ["📊","📈","📉","💰"]),
            "Has price ($)": "$" in content,
            "Long response (>200)": len(content) > 200
        }
        
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check}")
        
        # Verdict
        if checks["Has citations [1], [2]"]:
            print("\n🎯 VERDICT: ✅ PERPLEXITY API IS WORKING!")
        else:
            print("\n🎯 VERDICT: ⚠️  Not using Perplexity (no citations)")
            
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text[:500])
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to backend")
    print("ℹ️  Make sure backend is running on port 8080")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80 + "\n")
