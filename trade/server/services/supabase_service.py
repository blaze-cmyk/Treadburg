"""
Supabase Client Integration
"""
from supabase import create_client, Client
from config import settings

_supabase_client = None

def get_supabase_client() -> Client:
    """Get or create Supabase client instance"""
    global _supabase_client
    
    if _supabase_client is None:
        url = settings.SUPABASE_URL
        key = settings.SUPABASE_SERVICE_ROLE_KEY
        
        if not url or not key:
            raise ValueError("Supabase URL and Service Role Key must be set in environment")
        
        _supabase_client = create_client(url, key)
    
    return _supabase_client
