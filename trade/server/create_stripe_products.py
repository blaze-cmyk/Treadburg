"""
Automated Stripe Product Creation Script
Run this to automatically create products and prices in Stripe
"""
import os
import stripe
from dotenv import load_dotenv

# Load environment variables
load_dotenv('env')

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def create_products():
    """Create TradeBerg subscription products in Stripe"""
    
    print("🚀 Creating Stripe Products for TradeBerg...\n")
    
    # Check if using test key
    if not stripe.api_key or not stripe.api_key.startswith('sk_test_'):
        print("⚠️  WARNING: Not using test key!")
        print("Please use TEST keys for development.")
        response = input("Continue anyway? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return
    
    try:
        # Create Pro Plan
        print("📦 Creating Pro Plan...")
        pro_product = stripe.Product.create(
            name="TradeBerg Pro",
            description="Professional trading analysis with advanced features",
            metadata={
                "tier": "pro",
                "features": "10x citations, Unlimited uploads, Extended image generation, Pro search"
            }
        )
        print(f"✅ Pro Product created: {pro_product.id}")
        
        # Create Pro Monthly Price
        pro_monthly = stripe.Price.create(
            product=pro_product.id,
            unit_amount=2000,  # $20.00
            currency="usd",
            recurring={"interval": "month"},
            nickname="Pro Monthly"
        )
        print(f"✅ Pro Monthly Price: {pro_monthly.id}")
        
        # Create Pro Yearly Price
        pro_yearly = stripe.Price.create(
            product=pro_product.id,
            unit_amount=20000,  # $200.00
            currency="usd",
            recurring={"interval": "year"},
            nickname="Pro Yearly"
        )
        print(f"✅ Pro Yearly Price: {pro_yearly.id}\n")
        
        # Create Max Plan
        print("📦 Creating Max Plan...")
        max_product = stripe.Product.create(
            name="TradeBerg Max",
            description="Maximum features with priority support and early access",
            metadata={
                "tier": "max",
                "features": "Everything in Pro, Early access, Enhanced video, Priority support"
            }
        )
        print(f"✅ Max Product created: {max_product.id}")
        
        # Create Max Monthly Price
        max_monthly = stripe.Price.create(
            product=max_product.id,
            unit_amount=20000,  # $200.00
            currency="usd",
            recurring={"interval": "month"},
            nickname="Max Monthly"
        )
        print(f"✅ Max Monthly Price: {max_monthly.id}")
        
        # Create Max Yearly Price
        max_yearly = stripe.Price.create(
            product=max_product.id,
            unit_amount=200000,  # $2000.00
            currency="usd",
            recurring={"interval": "year"},
            nickname="Max Yearly"
        )
        print(f"✅ Max Yearly Price: {max_yearly.id}\n")
        
        # Print summary
        print("=" * 60)
        print("🎉 SUCCESS! All products created!")
        print("=" * 60)
        print("\n📋 Add these to your backend/env file:\n")
        print(f"STRIPE_PRICE_PRO_MONTHLY={pro_monthly.id}")
        print(f"STRIPE_PRICE_PRO_YEARLY={pro_yearly.id}")
        print(f"STRIPE_PRICE_MAX_MONTHLY={max_monthly.id}")
        print(f"STRIPE_PRICE_MAX_YEARLY={max_yearly.id}")
        print("\n" + "=" * 60)
        print("\n✅ Next steps:")
        print("1. Copy the price IDs above to backend/env")
        print("2. Restart your backend server")
        print("3. Test checkout at http://localhost:3000/pricing")
        print("4. Use test card: 4242 4242 4242 4242")
        
    except stripe.error.StripeError as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("- Check your STRIPE_SECRET_KEY in backend/env")
        print("- Make sure you're using a TEST key (starts with sk_test_)")
        print("- Verify your Stripe account is active")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    create_products()
