"""Diagnose the purchase error"""
import os
from dotenv import load_dotenv
load_dotenv('.env.mcp')

print("=" * 60)
print("DIAGNOSING STRIPE PURCHASE ERROR")
print("=" * 60)

# Check 1: Stripe API Key
print("\n1. Checking Stripe API Key...")
stripe_key = os.getenv('STRIPE_SECRET_KEY')
if stripe_key:
    print(f"   ✅ Found: {stripe_key[:7]}...{stripe_key[-4:]}")
else:
    print("   ❌ Missing STRIPE_SECRET_KEY")

# Check 2: Supabase credentials
print("\n2. Checking Supabase credentials...")
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
if supabase_url and supabase_key:
    print(f"   ✅ URL: {supabase_url}")
    print(f"   ✅ Key: {supabase_key[:20]}...")
else:
    print("   ❌ Missing Supabase credentials")

# Check 3: Can we connect to Supabase?
print("\n3. Testing Supabase connection...")
try:
    from open_webui.integrations.supabase_integration import get_supabase_client
    supabase = get_supabase_client()
    print("   ✅ Supabase client created")
    
    # Check 4: Do tables exist?
    print("\n4. Checking if tables exist...")
    try:
        result = supabase.client.table('users').select('count').limit(1).execute()
        print("   ✅ 'users' table exists")
    except Exception as e:
        print(f"   ❌ 'users' table error: {e}")
        print("\n   ⚠️  YOU NEED TO RUN THE MIGRATION SQL IN SUPABASE!")
        print("   ⚠️  See: RUN_MIGRATION_GUIDE.md")
        
    try:
        result = supabase.client.table('payments').select('count').limit(1).execute()
        print("   ✅ 'payments' table exists")
    except Exception as e:
        print(f"   ❌ 'payments' table error: {e}")
        
except Exception as e:
    print(f"   ❌ Supabase connection failed: {e}")

# Check 5: Can we create Stripe client?
print("\n5. Testing Stripe client...")
try:
    from open_webui.integrations.stripe_integration import get_stripe_client
    stripe_client = get_stripe_client()
    print("   ✅ Stripe client created")
except Exception as e:
    print(f"   ❌ Stripe client error: {e}")

print("\n" + "=" * 60)
print("DIAGNOSIS COMPLETE")
print("=" * 60)
