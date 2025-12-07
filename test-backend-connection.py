"""
Test backend connection and Perplexity integration
"""
import requests
import sys

def test_backend_health():
    """Test if backend is running"""
    print("\n" + "="*60)
    print("TEST 1: Backend Health Check")
    print("="*60)
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running on port 8080")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is NOT running on port 8080")
        print("   Please start backend with: python -m uvicorn app:app --reload --port 8080")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_chat_list():
    """Test chat list endpoint"""
    print("\n" + "="*60)
    print("TEST 2: Chat List Endpoint")
    print("="*60)
    try:
        response = requests.get("http://localhost:8080/api/chat", timeout=5)
        if response.status_code == 200:
            chats = response.json()
            print(f"✅ Chat list endpoint working")
            print(f"   Found {len(chats)} chats")
            return True
        else:
            print(f"❌ Chat list returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_create_chat():
    """Test creating a new chat"""
    print("\n" + "="*60)
    print("TEST 3: Create Chat")
    print("="*60)
    try:
        response = requests.post(
            "http://localhost:8080/api/chat/create",
            json={"prompt": "Test message"},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            chat_id = data.get("chatId")
            print(f"✅ Chat created successfully")
            print(f"   Chat ID: {chat_id}")
            return chat_id
        else:
            print(f"❌ Create chat returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_stream_message(chat_id):
    """Test streaming a message"""
    print("\n" + "="*60)
    print("TEST 4: Stream Message")
    print("="*60)
    if not chat_id:
        print("⚠️  Skipping - no chat ID")
        return False
    
    try:
        response = requests.post(
            f"http://localhost:8080/api/chat/{chat_id}/stream",
            json={"userPrompt": "What is Bitcoin?"},
            timeout=30,
            stream=True
        )
        if response.status_code == 200:
            print(f"✅ Streaming endpoint working")
            print("   Response preview:")
            chunk_count = 0
            for chunk in response.iter_content(chunk_size=100, decode_unicode=True):
                if chunk:
                    chunk_count += 1
                    if chunk_count <= 5:  # Show first 5 chunks
                        print(f"   {chunk[:50]}...")
            print(f"   Total chunks received: {chunk_count}")
            return True
        else:
            print(f"❌ Stream returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n" + "🔍 TRADEBERG BACKEND CONNECTION TEST" + "\n")
    
    results = []
    
    # Test 1: Backend health
    results.append(("Backend Health", test_backend_health()))
    
    if not results[0][1]:
        print("\n" + "="*60)
        print("⚠️  BACKEND IS NOT RUNNING - STOPPING TESTS")
        print("="*60)
        print("\nTo start backend:")
        print("  cd c:\\Users\\hariom\\Downloads\\tradebergs\\backend")
        print("  python -m uvicorn app:app --reload --host 0.0.0.0 --port 8080")
        sys.exit(1)
    
    # Test 2: Chat list
    results.append(("Chat List", test_chat_list()))
    
    # Test 3: Create chat
    chat_id = test_create_chat()
    results.append(("Create Chat", chat_id is not None))
    
    # Test 4: Stream message
    results.append(("Stream Message", test_stream_message(chat_id)))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - Backend is working correctly!")
    else:
        print("⚠️  SOME TESTS FAILED - Check errors above")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
