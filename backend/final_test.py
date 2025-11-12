"""Final Test - Check if Perplexity is working"""
import requests
import json
import time

print("\n" + "="*80)
print("🎯 FINAL TEST - Checking Perplexity Integration")
print("="*80 + "\n")

payload = {
    "model": "tradeberg",
    "messages": [{"role": "user", "content": "what is bitcoin price?"}],
    "stream": False
}

print("📤 Sending request...")
print(f"⏰ Timestamp: {time.strftime('%H:%M:%S')}\n")

try:
    response = requests.post(
        "http://localhost:8080/api/tradeberg/enforced/chat/completions",
        json=payload,
        timeout=90  # Longer timeout
    )
    
    print(f"📊 Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        
        print(f"✅ SUCCESS! Response length: {len(content)} chars\n")
        print("="*80)
        print("RESPONSE:")
        print("="*80)
        print(content[:1200])
        if len(content) > 1200:
            print(f"\n... ({len(content)} total chars)")
        print("="*80 + "\n")
        
        # Check for Perplexity
        has_citations = any(f"[{i}]" in content for i in range(1,6))
        has_tables = "|" in content
        has_price = "$" in content
        
        print("🔍 VERIFICATION:")
        print(f"  ✅ Citations: {has_citations}")
        print(f"  ✅ Tables: {has_tables}")
        print(f"  ✅ Price data: {has_price}")
        
        if has_citations and has_tables:
            print("\n🎉 PERPLEXITY IS WORKING PERFECTLY!")
        else:
            print("\n⚠️  Response missing Perplexity features")
            
    else:
        print(f"❌ Error {response.status_code}")
        print(response.text[:800])
        
except requests.exceptions.Timeout:
    print("⏰ Request timed out after 90 seconds")
    print("   Backend might be processing or having issues")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80 + "\n")
