"""
Stripe Integration for TradeBerg

This module provides integration with Stripe for:
- Payment processing
- Subscription management
- Customer management
- Invoice generation
- Webhook handling
"""

import os
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

try:
    import stripe
except ImportError:
    stripe = None

log = logging.getLogger(__name__)


class StripeClient:
    """
    Stripe client wrapper for TradeBerg application
    
    Features:
    - Subscription management
    - Payment processing
    - Customer management
    - Invoice generation
    - Webhook verification
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        webhook_secret: Optional[str] = None
    ):
        """
        Initialize Stripe client
        
        Args:
            api_key: Stripe secret API key
            webhook_secret: Stripe webhook secret for verification
        """
        if stripe is None:
            raise ImportError(
                "stripe is not installed. "
                "Install it with: pip install stripe"
            )
        
        self.api_key = api_key or os.getenv("STRIPE_SECRET_KEY")
        self.webhook_secret = webhook_secret or os.getenv("STRIPE_WEBHOOK_SECRET")
        
        if not self.api_key:
            raise ValueError(
                "Stripe API key is required. "
                "Set STRIPE_SECRET_KEY environment variable."
            )
        
        stripe.api_key = self.api_key
        
        # Set API version if specified
        api_version = os.getenv("STRIPE_API_VERSION")
        if api_version:
            stripe.api_version = api_version
        
        log.info("Stripe client initialized successfully")
    
    # ==========================================
    # CUSTOMER MANAGEMENT
    # ==========================================
    
    async def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Create a new Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            return {"success": True, "customer": customer}
        except stripe.error.StripeError as e:
            log.error(f"Error creating customer: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_customer(self, customer_id: str) -> Optional[Dict]:
        """Get customer details"""
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return customer
        except stripe.error.StripeError as e:
            log.error(f"Error getting customer: {e}")
            return None
    
    async def update_customer(
        self,
        customer_id: str,
        **kwargs
    ) -> Dict:
        """Update customer details"""
        try:
            customer = stripe.Customer.modify(customer_id, **kwargs)
            return {"success": True, "customer": customer}
        except stripe.error.StripeError as e:
            log.error(f"Error updating customer: {e}")
            return {"success": False, "error": str(e)}
    
    async def list_customers(
        self,
        limit: int = 10,
        email: Optional[str] = None
    ) -> List[Dict]:
        """List customers"""
        try:
            params = {"limit": limit}
            if email:
                params["email"] = email
            
            customers = stripe.Customer.list(**params)
            return customers.data
        except stripe.error.StripeError as e:
            log.error(f"Error listing customers: {e}")
            return []
    
    # ==========================================
    # PRODUCT & PRICE MANAGEMENT
    # ==========================================
    
    async def create_product(
        self,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Create a new product"""
        try:
            product = stripe.Product.create(
                name=name,
                description=description,
                metadata=metadata or {}
            )
            return {"success": True, "product": product}
        except stripe.error.StripeError as e:
            log.error(f"Error creating product: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_price(
        self,
        product_id: str,
        unit_amount: int,
        currency: str = "usd",
        recurring: Optional[Dict] = None
    ) -> Dict:
        """Create a price for a product"""
        try:
            params = {
                "product": product_id,
                "unit_amount": unit_amount,
                "currency": currency
            }
            
            if recurring:
                params["recurring"] = recurring
            
            price = stripe.Price.create(**params)
            return {"success": True, "price": price}
        except stripe.error.StripeError as e:
            log.error(f"Error creating price: {e}")
            return {"success": False, "error": str(e)}
    
    async def list_products(self, limit: int = 10) -> List[Dict]:
        """List products"""
        try:
            products = stripe.Product.list(limit=limit)
            return products.data
        except stripe.error.StripeError as e:
            log.error(f"Error listing products: {e}")
            return []
    
    async def list_prices(
        self,
        product_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """List prices"""
        try:
            params = {"limit": limit}
            if product_id:
                params["product"] = product_id
            
            prices = stripe.Price.list(**params)
            return prices.data
        except stripe.error.StripeError as e:
            log.error(f"Error listing prices: {e}")
            return []
    
    # ==========================================
    # SUBSCRIPTION MANAGEMENT
    # ==========================================
    
    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Create a subscription"""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                metadata=metadata or {}
            )
            return {"success": True, "subscription": subscription}
        except stripe.error.StripeError as e:
            log.error(f"Error creating subscription: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_subscription(self, subscription_id: str) -> Optional[Dict]:
        """Get subscription details"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return subscription
        except stripe.error.StripeError as e:
            log.error(f"Error getting subscription: {e}")
            return None
    
    async def update_subscription(
        self,
        subscription_id: str,
        **kwargs
    ) -> Dict:
        """Update subscription"""
        try:
            subscription = stripe.Subscription.modify(subscription_id, **kwargs)
            return {"success": True, "subscription": subscription}
        except stripe.error.StripeError as e:
            log.error(f"Error updating subscription: {e}")
            return {"success": False, "error": str(e)}
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        at_period_end: bool = True
    ) -> Dict:
        """Cancel a subscription"""
        try:
            if at_period_end:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                subscription = stripe.Subscription.delete(subscription_id)
            
            return {"success": True, "subscription": subscription}
        except stripe.error.StripeError as e:
            log.error(f"Error canceling subscription: {e}")
            return {"success": False, "error": str(e)}
    
    async def list_subscriptions(
        self,
        customer_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """List subscriptions"""
        try:
            params = {"limit": limit}
            if customer_id:
                params["customer"] = customer_id
            if status:
                params["status"] = status
            
            subscriptions = stripe.Subscription.list(**params)
            return subscriptions.data
        except stripe.error.StripeError as e:
            log.error(f"Error listing subscriptions: {e}")
            return []
    
    # ==========================================
    # PAYMENT INTENT & CHECKOUT
    # ==========================================
    
    async def create_payment_intent(
        self,
        amount: int,
        currency: str = "usd",
        customer_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Create a payment intent"""
        try:
            params = {
                "amount": amount,
                "currency": currency,
                "metadata": metadata or {}
            }
            
            if customer_id:
                params["customer"] = customer_id
            
            payment_intent = stripe.PaymentIntent.create(**params)
            return {"success": True, "payment_intent": payment_intent}
        except stripe.error.StripeError as e:
            log.error(f"Error creating payment intent: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_checkout_session(
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
        """Create a Checkout session for one-time payment or subscription"""
        try:
            params = {
                "mode": mode,
                "success_url": success_url,
                "cancel_url": cancel_url
            }
            
            if customer_id:
                params["customer"] = customer_id
            
            if metadata:
                params["metadata"] = metadata
            
            # For one-time payments with custom amount
            if amount and mode == "payment":
                params["line_items"] = [{
                    "price_data": {
                        "currency": currency,
                        "unit_amount": amount,
                        "product_data": {
                            "name": "TradeBerg Credits",
                            "description": f"Purchase {metadata.get('credits', 0)} credits" if metadata else "Credits purchase"
                        }
                    },
                    "quantity": 1
                }]
            # For subscriptions with price_id
            elif price_id:
                params["line_items"] = [{"price": price_id, "quantity": 1}]
            else:
                raise ValueError("Either price_id or amount must be provided")
            
            session = stripe.checkout.Session.create(**params)
            return {"success": True, "session": session}
        except stripe.error.StripeError as e:
            log.error(f"Error creating checkout session: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            log.error(f"Unexpected error creating checkout session: {e}")
            return {"success": False, "error": str(e)}
    
    # ==========================================
    # INVOICE MANAGEMENT
    # ==========================================
    
    async def create_invoice(
        self,
        customer_id: str,
        auto_advance: bool = True
    ) -> Dict:
        """Create an invoice"""
        try:
            invoice = stripe.Invoice.create(
                customer=customer_id,
                auto_advance=auto_advance
            )
            return {"success": True, "invoice": invoice}
        except stripe.error.StripeError as e:
            log.error(f"Error creating invoice: {e}")
            return {"success": False, "error": str(e)}
    
    async def finalize_invoice(self, invoice_id: str) -> Dict:
        """Finalize an invoice"""
        try:
            invoice = stripe.Invoice.finalize_invoice(invoice_id)
            return {"success": True, "invoice": invoice}
        except stripe.error.StripeError as e:
            log.error(f"Error finalizing invoice: {e}")
            return {"success": False, "error": str(e)}
    
    async def list_invoices(
        self,
        customer_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """List invoices"""
        try:
            params = {"limit": limit}
            if customer_id:
                params["customer"] = customer_id
            
            invoices = stripe.Invoice.list(**params)
            return invoices.data
        except stripe.error.StripeError as e:
            log.error(f"Error listing invoices: {e}")
            return []
    
    # ==========================================
    # WEBHOOK HANDLING
    # ==========================================
    
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str
    ) -> Optional[Dict]:
        """Verify webhook signature and return event"""
        if not self.webhook_secret:
            log.warning("Webhook secret not configured")
            return None
        
        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                self.webhook_secret
            )
            return event
        except stripe.error.SignatureVerificationError as e:
            log.error(f"Webhook signature verification failed: {e}")
            return None
    
    async def handle_webhook_event(self, event: Dict) -> Dict:
        """Handle webhook event"""
        event_type = event.get("type")
        
        handlers = {
            "customer.subscription.created": self._handle_subscription_created,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.payment_succeeded": self._handle_payment_succeeded,
            "invoice.payment_failed": self._handle_payment_failed,
        }
        
        handler = handlers.get(event_type)
        if handler:
            return await handler(event)
        
        log.info(f"Unhandled webhook event type: {event_type}")
        return {"success": True, "message": "Event received"}
    
    async def _handle_subscription_created(self, event: Dict) -> Dict:
        """Handle subscription created event"""
        subscription = event["data"]["object"]
        log.info(f"Subscription created: {subscription['id']}")
        # Add your custom logic here
        return {"success": True}
    
    async def _handle_subscription_updated(self, event: Dict) -> Dict:
        """Handle subscription updated event"""
        subscription = event["data"]["object"]
        log.info(f"Subscription updated: {subscription['id']}")
        # Add your custom logic here
        return {"success": True}
    
    async def _handle_subscription_deleted(self, event: Dict) -> Dict:
        """Handle subscription deleted event"""
        subscription = event["data"]["object"]
        log.info(f"Subscription deleted: {subscription['id']}")
        # Add your custom logic here
        return {"success": True}
    
    async def _handle_payment_succeeded(self, event: Dict) -> Dict:
        """Handle payment succeeded event"""
        invoice = event["data"]["object"]
        log.info(f"Payment succeeded for invoice: {invoice['id']}")
        # Add your custom logic here
        return {"success": True}
    
    async def _handle_payment_failed(self, event: Dict) -> Dict:
        """Handle payment failed event"""
        invoice = event["data"]["object"]
        log.warning(f"Payment failed for invoice: {invoice['id']}")
        # Add your custom logic here
        return {"success": True}


# Global instance
_stripe_client: Optional[StripeClient] = None


def get_stripe_client() -> StripeClient:
    """Get or create global Stripe client instance"""
    global _stripe_client
    
    if _stripe_client is None:
        _stripe_client = StripeClient()
    
    return _stripe_client
