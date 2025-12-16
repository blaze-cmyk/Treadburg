import requests

print("Testing chat creation API...")

# Test creating a chat
response = requests.post(
    'http://127.0.0.1:8080/api/chat/create',
    json={'prompt': ''},
    headers={'Content-Type': 'application/json'}
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    data = response.json()
    print(f"\n✅ Chat created successfully!")
    print(f"Chat ID: {data.get('chatId')}")
else:
    print(f"\n❌ Failed to create chat")
