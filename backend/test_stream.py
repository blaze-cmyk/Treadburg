import asyncio
import httpx

async def test_stream():
    # First create a chat
    create_response = httpx.post(
        'http://127.0.0.1:8080/api/chat/create',
        json={'prompt': 'test'}
    )
    print(f"Create chat status: {create_response.status_code}")
    chat_data = create_response.json()
    print(f"Chat data: {chat_data}")
    
    if 'chatId' not in chat_data:
        print("No chatId in response!")
        return
    
    chat_id = chat_data['chatId']
    
    # Now try to stream a message
    print(f"\nTesting stream for chat {chat_id}...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            async with client.stream(
                'POST',
                f'http://127.0.0.1:8080/api/chat/{chat_id}/stream',
                json={'userPrompt': 'Hello, test message'}
            ) as response:
                print(f"Stream status: {response.status_code}")
                
                if response.status_code != 200:
                    error_text = await response.aread()
                    print(f"Error: {error_text.decode()}")
                    return
                
                print("Streaming response:")
                async for chunk in response.aiter_text():
                    print(chunk, end='', flush=True)
                print("\n\nStream complete!")
                
        except Exception as e:
            print(f"Stream error: {e}")

if __name__ == "__main__":
    asyncio.run(test_stream())
