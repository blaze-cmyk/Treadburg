"""
Test the exact flow the frontend uses
"""
import asyncio
import httpx

async def test():
    print("=" * 60)
    print("TESTING FRONTEND FLOW")
    print("=" * 60)
    
    # 1. Create chat (like home page does)
    print("\n1. Creating chat via /api/chat/create...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post('http://127.0.0.1:8080/api/chat/create', json={'prompt': ''})
        print(f"Status: {r.status_code}")
        data = r.json()
        print(f"Response: {data}")
        chat_id = data['chatId']
    
    # 2. Verify chat exists
    print(f"\n2. Verifying chat {chat_id} exists...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f'http://127.0.0.1:8080/api/chat/{chat_id}')
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(f"✅ Chat exists: {r.json()}")
        else:
            print(f"❌ Chat not found: {r.text}")
            return
    
    # 3. Stream message (like chat page does)
    print(f"\n3. Streaming message...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        async with client.stream(
            'POST',
            f'http://127.0.0.1:8080/api/chat/{chat_id}/stream',
            json={'userPrompt': 'Is TSLA undervalued?', 'attachments': None, 'mode': 'chat'}
        ) as response:
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("Response:")
                async for chunk in response.aiter_text():
                    print(chunk, end='', flush=True)
                print("\n\n✅ Success!")
            else:
                error = await response.aread()
                print(f"❌ Error: {error.decode()}")

asyncio.run(test())
