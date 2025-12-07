import asyncio
from dotenv import load_dotenv
load_dotenv('env')
from services.supabase_client import get_supabase_client

async def test():
    print("Testing Supabase REST API...")
    client = get_supabase_client()
    
    # Test getting chats
    chats = await client.get_all_chats()
    print(f"✅ Supabase REST API working! Found {len(chats)} chats")
    
    # Test creating a chat
    new_chat = await client.create_chat(title="Test Chat")
    print(f"✅ Created chat: {new_chat['id']}")
    
    return True

if __name__ == "__main__":
    asyncio.run(test())
