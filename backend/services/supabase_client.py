"""
Supabase REST API Client
Alternative to direct PostgreSQL connection when port 5432 is blocked
"""
import os
from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime
import uuid
from config import settings

class SupabaseClient:
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_SERVICE_ROLE_KEY
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        
        self.base_url = f"{self.url}/rest/v1"
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make HTTP request to Supabase REST API"""
        url = f"{self.base_url}/{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, headers=self.headers, **kwargs)
            if response.status_code >= 400:
                print(f"Error {response.status_code}: {response.text}")
            response.raise_for_status()
            return response.json()
    
    # Chat operations
    async def create_chat(self, title: str = "New Chat") -> Dict[str, Any]:
        """Create a new chat"""
        chat_data = {
            "title": title
        }
        result = await self._request("POST", "chats", json=chat_data)
        return result[0] if isinstance(result, list) else result
    
    async def get_all_chats(self) -> List[Dict[str, Any]]:
        """Get all chats"""
        return await self._request("GET", "chats?order=updated_at.desc")
    
    async def get_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get chat by ID"""
        result = await self._request("GET", f"chats?id=eq.{chat_id}")
        return result[0] if result else None
    
    async def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat"""
        await self._request("DELETE", f"chats?id=eq.{chat_id}")
        return True
    
    async def update_chat(self, chat_id: str, title: str) -> Dict[str, Any]:
        """Update chat title"""
        update_data = {
            "title": title,
            "updated_at": datetime.utcnow().isoformat()
        }
        result = await self._request("PATCH", f"chats?id=eq.{chat_id}", json=update_data)
        return result[0] if isinstance(result, list) else result
    
    # Message operations
    async def create_message(self, chat_id: str, role: str, content: str) -> Dict[str, Any]:
        """Create a new message"""
        message_data = {
            "chat_id": chat_id,
            "role": role,
            "content": content,
            "created_at": datetime.utcnow().isoformat()
        }
        result = await self._request("POST", "messages", json=message_data)
        return result[0] if isinstance(result, list) else result
    
    async def get_messages(self, chat_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a chat"""
        return await self._request("GET", f"messages?chat_id=eq.{chat_id}&order=created_at.asc")
    
    # User operations
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        result = await self._request("GET", f"users?email=eq.{email}")
        return result[0] if result else None
    
    async def create_user(self, email: str, **kwargs) -> Dict[str, Any]:
        """Create a new user"""
        user_data = {
            "id": str(uuid.uuid4()),
            "email": email,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            **kwargs
        }
        result = await self._request("POST", "users", json=user_data)
        return result[0] if isinstance(result, list) else result
    
    # Subscription operations
    async def get_subscription(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's active subscription"""
        result = await self._request("GET", f"subscriptions?user_id=eq.{user_id}&status=eq.active")
        return result[0] if result else None
    
    async def create_subscription(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """Create a new subscription"""
        subscription_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            **kwargs
        }
        result = await self._request("POST", "subscriptions", json=subscription_data)
        return result[0] if isinstance(result, list) else result
    
    async def update_subscription(self, subscription_id: str, **kwargs) -> Dict[str, Any]:
        """Update subscription"""
        update_data = {
            "updated_at": datetime.utcnow().isoformat(),
            **kwargs
        }
        result = await self._request("PATCH", f"subscriptions?id=eq.{subscription_id}", json=update_data)
        return result[0] if isinstance(result, list) else result

# Global instance
_supabase_client = None

def get_supabase_client() -> SupabaseClient:
    """Get or create Supabase client instance"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client
