"""
Test all chat endpoints to find the issue
"""
import requests
import json

print("=" * 70)
print("TESTING ALL CHAT ENDPOINTS")
print("=" * 70)

base_url = "http://127.0.0.1:8080/api"

# 1. Test GET /chat (get all chats)
print("\n1. GET /chat - Get all chats")
try:
    r = requests.get(f"{base_url}/chat", timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        chats = r.json()
        print(f"   ✅ Found {len(chats)} chats")
        if chats:
            print(f"   Latest: {chats[0]['id']} - {chats[0]['title']}")
    else:
        print(f"   ❌ Error: {r.text}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

# 2. Test POST /chat/create
print("\n2. POST /chat/create - Create new chat")
try:
    r = requests.post(f"{base_url}/chat/create", json={"prompt": ""}, timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        chat_id = data.get('chatId')
        print(f"   ✅ Created chat: {chat_id}")
        
        # 3. Test GET /chat/{id}
        print(f"\n3. GET /chat/{chat_id} - Get specific chat")
        r2 = requests.get(f"{base_url}/chat/{chat_id}", timeout=5)
        print(f"   Status: {r2.status_code}")
        if r2.status_code == 200:
            print(f"   ✅ Chat found: {r2.json()}")
        else:
            print(f"   ❌ Error: {r2.text}")
        
        # 4. Test POST /chat/{id}/stream
        print(f"\n4. POST /chat/{chat_id}/stream - Stream message")
        try:
            r3 = requests.post(
                f"{base_url}/chat/{chat_id}/stream",
                json={"userPrompt": "Hello", "attachments": None, "mode": "chat"},
                timeout=10,
                stream=True
            )
            print(f"   Status: {r3.status_code}")
            if r3.status_code == 200:
                print(f"   ✅ Stream started, first 200 chars:")
                content = ""
                for chunk in r3.iter_content(chunk_size=1024, decode_unicode=True):
                    if chunk:
                        content += chunk
                        if len(content) > 200:
                            break
                print(f"   {content[:200]}")
            else:
                print(f"   ❌ Error: {r3.text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        # 5. Test GET /chat/{id}/messages
        print(f"\n5. GET /chat/{chat_id}/messages - Get messages")
        r4 = requests.get(f"{base_url}/chat/{chat_id}/messages", timeout=5)
        print(f"   Status: {r4.status_code}")
        if r4.status_code == 200:
            messages = r4.json()
            print(f"   ✅ Found {len(messages)} messages")
        else:
            print(f"   ❌ Error: {r4.text}")
        
        # 6. Test PUT /chat/{id}/title
        print(f"\n6. PUT /chat/{chat_id}/title - Rename chat")
        r5 = requests.put(f"{base_url}/chat/{chat_id}/title", json={"title": "Test Chat"}, timeout=5)
        print(f"   Status: {r5.status_code}")
        if r5.status_code == 200:
            print(f"   ✅ Renamed: {r5.json()}")
        else:
            print(f"   ❌ Error: {r5.text}")
        
        # 7. Test DELETE /chat/{id}
        print(f"\n7. DELETE /chat/{chat_id} - Delete chat")
        r6 = requests.delete(f"{base_url}/chat/{chat_id}", timeout=5)
        print(f"   Status: {r6.status_code}")
        if r6.status_code == 200:
            print(f"   ✅ Deleted successfully")
        else:
            print(f"   ❌ Error: {r6.text}")
    else:
        print(f"   ❌ Error: {r.text}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

print("\n" + "=" * 70)
print("ENDPOINT TESTING COMPLETE")
print("=" * 70)
