import requests
import json

response = requests.get('http://127.0.0.1:8080/api/billing/pricing')
data = response.json()

print("=== PRICING API CHECK ===\n")
for sub in data['subscriptions']:
    if sub['id'] in ['pro', 'max']:
        print(f"{sub['name']} Plan ({sub['id']}):")
        print(f"  Monthly: ${sub['price_monthly']}")
        print(f"  Monthly Price ID: '{sub.get('stripe_price_id_monthly', 'MISSING')}'")
        print(f"  Yearly: ${sub['price_yearly']}")
        print(f"  Yearly Price ID: '{sub.get('stripe_price_id_yearly', 'MISSING')}'")
        print()
