"""Test the purchase endpoint directly"""
import requests
import json

# Get a token first (you'll need to replace this with your actual token)
# You can get it from localStorage in browser console: localStorage.getItem('token')

token = input("Enter your auth token from browser (localStorage.getItem('token')): ").strip()

if not token:
    print("No token provided, exiting...")
    exit(1)

# Test the purchase endpoint
url = "http://localhost:8080/api/user-management/credits/purchase"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
data = {
    "amount": 15.00,
    "credits": 100,
    "success_url": "http://localhost:5173/credits/success",
    "cancel_url": "http://localhost:5173/credits"
}

print("\nSending request to:", url)
print("Data:", json.dumps(data, indent=2))

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.ok:
        result = response.json()
        print(f"\n✅ Success!")
        print(f"Checkout URL: {result.get('checkout_url')}")
    else:
        print(f"\n❌ Error: {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")
