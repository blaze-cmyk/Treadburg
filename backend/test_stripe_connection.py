"""
Test Stripe Connection
Quick script to verify Stripe API is working
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

def test_stripe():
    print("=" * 50)
    print("Testing Stripe Connection")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv("STRIPE_SECRET_KEY")
    if not api_key:
        print("❌ STRIPE_SECRET_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:7]}...{api_key[-4:]}")
    
    try:
        # Initialize Stripe client
        print("\n📡 Initializing Stripe client...")
        client = StripeClient()
        print("✅ Stripe client initialized")
        
        # Test creating a customer
        print("\n👤 Testing customer creation...")
        result = client.create_customer(
            email="test@example.com",
            name="Test User"
        )
        
        if result.get('success'):
            customer = result['customer']
            print(f"✅ Customer created: {customer.id}")
            print(f"   Email: {customer.email}")
            print(f"   Name: {customer.name}")
            
            # Clean up - delete test customer
            import stripe
            stripe.Customer.delete(customer.id)
            print(f"🗑️  Test customer deleted")
            
            return True
        else:
            print(f"❌ Failed to create customer: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_stripe()
    print("\n" + "=" * 50)
    if success:
        print("✅ Stripe integration is working!")
    else:
        print("❌ Stripe integration has issues")
    print("=" * 50)
    sys.exit(0 if success else 1)
