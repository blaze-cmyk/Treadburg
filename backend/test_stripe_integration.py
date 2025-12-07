"""
Stripe Integration Test Script
Tests all billing endpoints and Stripe functionality
"""
import requests
import json

BASE_URL = "http://localhost:8080/api"

def test_pricing_endpoint():
    """Test GET /api/billing/pricing"""
    print("\n🧪 Testing Pricing Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/billing/pricing")
        data = response.json()
        
        if response.status_code == 200 and data.get("success"):
            print("✅ Pricing endpoint working")
            print(f"   - Subscription tiers: {len(data.get('subscriptions', []))}")
            print(f"   - Credit packages: {len(data.get('credits', []))}")
            return True
        else:
            print(f"❌ Pricing endpoint failed: {data}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_checkout_session():
    """Test POST /api/billing/create-checkout-session"""
    print("\n🧪 Testing Checkout Session Creation...")
    try:
        payload = {
            "price_id": "price_test_123",  # Replace with actual test price ID
            "mode": "subscription",
            "success_url": "http://localhost:3000/billing/success",
            "cancel_url": "http://localhost:3000/billing/cancel"
        }
        
        response = requests.post(
            f"{BASE_URL}/billing/create-checkout-session",
            json=payload
        )
        data = response.json()
        
        if response.status_code == 200 and data.get("success"):
            print("✅ Checkout session created")
            print(f"   - Session ID: {data.get('session_id', 'N/A')[:20]}...")
            print(f"   - Checkout URL: {data.get('url', 'N/A')[:50]}...")
            return True
        else:
            print(f"❌ Checkout session failed: {data}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_subscription_status():
    """Test GET /api/billing/subscription-status"""
    print("\n🧪 Testing Subscription Status...")
    try:
        response = requests.get(f"{BASE_URL}/billing/subscription-status")
        data = response.json()
        
        if response.status_code == 200 and data.get("success"):
            print("✅ Subscription status endpoint working")
            print(f"   - Tier: {data.get('tier', 'N/A')}")
            print(f"   - Subscription: {data.get('subscription', 'None')}")
            return True
        else:
            print(f"❌ Subscription status failed: {data}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_webhook_endpoint():
    """Test POST /api/billing/webhook (without signature)"""
    print("\n🧪 Testing Webhook Endpoint...")
    print("⚠️  Note: This will fail signature verification (expected)")
    try:
        payload = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_123",
                    "customer": "cus_test_123",
                    "subscription": "sub_test_123"
                }
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/billing/webhook",
            json=payload,
            headers={"stripe-signature": "test_signature"}
        )
        
        # We expect this to fail signature verification
        if response.status_code == 400:
            print("✅ Webhook endpoint exists (signature verification working)")
            return True
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_all_tests():
    """Run all Stripe integration tests"""
    print("=" * 60)
    print("🚀 Stripe Integration Test Suite")
    print("=" * 60)
    
    results = {
        "Pricing Endpoint": test_pricing_endpoint(),
        "Checkout Session": test_checkout_session(),
        "Subscription Status": test_subscription_status(),
        "Webhook Endpoint": test_webhook_endpoint()
    }
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Stripe integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    print("\n⚠️  Prerequisites:")
    print("   1. Backend server running on http://localhost:8080")
    print("   2. Stripe configured in .env file")
    print("   3. Test price IDs configured (optional for full testing)")
    print("\nStarting tests in 3 seconds...")
    
    import time
    time.sleep(3)
    
    success = run_all_tests()
    exit(0 if success else 1)
