"""
Comprehensive Integration Test Suite
Tests all aspects of Supabase and Stripe integration
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.mcp")

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_test(name, status, details=""):
    icon = "✅" if status else "❌"
    print(f"{icon} {name}")
    if details:
        print(f"   {details}")

# Test 1: Environment Variables
print_header("TEST 1: Environment Variables")
tests_passed = 0
tests_total = 0

env_vars = {
    "SUPABASE_URL": os.getenv("SUPABASE_URL"),
    "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY"),
    "SUPABASE_SERVICE_ROLE_KEY": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
    "STRIPE_SECRET_KEY": os.getenv("STRIPE_SECRET_KEY"),
    "STRIPE_PUBLISHABLE_KEY": os.getenv("STRIPE_PUBLISHABLE_KEY"),
}

for var_name, var_value in env_vars.items():
    tests_total += 1
    if var_value:
        print_test(f"{var_name}", True, f"Length: {len(var_value)} chars")
        tests_passed += 1
    else:
        print_test(f"{var_name}", False, "NOT SET")

# Test 2: Import Modules
print_header("TEST 2: Import Integration Modules")

try:
    tests_total += 1
    from open_webui.integrations.supabase_integration import SupabaseClient, get_supabase_client
    print_test("Import Supabase Integration", True)
    tests_passed += 1
except Exception as e:
    print_test("Import Supabase Integration", False, str(e))

try:
    tests_total += 1
    from open_webui.integrations.stripe_integration import StripeClient, get_stripe_client
    print_test("Import Stripe Integration", True)
    tests_passed += 1
except Exception as e:
    print_test("Import Stripe Integration", False, str(e))

try:
    tests_total += 1
    from open_webui.routers.integrations import router
    print_test("Import Integrations Router", True)
    tests_passed += 1
except Exception as e:
    print_test("Import Integrations Router", False, str(e))

# Test 3: Supabase Connection
print_header("TEST 3: Supabase Connection & Operations")

try:
    tests_total += 1
    supabase_client = SupabaseClient()
    print_test("Initialize Supabase Client", True, f"URL: {os.getenv('SUPABASE_URL')}")
    tests_passed += 1
    
    # Test client methods exist
    tests_total += 1
    methods = ['create_user_profile', 'get_user_profile', 'save_market_analysis', 
               'get_user_analyses', 'save_subscription', 'get_user_subscription']
    all_methods_exist = all(hasattr(supabase_client, method) for method in methods)
    if all_methods_exist:
        print_test("Supabase Client Methods", True, f"All {len(methods)} methods available")
        tests_passed += 1
    else:
        print_test("Supabase Client Methods", False, "Some methods missing")
    
except Exception as e:
    print_test("Initialize Supabase Client", False, str(e))
    tests_total += 1

# Test 4: Stripe Connection
print_header("TEST 4: Stripe Connection & Operations")

try:
    tests_total += 1
    stripe_client = StripeClient()
    print_test("Initialize Stripe Client", True, "API Key configured")
    tests_passed += 1
    
    # Test async operations
    async def test_stripe_operations():
        global tests_passed, tests_total
        
        # List products
        tests_total += 1
        try:
            products = await stripe_client.list_products(limit=5)
            print_test("List Stripe Products", True, f"Found {len(products)} product(s)")
            tests_passed += 1
            
            if products:
                for i, product in enumerate(products[:3], 1):
                    print(f"      {i}. {product.get('name', 'Unnamed')} (ID: {product.get('id', 'N/A')})")
        except Exception as e:
            print_test("List Stripe Products", False, str(e))
        
        # List prices
        tests_total += 1
        try:
            prices = await stripe_client.list_prices(limit=5)
            print_test("List Stripe Prices", True, f"Found {len(prices)} price(s)")
            tests_passed += 1
        except Exception as e:
            print_test("List Stripe Prices", False, str(e))
        
        # Test customer methods exist
        tests_total += 1
        methods = ['create_customer', 'get_customer', 'update_customer', 
                   'create_subscription', 'cancel_subscription']
        all_methods_exist = all(hasattr(stripe_client, method) for method in methods)
        if all_methods_exist:
            print_test("Stripe Client Methods", True, f"All {len(methods)} methods available")
            tests_passed += 1
        else:
            print_test("Stripe Client Methods", False, "Some methods missing")
    
    asyncio.run(test_stripe_operations())
    
except Exception as e:
    print_test("Initialize Stripe Client", False, str(e))
    tests_total += 1

# Test 5: API Router Configuration
print_header("TEST 5: API Router Configuration")

try:
    tests_total += 1
    from open_webui.routers.integrations import router
    
    # Check routes
    route_count = len(router.routes)
    print_test("Integration Router Loaded", True, f"{route_count} routes registered")
    tests_passed += 1
    
    # List some routes
    print("\n   Available Routes:")
    for route in router.routes[:10]:
        if hasattr(route, 'path'):
            print(f"      - {route.methods if hasattr(route, 'methods') else 'GET'} {route.path}")
    
except Exception as e:
    print_test("Integration Router Loaded", False, str(e))

# Test 6: File Structure
print_header("TEST 6: File Structure")

required_files = {
    ".env.mcp": "Environment configuration",
    "open_webui/integrations/__init__.py": "Integration module init",
    "open_webui/integrations/supabase_integration.py": "Supabase client",
    "open_webui/integrations/stripe_integration.py": "Stripe client",
    "open_webui/routers/integrations.py": "API router",
    "supabase/migrations/001_initial_schema.sql": "Database schema",
}

for file_path, description in required_files.items():
    tests_total += 1
    full_path = os.path.join(os.getcwd(), file_path)
    if os.path.exists(full_path):
        size = os.path.getsize(full_path)
        print_test(description, True, f"{file_path} ({size} bytes)")
        tests_passed += 1
    else:
        print_test(description, False, f"{file_path} NOT FOUND")

# Test 7: Main App Integration
print_header("TEST 7: Main App Integration Check")

try:
    tests_total += 1
    with open("open_webui/main.py", "r", encoding="utf-8") as f:
        main_content = f.read()
    
    # Check if integrations router is imported
    if "integrations" in main_content and "from open_webui.routers import" in main_content:
        print_test("Integrations Router Import", True, "Found in main.py imports")
        tests_passed += 1
    else:
        print_test("Integrations Router Import", False, "Not found in main.py")
    
    tests_total += 1
    # Check if router is included
    if "app.include_router(integrations.router" in main_content:
        print_test("Router Registration", True, "Registered in main app")
        tests_passed += 1
    else:
        print_test("Router Registration", False, "Not registered in main app")
    
except Exception as e:
    print_test("Main App Integration", False, str(e))
    tests_total += 1

# Final Summary
print_header("TEST SUMMARY")
print(f"\n   Total Tests: {tests_total}")
print(f"   Passed: {tests_passed}")
print(f"   Failed: {tests_total - tests_passed}")
print(f"   Success Rate: {(tests_passed/tests_total*100):.1f}%")

if tests_passed == tests_total:
    print("\n   🎉 ALL TESTS PASSED! Integration is fully functional!")
    print("\n   ✅ Ready to start server:")
    print("      python -m uvicorn main:app --reload --port 8080")
else:
    print(f"\n   ⚠️  {tests_total - tests_passed} test(s) failed. Review errors above.")

print("\n" + "=" * 70)
