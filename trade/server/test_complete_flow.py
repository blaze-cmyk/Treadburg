"""
Complete flow test for Supabase REST API integration
"""
import asyncio
import httpx

async def test_complete_flow():
    print("=" * 60)
    print("TESTING COMPLETE CHAT FLOW WITH SUPABASE REST API")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8080/api"
    
    # 1. Create a chat
    print("\n1️⃣  Creating chat...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(f"{base_url}/chat/create", json={"prompt": ""})
        if response.status_code == 200:
            data = response.json()
            chat_id = data.get("chatId")
            print(f"✅ Chat created: {chat_id}")
        else:
            print(f"❌ Failed to create chat: {response.status_code}")
            return
    
    # 2. Get all chats
    print("\n2️⃣  Getting all chats...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{base_url}/chat")
        if response.status_code == 200:
            chats = response.json()
            print(f"✅ Found {len(chats)} chats")
        else:
            print(f"❌ Failed to get chats: {response.status_code}")
    
    # 3. Get specific chat
    print(f"\n3️⃣  Getting chat {chat_id}...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{base_url}/chat/{chat_id}")
        if response.status_code == 200:
            chat = response.json()
            print(f"✅ Chat title: {chat.get('title')}")
        else:
            print(f"❌ Failed to get chat: {response.status_code}")
    
    # 4. Stream a message
    print(f"\n4️⃣  Streaming message to chat...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            async with client.stream(
                'POST',
                f"{base_url}/chat/{chat_id}/stream",
                json={'userPrompt': 'What is 2+2?'}
            ) as response:
                if response.status_code == 200:
                    print("✅ Streaming response:")
                    print("-" * 60)
                    async for chunk in response.aiter_text():
                        print(chunk, end='', flush=True)
                    print("\n" + "-" * 60)
                else:
                    error = await response.aread()
                    print(f"❌ Stream failed: {response.status_code}")
                    print(f"Error: {error.decode()}")
        except Exception as e:
            print(f"❌ Stream error: {e}")
    
    # 5. Get messages
    print(f"\n5️⃣  Getting messages...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{base_url}/chat/{chat_id}/messages")
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ Found {len(messages)} messages")
            for msg in messages:
                print(f"  - {msg.get('role')}: {msg.get('content')[:50]}...")
        else:
            print(f"❌ Failed to get messages: {response.status_code}")
    
    # 6. Rename chat
    print(f"\n6️⃣  Renaming chat...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.put(
            f"{base_url}/chat/{chat_id}/title",
            json={"title": "Test Chat"}
        )
        if response.status_code == 200:
            chat = response.json()
            print(f"✅ Chat renamed to: {chat.get('title')}")
        else:
            print(f"❌ Failed to rename chat: {response.status_code}")
    
    # 7. Delete chat
    print(f"\n7️⃣  Deleting chat...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.delete(f"{base_url}/chat/{chat_id}")
        if response.status_code == 200:
            print(f"✅ Chat deleted successfully")
        else:
            print(f"❌ Failed to delete chat: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_complete_flow())
