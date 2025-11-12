"""
Supabase Integration for TradeBerg

This module provides integration with Supabase for:
- Database operations (CRUD)
- Real-time subscriptions
- Authentication
- Storage
- Edge Functions
"""

import os
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = None

log = logging.getLogger(__name__)


class SupabaseClient:
    """
    Supabase client wrapper for TradeBerg application
    
    Features:
    - User data management
    - Trading data storage
    - Market analysis history
    - Subscription management
    - Real-time updates
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        key: Optional[str] = None,
        service_role_key: Optional[str] = None
    ):
        """
        Initialize Supabase client
        
        Args:
            url: Supabase project URL
            key: Supabase anon/public key
            service_role_key: Supabase service role key (for admin operations)
        """
        if create_client is None:
            raise ImportError(
                "supabase-py is not installed. "
                "Install it with: pip install supabase"
            )
        
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_ANON_KEY")
        self.service_role_key = service_role_key or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.url or not self.key:
            raise ValueError(
                "Supabase URL and Key are required. "
                "Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables."
            )
        
        # Client for user operations
        self.client: Client = create_client(self.url, self.key)
        
        # Admin client for privileged operations
        self.admin_client: Optional[Client] = None
        if self.service_role_key:
            self.admin_client = create_client(self.url, self.service_role_key)
        
        log.info("Supabase client initialized successfully")
    
    # ==========================================
    # USER MANAGEMENT
    # ==========================================
    
    async def create_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict:
        """Create or update user profile in Supabase"""
        try:
            data = {
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                **profile_data
            }
            
            result = self.client.table("user_profiles").upsert(data).execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            log.error(f"Error creating user profile: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile from Supabase"""
        try:
            result = self.client.table("user_profiles").select("*").eq("user_id", user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            log.error(f"Error getting user profile: {e}")
            return None
    
    # ==========================================
    # TRADING DATA MANAGEMENT
    # ==========================================
    
    async def save_market_analysis(
        self,
        user_id: str,
        symbol: str,
        analysis_data: Dict[str, Any]
    ) -> Dict:
        """Save market analysis to Supabase"""
        try:
            data = {
                "user_id": user_id,
                "symbol": symbol,
                "analysis_data": analysis_data,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("market_analyses").insert(data).execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            log.error(f"Error saving market analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_analyses(
        self,
        user_id: str,
        limit: int = 50,
        symbol: Optional[str] = None
    ) -> List[Dict]:
        """Get user's market analyses"""
        try:
            query = self.client.table("market_analyses").select("*").eq("user_id", user_id)
            
            if symbol:
                query = query.eq("symbol", symbol)
            
            result = query.order("created_at", desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            log.error(f"Error getting user analyses: {e}")
            return []
    
    # ==========================================
    # SUBSCRIPTION MANAGEMENT
    # ==========================================
    
    async def save_subscription(
        self,
        user_id: str,
        subscription_data: Dict[str, Any]
    ) -> Dict:
        """Save user subscription data"""
        try:
            data = {
                "user_id": user_id,
                "subscription_data": subscription_data,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("subscriptions").upsert(data).execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            log.error(f"Error saving subscription: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_subscription(self, user_id: str) -> Optional[Dict]:
        """Get user's active subscription"""
        try:
            result = (
                self.client.table("subscriptions")
                .select("*")
                .eq("user_id", user_id)
                .eq("status", "active")
                .execute()
            )
            return result.data[0] if result.data else None
        except Exception as e:
            log.error(f"Error getting user subscription: {e}")
            return None
    
    # ==========================================
    # CHAT HISTORY
    # ==========================================
    
    async def save_chat_message(
        self,
        user_id: str,
        chat_id: str,
        message_data: Dict[str, Any]
    ) -> Dict:
        """Save chat message to Supabase"""
        try:
            data = {
                "user_id": user_id,
                "chat_id": chat_id,
                "message_data": message_data,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("chat_messages").insert(data).execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            log.error(f"Error saving chat message: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_chat_history(
        self,
        user_id: str,
        chat_id: str,
        limit: int = 100
    ) -> List[Dict]:
        """Get chat history from Supabase"""
        try:
            result = (
                self.client.table("chat_messages")
                .select("*")
                .eq("user_id", user_id)
                .eq("chat_id", chat_id)
                .order("created_at", desc=False)
                .limit(limit)
                .execute()
            )
            return result.data
        except Exception as e:
            log.error(f"Error getting chat history: {e}")
            return []
    
    # ==========================================
    # STORAGE OPERATIONS
    # ==========================================
    
    async def upload_file(
        self,
        bucket: str,
        file_path: str,
        file_data: bytes,
        content_type: Optional[str] = None
    ) -> Dict:
        """Upload file to Supabase Storage"""
        try:
            result = self.client.storage.from_(bucket).upload(
                file_path,
                file_data,
                {"content-type": content_type} if content_type else {}
            )
            return {"success": True, "data": result}
        except Exception as e:
            log.error(f"Error uploading file: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_file_url(self, bucket: str, file_path: str) -> Optional[str]:
        """Get public URL for a file"""
        try:
            result = self.client.storage.from_(bucket).get_public_url(file_path)
            return result
        except Exception as e:
            log.error(f"Error getting file URL: {e}")
            return None
    
    # ==========================================
    # REAL-TIME SUBSCRIPTIONS
    # ==========================================
    
    def subscribe_to_table(self, table: str, callback):
        """Subscribe to real-time changes on a table"""
        try:
            return self.client.table(table).on("*", callback).subscribe()
        except Exception as e:
            log.error(f"Error subscribing to table: {e}")
            return None
    
    # ==========================================
    # ADMIN OPERATIONS
    # ==========================================
    
    async def execute_migration(self, sql: str) -> Dict:
        """Execute SQL migration (requires service role key)"""
        if not self.admin_client:
            return {"success": False, "error": "Service role key not configured"}
        
        try:
            # Execute raw SQL using admin client
            result = self.admin_client.rpc("exec_sql", {"query": sql}).execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            log.error(f"Error executing migration: {e}")
            return {"success": False, "error": str(e)}


# Global instance
_supabase_client: Optional[SupabaseClient] = None


def get_supabase_client() -> SupabaseClient:
    """Get or create global Supabase client instance"""
    global _supabase_client
    
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    
    return _supabase_client
