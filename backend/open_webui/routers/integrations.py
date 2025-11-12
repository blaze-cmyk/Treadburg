"""
API Router for Supabase and Stripe Integrations

This module provides REST API endpoints for:
- Supabase database operations
- Stripe payment processing
- Subscription management
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel, EmailStr

from open_webui.utils.auth import get_verified_user
from open_webui.models.users import UserModel
from open_webui.integrations.supabase_integration import get_supabase_client
from open_webui.integrations.stripe_integration import get_stripe_client

log = logging.getLogger(__name__)
router = APIRouter()


# ==========================================
# REQUEST/RESPONSE MODELS
# ==========================================

class UserProfileRequest(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class MarketAnalysisRequest(BaseModel):
    symbol: str
    timeframe: Optional[str] = None
    analysis_type: Optional[str] = None
    analysis_data: Dict[str, Any]
    confidence_score: Optional[float] = None


class SubscriptionRequest(BaseModel):
    price_id: str
    success_url: str
    cancel_url: str


class WebhookRequest(BaseModel):
    payload: bytes
    signature: str


# ==========================================
# SUPABASE ENDPOINTS
# ==========================================

@router.get("/supabase/profile")
async def get_user_profile(user: UserModel = Depends(get_verified_user)):
    """Get user profile from Supabase"""
    try:
        supabase = get_supabase_client()
        profile = await supabase.get_user_profile(user.id)
        
        if not profile:
            return {"success": False, "message": "Profile not found"}
        
        return {"success": True, "profile": profile}
    except Exception as e:
        log.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/supabase/profile")
async def create_or_update_profile(
    profile_data: UserProfileRequest,
    user: UserModel = Depends(get_verified_user)
):
    """Create or update user profile in Supabase"""
    try:
        supabase = get_supabase_client()
        
        data = {
            "email": user.email,
            **profile_data.dict(exclude_none=True)
        }
        
        result = await supabase.create_user_profile(user.id, data)
        return result
    except Exception as e:
        log.error(f"Error creating/updating profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/supabase/analysis")
async def save_market_analysis(
    analysis: MarketAnalysisRequest,
    user: UserModel = Depends(get_verified_user)
):
    """Save market analysis to Supabase"""
    try:
        supabase = get_supabase_client()
        
        result = await supabase.save_market_analysis(
            user.id,
            analysis.symbol,
            analysis.dict()
        )
        return result
    except Exception as e:
        log.error(f"Error saving market analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supabase/analyses")
async def get_user_analyses(
    symbol: Optional[str] = None,
    limit: int = 50,
    user: UserModel = Depends(get_verified_user)
):
    """Get user's market analyses from Supabase"""
    try:
        supabase = get_supabase_client()
        analyses = await supabase.get_user_analyses(user.id, limit, symbol)
        
        return {"success": True, "analyses": analyses}
    except Exception as e:
        log.error(f"Error getting analyses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supabase/chat-history/{chat_id}")
async def get_chat_history(
    chat_id: str,
    limit: int = 100,
    user: UserModel = Depends(get_verified_user)
):
    """Get chat history from Supabase"""
    try:
        supabase = get_supabase_client()
        messages = await supabase.get_chat_history(user.id, chat_id, limit)
        
        return {"success": True, "messages": messages}
    except Exception as e:
        log.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# STRIPE ENDPOINTS
# ==========================================

@router.post("/stripe/customer")
async def create_stripe_customer(user: UserModel = Depends(get_verified_user)):
    """Create a Stripe customer"""
    try:
        stripe_client = get_stripe_client()
        
        result = await stripe_client.create_customer(
            email=user.email,
            name=user.name,
            metadata={"user_id": user.id}
        )
        
        if result["success"]:
            # Save customer ID to Supabase
            supabase = get_supabase_client()
            await supabase.create_user_profile(
                user.id,
                {"stripe_customer_id": result["customer"]["id"]}
            )
        
        return result
    except Exception as e:
        log.error(f"Error creating Stripe customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stripe/products")
async def list_products(user: UserModel = Depends(get_verified_user)):
    """List available products"""
    try:
        stripe_client = get_stripe_client()
        products = await stripe_client.list_products(limit=20)
        
        return {"success": True, "products": products}
    except Exception as e:
        log.error(f"Error listing products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stripe/prices")
async def list_prices(
    product_id: Optional[str] = None,
    user: UserModel = Depends(get_verified_user)
):
    """List available prices"""
    try:
        stripe_client = get_stripe_client()
        prices = await stripe_client.list_prices(product_id=product_id, limit=20)
        
        return {"success": True, "prices": prices}
    except Exception as e:
        log.error(f"Error listing prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stripe/checkout")
async def create_checkout_session(
    subscription: SubscriptionRequest,
    user: UserModel = Depends(get_verified_user)
):
    """Create a Stripe Checkout session"""
    try:
        stripe_client = get_stripe_client()
        
        # Get or create customer
        supabase = get_supabase_client()
        profile = await supabase.get_user_profile(user.id)
        
        customer_id = None
        if profile and profile.get("stripe_customer_id"):
            customer_id = profile["stripe_customer_id"]
        else:
            # Create new customer
            customer_result = await stripe_client.create_customer(
                email=user.email,
                name=user.name,
                metadata={"user_id": user.id}
            )
            if customer_result["success"]:
                customer_id = customer_result["customer"]["id"]
                await supabase.create_user_profile(
                    user.id,
                    {"stripe_customer_id": customer_id}
                )
        
        # Create checkout session
        result = await stripe_client.create_checkout_session(
            price_id=subscription.price_id,
            success_url=subscription.success_url,
            cancel_url=subscription.cancel_url,
            customer_id=customer_id
        )
        
        return result
    except Exception as e:
        log.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stripe/subscription")
async def get_user_subscription(user: UserModel = Depends(get_verified_user)):
    """Get user's active subscription"""
    try:
        supabase = get_supabase_client()
        subscription = await supabase.get_user_subscription(user.id)
        
        if not subscription:
            return {"success": True, "subscription": None}
        
        return {"success": True, "subscription": subscription}
    except Exception as e:
        log.error(f"Error getting subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stripe/subscription/cancel")
async def cancel_subscription(
    at_period_end: bool = True,
    user: UserModel = Depends(get_verified_user)
):
    """Cancel user's subscription"""
    try:
        supabase = get_supabase_client()
        subscription = await supabase.get_user_subscription(user.id)
        
        if not subscription or not subscription.get("stripe_subscription_id"):
            raise HTTPException(status_code=404, detail="No active subscription found")
        
        stripe_client = get_stripe_client()
        result = await stripe_client.cancel_subscription(
            subscription["stripe_subscription_id"],
            at_period_end=at_period_end
        )
        
        if result["success"]:
            # Update subscription in Supabase
            await supabase.save_subscription(
                user.id,
                {
                    "status": "canceled" if not at_period_end else "active",
                    "cancel_at_period_end": at_period_end
                }
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error canceling subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stripe/webhook")
async def handle_stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature")
):
    """Handle Stripe webhook events"""
    try:
        payload = await request.body()
        
        stripe_client = get_stripe_client()
        event = stripe_client.verify_webhook_signature(payload, stripe_signature)
        
        if not event:
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        result = await stripe_client.handle_webhook_event(event)
        
        # Additional handling based on event type
        event_type = event.get("type")
        if event_type in ["customer.subscription.created", "customer.subscription.updated"]:
            # Update subscription in Supabase
            subscription = event["data"]["object"]
            customer_id = subscription["customer"]
            
            # Find user by customer ID
            supabase = get_supabase_client()
            # Note: You'll need to implement a way to find user by stripe_customer_id
            # This is a simplified example
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error handling webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# HEALTH CHECK
# ==========================================

@router.get("/health")
async def health_check():
    """Check integration health"""
    try:
        supabase_ok = False
        stripe_ok = False
        
        try:
            supabase = get_supabase_client()
            supabase_ok = True
        except Exception as e:
            log.error(f"Supabase health check failed: {e}")
        
        try:
            stripe_client = get_stripe_client()
            stripe_ok = True
        except Exception as e:
            log.error(f"Stripe health check failed: {e}")
        
        return {
            "success": True,
            "integrations": {
                "supabase": {"status": "ok" if supabase_ok else "error"},
                "stripe": {"status": "ok" if stripe_ok else "error"}
            }
        }
    except Exception as e:
        log.error(f"Health check error: {e}")
        return {"success": False, "error": str(e)}
