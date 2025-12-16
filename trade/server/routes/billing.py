"""
Billing and Stripe Integration Routes
"""
from fastapi import APIRouter, HTTPException, Request, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os

from services.stripe_service import get_stripe_client
from config import settings
from database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/billing", tags=["billing"])

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class CheckoutSessionRequest(BaseModel):
    price_id: Optional[str] = None
    mode: str = "subscription"  # "subscription" or "payment"
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None
    customer_email: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PortalSessionRequest(BaseModel):
    customer_id: str
    return_url: Optional[str] = None

class SubscriptionTier(BaseModel):
    name: str
    price_monthly: float
    price_yearly: Optional[float] = None
    features: List[str]
    stripe_price_id_monthly: Optional[str] = None
    stripe_price_id_yearly: Optional[str] = None
    popular: bool = False

class CreditPackage(BaseModel):
    name: str
    credits: int
    price: float
    stripe_price_id: Optional[str] = None
    savings: Optional[str] = None

# ---------------------------------------------------------------------------
# Subscription Tiers Configuration
# ---------------------------------------------------------------------------

SUBSCRIPTION_TIERS = [
    {
        "id": "free",
        "name": "Free",
        "price_monthly": 0,
        "price_yearly": 0,
        "features": [
            "100 messages per month",
            "Basic AI responses",
            "Limited chart access",
            "Community support"
        ],
        "popular": False
    },
    {
        "id": "pro",
        "name": "Pro",
        "price_monthly": 20,  # Updated from strip folder
        "price_yearly": 200,  # $20/month * 10 months (2 months free)
        "stripe_price_id_monthly": settings.STRIPE_PRICE_ID_PRO_MONTHLY,
        "stripe_price_id_yearly": settings.STRIPE_PRICE_ID_PRO_YEARLY,
        "features": [
            "Unlimited messages",
            "10x as many citations in answers",
            "Advanced AI (Gemini + Perplexity)",
            "Full chart access",
            "SEC filing analysis",
            "Unlimited file and photo uploads",
            "Extended access to image generation",
            "Technical indicators",
            "Priority support"
        ],
        "popular": True
    },
    {
        "id": "max",  # Renamed from enterprise to match strip folder
        "name": "Max",
        "price_monthly": 200,  # Updated from strip folder
        "price_yearly": 2000,  # $200/month * 10 months (2 months free)
        "stripe_price_id_monthly": settings.STRIPE_PRICE_ID_MAX_MONTHLY,
        "stripe_price_id_yearly": settings.STRIPE_PRICE_ID_MAX_YEARLY,
        "features": [
            "Everything in Pro",
            "Early access to newest products",
            "Unlimited access to advanced AI models",
            "Enhanced access to video generation",
            "Custom AI training",
            "API access",
            "Dedicated support",
            "White-label option",
            "Team collaboration"
        ],
        "popular": False
    }
]

CREDIT_PACKAGES = [
    {
        "id": "starter",
        "name": "Starter Pack",
        "credits": 100,
        "price": 9.99,
        "stripe_price_id": os.getenv("STRIPE_PRICE_ID_CREDITS_100", ""),
        "savings": None
    },
    {
        "id": "popular",
        "name": "Popular Pack",
        "credits": 500,
        "price": 39.99,
        "stripe_price_id": os.getenv("STRIPE_PRICE_ID_CREDITS_500", ""),
        "savings": "Save 20%"
    },
    {
        "id": "pro",
        "name": "Pro Pack",
        "credits": 1000,
        "price": 69.99,
        "stripe_price_id": os.getenv("STRIPE_PRICE_ID_CREDITS_1000", ""),
        "savings": "Save 30%"
    }
]

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/pricing")
async def get_pricing():
    """Get available subscription tiers and credit packages"""
    return JSONResponse({
        "success": True,
        "subscriptions": SUBSCRIPTION_TIERS,
        "credits": CREDIT_PACKAGES
    })

@router.post("/create-checkout-session")
async def create_checkout_session(request: CheckoutSessionRequest):
    """
    Create a Stripe checkout session for subscription or one-time payment
    """
    try:
        stripe_client = get_stripe_client()
        
        # Default URLs if not provided
        base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        success_url = request.success_url or f"{base_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = request.cancel_url or f"{base_url}/billing/cancel"
        
        # Create checkout session
        result = stripe_client.create_checkout_session(
            success_url=success_url,
            cancel_url=cancel_url,
            price_id=request.price_id,
            mode=request.mode,
            metadata=request.metadata or {}
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create checkout session"))
        
        session = result["session"]
        
        return JSONResponse({
            "success": True,
            "session_id": session.id,
            "url": session.url
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-portal-session")
async def create_portal_session(request: PortalSessionRequest):
    """
    Create a Stripe customer portal session for subscription management
    """
    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return_url = request.return_url or f"{base_url}/billing"
        
        session = stripe.billing_portal.Session.create(
            customer=request.customer_id,
            return_url=return_url
        )
        
        return JSONResponse({
            "success": True,
            "url": session.url
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events
    """
    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        
        if not webhook_secret:
            raise HTTPException(status_code=500, detail="Webhook secret not configured")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Handle the event
        event_type = event["type"]
        event_data = event["data"]["object"]
        
        if event_type == "checkout.session.completed":
            # Payment successful
            session = event_data
            customer_id = session.get("customer")
            subscription_id = session.get("subscription")
            
            # TODO: Update database with subscription info
            print(f"✅ Checkout completed: customer={customer_id}, subscription={subscription_id}")
            
        elif event_type == "customer.subscription.created":
            # New subscription created
            subscription = event_data
            customer_id = subscription.get("customer")
            
            # TODO: Update database
            print(f"✅ Subscription created: {subscription.get('id')}")
            
        elif event_type == "customer.subscription.updated":
            # Subscription updated (e.g., plan change)
            subscription = event_data
            
            # TODO: Update database
            print(f"✅ Subscription updated: {subscription.get('id')}")
            
        elif event_type == "customer.subscription.deleted":
            # Subscription cancelled
            subscription = event_data
            
            # TODO: Update database
            print(f"✅ Subscription cancelled: {subscription.get('id')}")
            
        elif event_type == "invoice.paid":
            # Invoice paid successfully
            invoice = event_data
            
            # TODO: Update payment records
            print(f"✅ Invoice paid: {invoice.get('id')}")
            
        elif event_type == "invoice.payment_failed":
            # Invoice payment failed
            invoice = event_data
            
            # TODO: Handle failed payment
            print(f"❌ Invoice payment failed: {invoice.get('id')}")
        
        return JSONResponse({"success": True, "received": True})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subscription-status")
async def get_subscription_status(customer_id: Optional[str] = None):
    """
    Get subscription status for a customer
    """
    try:
        if not customer_id:
            return JSONResponse({
                "success": True,
                "subscription": None,
                "tier": "free"
            })
        
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Get customer's subscriptions
        subscriptions = stripe.Subscription.list(
            customer=customer_id,
            status="active",
            limit=1
        )
        
        if subscriptions.data:
            subscription = subscriptions.data[0]
            
            return JSONResponse({
                "success": True,
                "subscription": {
                    "id": subscription.id,
                    "status": subscription.status,
                    "current_period_end": subscription.current_period_end,
                    "cancel_at_period_end": subscription.cancel_at_period_end,
                    "plan": subscription.plan.nickname or "Pro"
                },
                "tier": "pro"  # TODO: Determine tier from price_id
            })
        else:
            return JSONResponse({
                "success": True,
                "subscription": None,
                "tier": "free"
            })
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cancel-subscription")
async def cancel_subscription(customer_id: str):
    """
    Cancel a customer's subscription at period end
    """
    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Get active subscription
        subscriptions = stripe.Subscription.list(
            customer=customer_id,
            status="active",
            limit=1
        )
        
        if not subscriptions.data:
            raise HTTPException(status_code=404, detail="No active subscription found")
        
        subscription = subscriptions.data[0]
        
        # Cancel at period end
        updated_subscription = stripe.Subscription.modify(
            subscription.id,
            cancel_at_period_end=True
        )
        
        return JSONResponse({
            "success": True,
            "subscription": {
                "id": updated_subscription.id,
                "cancel_at_period_end": updated_subscription.cancel_at_period_end,
                "current_period_end": updated_subscription.current_period_end
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
