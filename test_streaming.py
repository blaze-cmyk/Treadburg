#!/usr/bin/env python3
"""
Test script for streaming chat completions
"""
import requests
import json
import time

def test_streaming():
    """Test streaming endpoint"""
    print("🧪 Testing Streaming Chat Completion...\n")
    
    url = "http://localhost:8080/api/chat/completions"
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "what is the price of btc?"
            }
        ],
        "stream": True,
        "model": "gpt-4o"
    }
    
    print("📤 Sending request with stream=True...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")
    
    start_time = time.time()
    first_chunk_time = None
    chunk_count = 0
    
    try:
        response = requests.post(
            url,
            json=payload,
            stream=True,
            timeout=60
        )
        
        print(f"✅ Response Status: {response.status_code}\n")
        print("📊 Streaming Response:\n")
        print("-" * 80)
        
        for line in response.iter_lines():
            if line:
                line_text = line.decode('utf-8')
                
                if line_text.startswith('data: '):
                    data_str = line_text[6:]
                    
                    if data_str.strip() == '[DONE]':
                        print("\n" + "-" * 80)
                        print("✅ Stream completed!")
                        break
                    
                    try:
                        data = json.loads(data_str)
                        
                        if first_chunk_time is None:
                            first_chunk_time = time.time()
                            time_to_first = first_chunk_time - start_time
                            print(f"\n⚡ Time to first chunk: {time_to_first:.2f}s\n")
                        
                        chunk_count += 1
                        
                        if 'choices' in data and len(data['choices']) > 0:
                            delta = data['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            
                            if content:
                                # Print content without newline for streaming effect
                                print(content, end='', flush=True)
                    
                    except json.JSONDecodeError as e:
                        print(f"\n⚠️  JSON decode error: {e}")
                        print(f"Data: {data_str[:100]}...")
        
        total_time = time.time() - start_time
        
        print("\n\n" + "=" * 80)
        print("📊 Streaming Statistics:")
        print("=" * 80)
        print(f"⏱️  Total time: {total_time:.2f}s")
        print(f"⚡ Time to first chunk: {first_chunk_time - start_time if first_chunk_time else 'N/A':.2f}s")
        print(f"📦 Total chunks: {chunk_count}")
        print(f"📈 Average chunk rate: {chunk_count / total_time:.1f} chunks/sec")
        print("=" * 80)
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")


def test_non_streaming():
    """Test non-streaming endpoint for comparison"""
    print("\n\n🧪 Testing Non-Streaming Chat Completion...\n")
    
    url = "http://localhost:8080/api/chat/completions"
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "what is the price of btc?"
            }
        ],
        "stream": False,
        "model": "gpt-4o"
    }
    
    print("📤 Sending request with stream=False...")
    
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        total_time = time.time() - start_time
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"⏱️  Total time: {total_time:.2f}s\n")
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            print("📊 Response Preview:")
            print("-" * 80)
            print(content[:500] + "..." if len(content) > 500 else content)
            print("-" * 80)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🚀 TradeBerg Streaming Test Suite 🚀              ║
║                                                              ║
║  This script tests the real-time streaming implementation   ║
║  Make sure your backend is running on port 8080             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Test streaming
    test_streaming()
    
    # Test non-streaming for comparison
    test_non_streaming()
    
    print("\n\n✅ All tests completed!")
    print("\n💡 TIP: Compare the 'Time to first chunk' between streaming and non-streaming")
    print("   Streaming should show data within 0.1-0.5s, while non-streaming waits for everything!")
