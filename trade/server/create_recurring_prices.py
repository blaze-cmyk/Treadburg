"""
Create recurring subscription prices for TradeBerg products
"""
import os
import stripe
from dotenv import load_dotenv

# Load environment variables
load_dotenv('env')

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Product IDs (from MCP creation)
PRO_PRODUCT_ID = "prod_TYWiucPaWRXTll"
MAX_PRODUCT_ID = "prod_TYWimsIVaBVOZb"

print("🚀 Creating recurring subscription prices...\n")

try:
    # Create Pro Monthly Price ($20/month)
    print("📦 Creating Pro Monthly price...")
    pro_monthly = stripe.Price.create(
        product=PRO_PRODUCT_ID,
        unit_amount=2000,  # $20.00
        currency="usd",
        recurring={"interval": "month"},
        nickname="Pro Monthly"
    )
    print(f"✅ Pro Monthly: {pro_monthly.id} - $20.00/month\n")
    
    # Create Pro Yearly Price ($200/year)
    print("📦 Creating Pro Yearly price...")
    pro_yearly = stripe.Price.create(
        product=PRO_PRODUCT_ID,
        unit_amount=20000,  # $200.00
        currency="usd",
        recurring={"interval": "year"},
        nickname="Pro Yearly"
    )
    print(f"✅ Pro Yearly: {pro_yearly.id} - $200.00/year\n")
    
    # Create Max Monthly Price ($200/month)
    print("📦 Creating Max Monthly price...")
    max_monthly = stripe.Price.create(
        product=MAX_PRODUCT_ID,
        unit_amount=20000,  # $200.00
        currency="usd",
        recurring={"interval": "month"},
        nickname="Max Monthly"
    )
    print(f"✅ Max Monthly: {max_monthly.id} - $200.00/month\n")
    
    # Create Max Yearly Price ($2000/year)
    print("📦 Creating Max Yearly price...")
    max_yearly = stripe.Price.create(
        product=MAX_PRODUCT_ID,
        unit_amount=200000,  # $2000.00
        currency="usd",
        recurring={"interval": "year"},
        nickname="Max Yearly"
    )
    print(f"✅ Max Yearly: {max_yearly.id} - $2000.00/year\n")
    
    # Print summary
    print("=" * 60)
    print("🎉 SUCCESS! All recurring prices created!")
    print("=" * 60)
    print("\n📋 Add these to your backend/env file:\n")
    print(f"STRIPE_PRICE_PRO_MONTHLY={pro_monthly.id}")
    print(f"STRIPE_PRICE_PRO_YEARLY={pro_yearly.id}")
    print(f"STRIPE_PRICE_MAX_MONTHLY={max_monthly.id}")
    print(f"STRIPE_PRICE_MAX_YEARLY={max_yearly.id}")
    print("\n" + "=" * 60)
    
except stripe.error.StripeError as e:
    print(f"\n❌ Stripe Error: {e}")
except Exception as e:
    print(f"\n❌ Error: {e}")
