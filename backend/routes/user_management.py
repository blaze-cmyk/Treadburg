"""
User Management API Router
Handles user profiles, credits, payments, and authentication
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import logging

from services.supabase_service import get_supabase_client
from services.stripe_service import get_stripe_client

router = APIRouter()
security = HTTPBearer()
log = logging.getLogger(__name__)

# ============================================
# MODELS
# ============================================

class UserProfile(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

class CreditPurchase(BaseModel):
    package_id: Optional[str] = None
    amount: float = 15.00
    credits: int = 100
    success_url: str
    cancel_url: str

class CreditUsage(BaseModel):
    credits: int
    description: str
    endpoint: Optional[str] = None

# ============================================
# AUTHENTICATION HELPERS
# ============================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user from JWT token"""
    try:
        token = credentials.credentials
        supabase = get_supabase_client()
        
        # Verify token with Supabase
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get user profile from database
        user_data = supabase.table('users').select('*').eq('auth_user_id', user_response.user.id).single().execute()
        
        if not user_data.data:
            # Create user profile if doesn't exist
            new_user = {
                'auth_user_id': user_response.user.id,
                'email': user_response.user.email,
                'email_confirmed': user_response.user.email_confirmed_at is not None,
                'credits': 0
            }
            user_data = supabase.table('users').insert(new_user).execute()
        
        return user_data.data
        
    except Exception as e:
        log.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# ============================================
# USER PROFILE ENDPOINTS
# ============================================

@router.get("/profile")
async def get_user_profile(user: dict = Depends(get_current_user)):
    """Get current user's profile"""
    try:
        return {
            "success": True,
            "user": user
        }
    except Exception as e:
        log.error(f"Error getting profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profile")
async def update_user_profile(
    profile_update: UserUpdate,
    user: dict = Depends(get_current_user)
):
    """Update user profile"""
    try:
        supabase = get_supabase_client()
        
        update_data = profile_update.dict(exclude_unset=True)
        result = supabase.table('users').update(update_data).eq('id', user['id']).execute()
        
        return {
            "success": True,
            "user": result.data[0] if result.data else None
        }
    except Exception as e:
        log.error(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# CREDITS ENDPOINTS
# ============================================

@router.get("/credits")
async def get_user_credits(user: dict = Depends(get_current_user)):
    """Get user's current credits"""
    return {
        "success": True,
        "credits": user.get('credits', 0),
        "total_purchased": user.get('total_credits_purchased', 0),
        "total_used": user.get('total_credits_used', 0)
    }

@router.post("/credits/purchase")
async def purchase_credits(
    purchase: CreditPurchase,
    user: dict = Depends(get_current_user)
):
    """Create Stripe checkout session for credit purchase"""
    try:
        log.info(f"Purchase request: user={user.get('email')}, amount=${purchase.amount}, credits={purchase.credits}")
        supabase = get_supabase_client()
        stripe_client = get_stripe_client()
        
        # Get or create user in Supabase
        user_response = supabase.table('users').select('*').eq('auth_user_id', user['auth_user_id']).execute()
        
        if not user_response.data:
            # Auto-create user in Supabase if doesn't exist
            log.info(f"Creating user in Supabase: {user.get('email')}")
            new_user_data = {
                'auth_user_id': user['auth_user_id'],
                'email': user.get('email'),
                'email_confirmed': user.get('email_confirmed', False),
                'credits': 0
            }
            user_response = supabase.table('users').insert(new_user_data).execute()
        
        supabase_user_id = user_response.data[0]['id']
        
        # Get or create Stripe customer
        stripe_customer_id = user_response.data[0].get('stripe_customer_id')
        
        if not stripe_customer_id:
            log.info(f"Creating Stripe customer for {user.get('email')}")
            customer_result = stripe_client.create_customer(
                email=user.get('email'),
                name=user.get('full_name', user.get('email'))
            )
            
            if customer_result['success']:
                stripe_customer_id = customer_result['customer'].id
                supabase.table('users').update({
                    'stripe_customer_id': stripe_customer_id
                }).eq('id', supabase_user_id).execute()
            else:
                raise HTTPException(status_code=500, detail="Failed to create Stripe customer")
        
        # Create payment record
        payment_data = {
            'user_id': supabase_user_id,
            'amount': purchase.amount,
            'currency': 'usd',
            'status': 'pending',
            'credits': purchase.credits,
            'payment_method': 'stripe'
        }
        payment_result = supabase.table('payments').insert(payment_data).execute()
        payment_id = payment_result.data[0]['id']
        
        log.info(f"Created payment record {payment_id} for user {user.get('email')}")
        
        # Create Stripe checkout session
        log.info(f"Creating Stripe checkout for user {user.get('email')}: ${purchase.amount} for {purchase.credits} credits")
        checkout_result = stripe_client.create_checkout_session(
            customer_id=stripe_customer_id,
            amount=int(purchase.amount * 100),  # Convert to cents
            currency='usd',
            success_url=purchase.success_url,
            cancel_url=purchase.cancel_url,
            metadata={
                'user_id': supabase_user_id,
                'payment_id': payment_id,
                'credits': purchase.credits
            }
        )
        
        if not checkout_result['success']:
            error_msg = checkout_result.get('error', 'Unknown error')
            log.error(f"Stripe checkout failed: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Failed to create checkout session: {error_msg}")
        
        session = checkout_result['session']
        return {
            "success": True,
            "checkout_url": session.url,
            "session_id": session.id,
            "payment_id": payment_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error creating checkout: {e}")
        import traceback
        log.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/credits/use")
async def use_credits(
    usage: CreditUsage,
    user: dict = Depends(get_current_user)
):
    """Deduct credits from user account"""
    try:
        supabase = get_supabase_client()
        
        # Check if user has enough credits
        current_credits = user.get('credits', 0)
        if current_credits < usage.credits:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient credits. You have {current_credits}, need {usage.credits}"
            )
        
        # Deduct credits
        new_credits = current_credits - usage.credits
        supabase.table('users').update({
            'credits': new_credits,
            'total_credits_used': user.get('total_credits_used', 0) + usage.credits
        }).eq('id', user['id']).execute()
        
        # Record transaction
        transaction_data = {
            'user_id': user['id'],
            'type': 'usage',
            'amount': -usage.credits,
            'description': usage.description,
            'endpoint': usage.endpoint
        }
        supabase.table('credit_transactions').insert(transaction_data).execute()
        
        return {
            "success": True,
            "credits_remaining": new_credits,
            "credits_used": usage.credits
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error using credits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/credits/transactions")
async def get_credit_transactions(
    limit: int = 50,
    user: dict = Depends(get_current_user)
):
    """Get user's credit transaction history"""
    try:
        supabase = get_supabase_client()
        
        result = supabase.table('credit_transactions').select('*').eq(
            'user_id', user['id']
        ).order('created_at', desc=True).limit(limit).execute()
        
        return {
            "success": True,
            "transactions": result.data
        }
    except Exception as e:
        log.error(f"Error getting transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payments")
async def get_user_payments(
    limit: int = 50,
    user: dict = Depends(get_current_user)
):
    """Get user's payment history"""
    try:
        supabase = get_supabase_client()
        
        result = supabase.table('payments').select('*').eq(
            'user_id', user['id']
        ).order('created_at', desc=True).limit(limit).execute()
        
        return {
            "success": True,
            "payments": result.data
        }
    except Exception as e:
        log.error(f"Error getting payments: {e}")
        raise HTTPException(status_code=500, detail=str(e))
