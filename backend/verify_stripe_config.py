"""
Verify Stripe Configuration
Checks that all required environment variables are set correctly
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('env')

print("=" * 60)
print("   STRIPE CONFIGURATION VERIFICATION")
print("=" * 60)
print()

# Check Stripe API Keys
print("🔑 Stripe API Keys:")
stripe_secret = os.getenv('STRIPE_SECRET_KEY', '')
stripe_public = os.getenv('STRIPE_PUBLISHABLE_KEY', '')

if stripe_secret:
    print(f"✅ STRIPE_SECRET_KEY: {stripe_secret[:20]}...{stripe_secret[-10:]}")
else:
    print("❌ STRIPE_SECRET_KEY: NOT SET")

if stripe_public:
    print(f"✅ STRIPE_PUBLISHABLE_KEY: {stripe_public[:20]}...{stripe_public[-10:]}")
else:
    print("❌ STRIPE_PUBLISHABLE_KEY: NOT SET")

print()

# Check Price IDs
print("💰 Stripe Price IDs:")
price_ids = {
    "Pro Monthly": os.getenv('STRIPE_PRICE_ID_PRO_MONTHLY', ''),
    "Pro Yearly": os.getenv('STRIPE_PRICE_ID_PRO_YEARLY', ''),
    "Max Monthly": os.getenv('STRIPE_PRICE_ID_MAX_MONTHLY', ''),
    "Max Yearly": os.getenv('STRIPE_PRICE_ID_MAX_YEARLY', '')
}

all_set = True
for name, price_id in price_ids.items():
    if price_id:
        print(f"✅ {name}: {price_id}")
    else:
        print(f"❌ {name}: NOT SET")
        all_set = False

print()

# Check Webhook Secret
print("🔗 Webhook Configuration:")
webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')
if webhook_secret:
    print(f"✅ STRIPE_WEBHOOK_SECRET: {webhook_secret[:20]}...")
else:
    print("⚠️  STRIPE_WEBHOOK_SECRET: NOT SET (optional for local testing)")

print()
print("=" * 60)

if all_set and stripe_secret and stripe_public:
    print("✅ ALL REQUIRED CONFIGURATION IS SET!")
    print()
    print("🚀 Ready to test:")
    print("   1. Start backend: python -m uvicorn app:app --reload --port 8080")
    print("   2. Start frontend: cd ../frontend && npm run dev")
    print("   3. Visit: http://localhost:3000/pricing")
    print("   4. Test card: 4242 4242 4242 4242")
else:
    print("❌ MISSING CONFIGURATION!")
    print()
    print("Please check your backend/env file and ensure all variables are set.")

print("=" * 60)
