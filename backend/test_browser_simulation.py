"""
Simulate exact browser flow through frontend API routes
"""
import asyncio
import httpx

async def test():
    print("=" * 70)
    print("SIMULATING BROWSER FLOW")
    print("=" * 70)
    
    # 1. Browser calls frontend API to create chat
    print("\n1. POST http://localhost:3000/api/chat/create")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.post('http://localhost:3000/api/chat/create', json={'prompt': ''})
            print(f"   Status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                chat_id = data.get('chatId')
                print(f"   ✅ Chat created: {chat_id}")
                
                # 2. Browser calls frontend API to stream message
                print(f"\n2. POST http://localhost:3000/api/chat/{chat_id}/message")
                print("   Sending: 'Is TSLA undervalued?'")
                
                async with client.stream(
                    'POST',
                    f'http://localhost:3000/api/chat/{chat_id}/message',
                    json={'userPrompt': 'Is TSLA undervalued?', 'attachments': None, 'mode': 'chat'},
                    timeout=30.0
                ) as response:
                    print(f"   Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        print("   ✅ Streaming response:")
                        print("   " + "-" * 60)
                        content = ""
                        async for chunk in response.aiter_text():
                            print(chunk, end='', flush=True)
                            content += chunk
                            if len(content) > 500:  # Limit output
                                print("\n   ... (truncated)")
                                break
                        print("\n   " + "-" * 60)
                        print("   ✅ SUCCESS!")
                    else:
                        error = await response.aread()
                        print(f"   ❌ ERROR: {error.decode()}")
            else:
                print(f"   ❌ Failed: {r.text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            import traceback
            traceback.print_exc()

asyncio.run(test())
