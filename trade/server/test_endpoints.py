"""
Test all API endpoints to verify frontend-backend connectivity
"""
import asyncio
import httpx

BASE_URL = "http://127.0.0.1:8080/api"

async def test_endpoints():
    """Test all chat endpoints"""
    print("🧪 Testing API Endpoints...\n")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: Get token limit
        print("1️⃣ Testing GET /api/chat/limit")
        try:
            response = await client.get(f"{BASE_URL}/chat/limit")
            if response.status_code == 200:
                print(f"   ✅ Success: {response.json()}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 2: Get all chats
        print("\n2️⃣ Testing GET /api/chat")
        try:
            response = await client.get(f"{BASE_URL}/chat")
            if response.status_code == 200:
                chats = response.json()
                print(f"   ✅ Success: Found {len(chats)} chats")
            else:
                print(f"   ❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 3: Create a new chat
        print("\n3️⃣ Testing POST /api/chat/create")
        try:
            response = await client.post(
                f"{BASE_URL}/chat/create",
                json={"prompt": "Test message from endpoint test"}
            )
            if response.status_code == 200:
                data = response.json()
                chat_id = data.get("chatId")
                print(f"   ✅ Success: Created chat with ID: {chat_id}")
                
                # Test 4: Get chat by ID
                print(f"\n4️⃣ Testing GET /api/chat/{chat_id}")
                try:
                    response = await client.get(f"{BASE_URL}/chat/{chat_id}")
                    if response.status_code == 200:
                        print(f"   ✅ Success: {response.json()}")
                    else:
                        print(f"   ❌ Failed: {response.status_code}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                
                # Test 5: Get messages for chat
                print(f"\n5️⃣ Testing GET /api/chat/{chat_id}/message")
                try:
                    response = await client.get(f"{BASE_URL}/chat/{chat_id}/message")
                    if response.status_code == 200:
                        messages = response.json()
                        print(f"   ✅ Success: Found {len(messages)} messages")
                    else:
                        print(f"   ❌ Failed: {response.status_code}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n" + "="*50)
        print("✅ Endpoint testing complete!")
        print("="*50)

if __name__ == "__main__":
    asyncio.run(test_endpoints())
