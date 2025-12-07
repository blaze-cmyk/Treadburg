"""
Stripe Integration Service
"""
import stripe
from typing import Dict, Optional
from config import settings

class StripeClient:
    """Stripe API client wrapper"""
    
    def __init__(self):
        """Initialize Stripe client"""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        if not stripe.api_key:
            raise ValueError("STRIPE_SECRET_KEY must be set in environment")
    
    def create_customer(self, email: str, name: Optional[str] = None) -> Dict:
        """Create a Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name or email
            )
            return {"success": True, "customer": customer}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_checkout_session(
        self,
        success_url: str,
        cancel_url: str,
        customer_id: Optional[str] = None,
        price_id: Optional[str] = None,
        amount: Optional[int] = None,
        currency: str = "usd",
        mode: str = "payment",
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Create a Stripe checkout session"""
        try:
            params = {
                "success_url": success_url,
                "cancel_url": cancel_url,
                "mode": mode,
                "metadata": metadata or {}
            }
            
            if customer_id:
                params["customer"] = customer_id
            
            if mode == "payment":
                if amount is not None:
                    # One-time payment with dynamic amount
                    params["line_items"] = [{
                        "price_data": {
                            "currency": currency,
                            "product_data": {
                                "name": "TradeBerg Credits",
                                "description": f"{metadata.get('credits', 0)} credits" if metadata else "Credits"
                            },
                            "unit_amount": amount
                        },
                        "quantity": 1
                    }]
                elif price_id:
                    # One-time payment with existing price
                    params["line_items"] = [{
                        "price": price_id,
                        "quantity": 1
                    }]
            elif mode == "subscription" and price_id:
                params["line_items"] = [{
                    "price": price_id,
                    "quantity": 1
                }]
            
            session = stripe.checkout.Session.create(**params)
            return {"success": True, "session": session}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def handle_webhook(self, payload: bytes, sig_header: str, webhook_secret: str) -> Dict:
        """Handle Stripe webhook events"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return {"success": True, "event": event}
        except Exception as e:
            return {"success": False, "error": str(e)}

_stripe_client = None

def get_stripe_client() -> StripeClient:
    """Get or create Stripe client instance"""
    global _stripe_client
    
    if _stripe_client is None:
        _stripe_client = StripeClient()
    
    return _stripe_client
