"""Quick test script for Supabase and Stripe integrations"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.mcp")

print("=" * 60)
print("  Testing Supabase & Stripe Integrations")
print("=" * 60)

# Test Supabase
print("\n🔵 Testing Supabase Connection...")
try:
    from open_webui.integrations.supabase_integration import SupabaseClient
    
    url = os.getenv("SUPABASE_URL")
    print(f"   URL: {url}")
    
    client = SupabaseClient()
    print("   ✅ Supabase client initialized successfully!")
    
except Exception as e:
    print(f"   ❌ Supabase error: {e}")

# Test Stripe
print("\n💳 Testing Stripe Connection...")
try:
    from open_webui.integrations.stripe_integration import StripeClient
    
    client = StripeClient()
    print("   ✅ Stripe client initialized successfully!")
    
    # Test API call
    async def test_stripe():
        products = await client.list_products(limit=5)
        print(f"   ✅ Found {len(products)} products in Stripe")
        if products:
            for p in products[:3]:
                print(f"      - {p.get('name', 'Unnamed')}")
    
    asyncio.run(test_stripe())
    
except Exception as e:
    print(f"   ❌ Stripe error: {e}")

print("\n" + "=" * 60)
print("  ✅ Integration Test Complete!")
print("=" * 60)
print("\n📝 Next steps:")
print("   1. Start your server: python -m uvicorn main:app --reload --port 8080")
print("   2. Test health endpoint: http://localhost:8080/api/integrations/health")
print("   3. Check API docs: http://localhost:8080/docs")
