import requests

# Get most recent chat
r = requests.get('http://127.0.0.1:8080/api/chat')
chats = r.json()
if chats:
    chat_id = chats[0]['id']
    print(f"Testing with chat: {chat_id}")
    
    # Test streaming
    print("\nTesting stream...")
    try:
        r2 = requests.post(
            f'http://127.0.0.1:8080/api/chat/{chat_id}/stream',
            json={'userPrompt': 'Bitcoin price forecast'},
            stream=True,
            timeout=30
        )
        print(f"Status: {r2.status_code}")
        if r2.status_code == 200:
            print("Response:")
            for chunk in r2.iter_content(chunk_size=1024, decode_unicode=True):
                if chunk:
                    print(chunk[:200])
                    break
        else:
            print(f"Error: {r2.text}")
    except Exception as e:
        print(f"Exception: {e}")
else:
    print("No chats found")
