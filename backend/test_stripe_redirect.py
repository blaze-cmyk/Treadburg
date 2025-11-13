"""
Test Stripe Checkout Redirect
Quick test to verify Stripe checkout session creation and redirect URL
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env.mcp')

from open_webui.integrations.stripe_integration import StripeClient

def test_checkout_redirect():
    print("=" * 60)
    print("Testing Stripe Checkout Redirect")
    print("=" * 60)
    
    try:
        # Initialize Stripe client
        print("\n1. Initializing Stripe client...")
        client = StripeClient()
        print("   ✅ Stripe client initialized")
        
        # Create a test customer
        print("\n2. Creating test customer...")
        customer_result = client.create_customer(
            email="test@tradeberg.com",
            name="Test User"
        )
        
        if not customer_result['success']:
            print(f"   ❌ Failed to create customer: {customer_result.get('error')}")
            return False
        
        customer = customer_result['customer']
        print(f"   ✅ Customer created: {customer.id}")
        
        # Create checkout session
        print("\n3. Creating checkout session...")
        checkout_result = client.create_checkout_session(
            customer_id=customer.id,
            amount=1500,  # $15.00 in cents
            currency='usd',
            success_url='http://localhost:5173/credits/success',
            cancel_url='http://localhost:5173/credits',
            metadata={
                'user_id': 'test_user_123',
                'payment_id': 'test_payment_456',
                'credits': 100
            }
        )
        
        if not checkout_result['success']:
            print(f"   ❌ Failed to create checkout: {checkout_result.get('error')}")
            return False
        
        session = checkout_result['session']
        print(f"   ✅ Checkout session created: {session.id}")
        
        # Check if we can access the URL
        print("\n4. Checking redirect URL...")
        checkout_url = session.url
        print(f"   ✅ Checkout URL: {checkout_url}")
        
        # Verify URL format
        if checkout_url and checkout_url.startswith('https://checkout.stripe.com'):
            print("\n" + "=" * 60)
            print("✅ SUCCESS! Stripe redirect is working!")
            print("=" * 60)
            print(f"\nRedirect URL: {checkout_url}")
            print("\nThis URL would redirect the user to Stripe payment page.")
            
            # Clean up - delete test customer
            import stripe
            stripe.Customer.delete(customer.id)
            print(f"\n🗑️  Test customer deleted: {customer.id}")
            
            return True
        else:
            print(f"   ❌ Invalid checkout URL: {checkout_url}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_checkout_redirect()
    sys.exit(0 if success else 1)
