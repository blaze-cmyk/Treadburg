import asyncio
from services.supabase_client import get_supabase_client

async def test():
    print("Testing Supabase client...")
    
    try:
        client = get_supabase_client()
        print("✅ Client created")
        
        print("\nGetting all chats...")
        chats = await client.get_all_chats()
        print(f"✅ Got {len(chats)} chats")
        
        print("\nCreating new chat...")
        chat = await client.create_chat(title="Test Chat")
        print(f"✅ Created chat: {chat['id']}")
        
        print("\nDeleting test chat...")
        await client.delete_chat(chat['id'])
        print("✅ Deleted")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
