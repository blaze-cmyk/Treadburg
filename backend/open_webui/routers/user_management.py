"""
User Management API Router
Handles user profiles, credits, payments, and authentication
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
import os

from open_webui.integrations.supabase_integration import get_supabase_client
from open_webui.integrations.stripe_integration import get_stripe_client

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
    amount: float = 15.00  # Default $15
    credits: int = 100  # Default 100 credits
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
        user_response = supabase.client.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get user profile from database
        user_data = supabase.client.table('users').select('*').eq('auth_user_id', user_response.user.id).single().execute()
        
        if not user_data.data:
            # Create user profile if doesn't exist
            new_user = {
                'auth_user_id': user_response.user.id,
                'email': user_response.user.email,
                'email_confirmed': user_response.user.email_confirmed_at is not None,
                'credits': 0
            }
            user_data = supabase.client.table('users').insert(new_user).execute()
        
        return user_data.data
        
    except Exception as e:
        log.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_admin_user(user: dict = Depends(get_current_user)):
    """Verify user is admin"""
    if not user.get('is_admin'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user

# ============================================
# USER PROFILE ENDPOINTS
# ============================================

@router.get("/profile")
async def get_user_profile(user: dict = Depends(get_current_user)):
    """Get current user's profile"""
    try:
        supabase = get_supabase_client()
        
        # Get user stats
        stats_response = supabase.client.rpc('get_user_stats', {'p_user_id': user['id']}).execute()
        
        return {
            "success": True,
            "user": {
                "id": user['id'],
                "email": user['email'],
                "username": user.get('username'),
                "full_name": user.get('full_name'),
                "avatar_url": user.get('avatar_url'),
                "bio": user.get('bio'),
                "credits": user.get('credits', 0),
                "subscription_tier": user.get('subscription_tier', 'free'),
                "subscription_status": user.get('subscription_status', 'inactive'),
                "is_verified": user.get('is_verified', False),
                "created_at": user.get('created_at'),
                "last_login_at": user.get('last_login_at')
            },
            "stats": stats_response.data if stats_response.data else {}
        }
    except Exception as e:
        log.error(f"Error fetching profile: {e}")
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
        
        response = supabase.client.table('users').update(update_data).eq('id', user['id']).execute()
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "user": response.data[0] if response.data else None
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
        supabase = get_supabase_client()
        stripe_client = get_stripe_client()
        
        # Get or create user in Supabase
        user_response = supabase.client.table('users').select('*').eq('auth_user_id', user['id']).execute()
        
        if not user_response.data:
            # Auto-create user in Supabase if doesn't exist
            log.info(f"Creating user in Supabase: {user.get('email')}")
            new_user_data = {
                'auth_user_id': user['id'],
                'email': user.get('email'),
                'username': user.get('name'),
                'full_name': user.get('name'),
                'avatar_url': user.get('profile_image_url'),
                'credits': 0,
                'subscription_tier': 'free',
                'subscription_status': 'inactive',
                'is_verified': True
            }
            user_response = supabase.client.table('users').insert(new_user_data).execute()
            
            if not user_response.data:
                raise HTTPException(status_code=500, detail="Failed to create user in database")
        
        # Ensure user has Stripe customer ID
        stripe_customer_id = user_response.data[0].get('stripe_customer_id')
        if not stripe_customer_id:
            # Create Stripe customer
            customer_result = stripe_client.create_customer(
                email=user.get('email'),
                name=user.get('full_name') or user.get('email'),
                metadata={'user_id': user['id']}
            )
            
            if customer_result['success']:
                stripe_customer_id = customer_result['customer'].id  # Access as attribute
                # Update user with Stripe customer ID
                supabase.client.table('users').update({
                    'stripe_customer_id': stripe_customer_id
                }).eq('id', user_response.data[0]['id']).execute()  # Use correct user ID
        
        # Create payment record
        supabase_user_id = user_response.data[0]['id']
        payment_data = {
            'user_id': supabase_user_id,  # Use Supabase user ID
            'amount': purchase.amount,
            'credits_purchased': purchase.credits,
            'status': 'pending',
            'stripe_customer_id': stripe_customer_id
        }
        payment_response = supabase.client.table('payments').insert(payment_data).execute()
        payment_id = payment_response.data[0]['id']
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
                'user_id': user_response.data[0]['id'],  # Use Supabase user ID
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
            "checkout_url": session.url,  # Access as attribute, not dict
            "session_id": session.id,     # Access as attribute, not dict
            "payment_id": payment_id
        }
        
    except Exception as e:
        log.error(f"Error creating checkout: {e}")
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
        has_credits = supabase.client.rpc('check_user_credits', {
            'p_user_id': user['id'],
            'p_required_credits': usage.credits
        }).execute()
        
        if not has_credits.data:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Insufficient credits"
            )
        
        # Deduct credits
        result = supabase.client.rpc('update_user_credits', {
            'p_user_id': user['id'],
            'p_amount': -usage.credits,
            'p_transaction_type': 'usage',
            'p_description': usage.description
        }).execute()
        
        # Log API usage
        if usage.endpoint:
            supabase.client.table('api_usage_log').insert({
                'user_id': user['id'],
                'endpoint': usage.endpoint,
                'method': 'POST',
                'credits_used': usage.credits
            }).execute()
        
        return {
            "success": True,
            "credits_used": usage.credits,
            "new_balance": result.data['new_balance']
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
        
        response = supabase.client.table('credit_transactions')\
            .select('*')\
            .eq('user_id', user['id'])\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        return {
            "success": True,
            "transactions": response.data
        }
    except Exception as e:
        log.error(f"Error fetching transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# PAYMENT ENDPOINTS
# ============================================

@router.get("/payments")
async def get_user_payments(
    limit: int = 50,
    user: dict = Depends(get_current_user)
):
    """Get user's payment history"""
    try:
        supabase = get_supabase_client()
        
        response = supabase.client.table('payments')\
            .select('*')\
            .eq('user_id', user['id'])\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        return {
            "success": True,
            "payments": response.data
        }
    except Exception as e:
        log.error(f"Error fetching payments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks for payment events"""
    try:
        stripe_client = get_stripe_client()
        supabase = get_supabase_client()
        
        # Get webhook signature
        signature = request.headers.get('stripe-signature')
        payload = await request.body()
        
        # Verify webhook
        event = stripe_client.verify_webhook(payload, signature)
        
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            metadata = session.get('metadata', {})
            
            user_id = metadata.get('user_id')
            payment_id = metadata.get('payment_id')
            credits = int(metadata.get('credits', 0))
            
            # Update payment status
            supabase.client.table('payments').update({
                'status': 'succeeded',
                'stripe_payment_intent_id': session.get('payment_intent'),
                'paid_at': datetime.now().isoformat()
            }).eq('id', payment_id).execute()
            
            # Add credits to user
            supabase.client.rpc('update_user_credits', {
                'p_user_id': user_id,
                'p_amount': credits,
                'p_transaction_type': 'purchase',
                'p_description': f'Purchased {credits} credits',
                'p_payment_id': payment_id
            }).execute()
            
            log.info(f"Credits added: {credits} for user {user_id}")
        
        return {"success": True}
        
    except Exception as e:
        log.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ============================================
# SUBSCRIPTION ENDPOINTS
# ============================================

@router.get("/subscription")
async def get_user_subscription(user: dict = Depends(get_current_user)):
    """Get user's subscription details"""
    try:
        supabase = get_supabase_client()
        
        response = supabase.client.table('subscriptions')\
            .select('*')\
            .eq('user_id', user['id'])\
            .eq('status', 'active')\
            .execute()
        
        return {
            "success": True,
            "subscription": response.data[0] if response.data else None,
            "tier": user.get('subscription_tier', 'free'),
            "status": user.get('subscription_status', 'inactive')
        }
    except Exception as e:
        log.error(f"Error fetching subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# ADMIN ENDPOINTS
# ============================================

@router.get("/admin/users")
async def admin_get_all_users(
    limit: int = 100,
    offset: int = 0,
    admin: dict = Depends(get_admin_user)
):
    """Get all users (admin only)"""
    try:
        supabase = get_supabase_client()
        
        response = supabase.client.from_('admin_user_overview')\
            .select('*')\
            .order('created_at', desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        return {
            "success": True,
            "users": response.data,
            "count": len(response.data)
        }
    except Exception as e:
        log.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/stats")
async def admin_get_stats(admin: dict = Depends(get_admin_user)):
    """Get platform statistics (admin only)"""
    try:
        supabase = get_supabase_client()
        
        # Total users
        users_count = supabase.client.table('users').select('id', count='exact').execute()
        
        # Total revenue
        revenue = supabase.client.table('payments')\
            .select('amount')\
            .eq('status', 'succeeded')\
            .execute()
        total_revenue = sum(p['amount'] for p in revenue.data) if revenue.data else 0
        
        # Active subscriptions
        active_subs = supabase.client.table('subscriptions')\
            .select('id', count='exact')\
            .eq('status', 'active')\
            .execute()
        
        # Recent activity
        recent_users = supabase.client.table('users')\
            .select('id', count='exact')\
            .gte('created_at', (datetime.now() - timedelta(days=7)).isoformat())\
            .execute()
        
        return {
            "success": True,
            "stats": {
                "total_users": users_count.count,
                "total_revenue": float(total_revenue),
                "active_subscriptions": active_subs.count,
                "new_users_this_week": recent_users.count
            }
        }
    except Exception as e:
        log.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/users/{user_id}/credits")
async def admin_adjust_credits(
    user_id: str,
    amount: int,
    description: str,
    admin: dict = Depends(get_admin_user)
):
    """Adjust user credits (admin only)"""
    try:
        supabase = get_supabase_client()
        
        result = supabase.client.rpc('update_user_credits', {
            'p_user_id': user_id,
            'p_amount': amount,
            'p_transaction_type': 'admin_adjustment',
            'p_description': description
        }).execute()
        
        # Log admin activity
        supabase.client.table('admin_activity_log').insert({
            'admin_user_id': admin['id'],
            'action': 'adjust_credits',
            'target_user_id': user_id,
            'description': f'Adjusted credits by {amount}: {description}'
        }).execute()
        
        return {
            "success": True,
            "new_balance": result.data['new_balance']
        }
    except Exception as e:
        log.error(f"Error adjusting credits: {e}")
        raise HTTPException(status_code=500, detail=str(e))
