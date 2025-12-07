import asyncio
import httpx

async def test():
    # Use existing chat
    chat_id = "0c9c96a9-99d6-4cb2-8917-65f2ad9ece45"
    print(f"Testing with chat ID: {chat_id}")
    
    # Stream message
    print("\nStreaming 'Is TSLA undervalued?'...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        async with client.stream(
            'POST',
            f'http://127.0.0.1:8080/api/chat/{chat_id}/stream',
            json={'userPrompt': 'Is TSLA undervalued?'}
        ) as response:
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                async for chunk in response.aiter_text():
                    print(chunk, end='', flush=True)
                print("\n\n✅ Stream completed successfully!")
            else:
                error = await response.aread()
                print(f"❌ Error: {error.decode()}")

asyncio.run(test())
