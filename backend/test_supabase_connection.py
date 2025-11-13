"""Test Supabase connection"""
import os
from dotenv import load_dotenv
load_dotenv('.env.mcp')

from open_webui.integrations.supabase_integration import get_supabase_client

try:
    print("Testing Supabase connection...")
    supabase = get_supabase_client()
    
    # Try to query users table
    result = supabase.client.table('users').select('*').limit(1).execute()
    print(f"✅ Supabase connected! Found {len(result.data)} users")
    
except Exception as e:
    print(f"❌ Supabase error: {e}")
    import traceback
    traceback.print_exc()
