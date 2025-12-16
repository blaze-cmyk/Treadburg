"""
Credit Management Service
Handles credit deduction and balance checks for authenticated users
"""
from typing import Optional
import logging
from services.supabase_service import get_supabase_client

log = logging.getLogger(__name__)

CREDITS_PER_MESSAGE = 1  # Cost per AI message


async def check_user_credits(user_token: str) -> int:
    """
    Check user's current credit balance
    
    Args:
        user_token: User's JWT token
    
    Returns:
        Current credit balance
    
    Raises:
        Exception: If unable to fetch credits
    """
    try:
        supabase = get_supabase_client()
        
        # Get user from token
        user_response = supabase.auth.get_user(user_token)
        
        if not user_response.user:
            raise Exception("Invalid user token")
        
        # Get user profile with credits
        profile = supabase.table('profiles').select('credits_balance').eq(
            'auth_user_id', user_response.user.id
        ).execute()
        
        if not profile.data:
            log.warning(f"No profile found for user {user_response.user.id}")
            return 0
        
        return profile.data[0].get('credits_balance', 0)
        
    except Exception as e:
        log.error(f"Error checking credits: {e}")
        raise


async def deduct_credits(user_token: str, amount: int = CREDITS_PER_MESSAGE) -> dict:
    """
    Deduct credits from user's balance
    
    Args:
        user_token: User's JWT token
        amount: Number of credits to deduct (default: 1 per message)
    
    Returns:
        dict with success status and new balance
    
    Raises:
        Exception: If insufficient credits or unable to deduct
    """
    try:
        supabase = get_supabase_client()
        
        # Get user from token
        user_response = supabase.auth.get_user(user_token)
        
        if not user_response.user:
            raise Exception("Invalid user token")
        
        user_id = user_response.user.id
        
        # Get current balance
        profile = supabase.table('profiles').select('credits_balance').eq(
            'auth_user_id', user_id
        ).execute()
        
        if not profile.data:
            raise Exception("User profile not found")
        
        current_balance = profile.data[0].get('credits_balance', 0)
        
        # Check if sufficient credits
        if current_balance < amount:
            return {
                "success": False,
                "error": "insufficient_credits",
                "current_balance": current_balance,
                "required": amount
            }
        
        # Deduct credits
        new_balance = current_balance - amount
        
        update_result = supabase.table('profiles').update({
            'credits_balance': new_balance
        }).eq('auth_user_id', user_id).execute()
        
        log.info(f"Deducted {amount} credits from user {user_id}. New balance: {new_balance}")
        
        return {
            "success": True,
            "previous_balance": current_balance,
            "new_balance": new_balance,
            "deducted": amount
        }
        
    except Exception as e:
        log.error(f"Error deducting credits: {e}")
        raise


async def add_credits(user_token: str, amount: int) -> dict:
    """
    Add credits to user's balance (for purchases, bonuses, etc.)
    
    Args:
        user_token: User's JWT token
        amount: Number of credits to add
    
    Returns:
        dict with success status and new balance
    """
    try:
        supabase = get_supabase_client()
        
        # Get user from token
        user_response = supabase.auth.get_user(user_token)
        
        if not user_response.user:
            raise Exception("Invalid user token")
        
        user_id = user_response.user.id
        
        # Get current balance
        profile = supabase.table('profiles').select('credits_balance').eq(
            'auth_user_id', user_id
        ).execute()
        
        if not profile.data:
            raise Exception("User profile not found")
        
        current_balance = profile.data[0].get('credits_balance', 0)
        new_balance = current_balance + amount
        
        # Add credits
        update_result = supabase.table('profiles').update({
            'credits_balance': new_balance
        }).eq('auth_user_id', user_id).execute()
        
        log.info(f"Added {amount} credits to user {user_id}. New balance: {new_balance}")
        
        return {
            "success": True,
            "previous_balance": current_balance,
            "new_balance": new_balance,
            "added": amount
        }
        
    except Exception as e:
        log.error(f"Error adding credits: {e}")
        raise
