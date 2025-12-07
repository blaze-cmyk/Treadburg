# 🚀 Stripe Quick Setup Guide

## Step 1: Create Products in Stripe Dashboard

### Option A: Use Stripe Dashboard (Manual - 5 minutes)

1. **Go to Stripe Dashboard:**
   - Open: https://dashboard.stripe.com/test/products
   - Make sure you're in **TEST MODE** (toggle in top right)

2. **Create Pro Plan:**
   - Click "Add product"
   - Name: `TradeBerg Pro`
   - Description: `Professional trading analysis with advanced features`
   - Pricing:
     - Monthly: $20.00 USD (Recurring)
     - Yearly: $200.00 USD (Recurring, save $40)
   - Click "Save product"
   - **Copy the Price IDs** (starts with `price_...`)

3. **Create Max Plan:**
   - Click "Add product"
   - Name: `TradeBerg Max`
   - Description: `Maximum features with priority support and early access`
   - Pricing:
     - Monthly: $200.00 USD (Recurring)
     - Yearly: $2000.00 USD (Recurring, save $400)
   - Click "Save product"
   - **Copy the Price IDs**

### Option B: Use Stripe CLI (Automated - 1 minute)

```bash
# Install Stripe CLI: https://stripe.com/docs/stripe-cli
stripe login

# Create Pro Plan
stripe products create --name="TradeBerg Pro" --description="Professional trading analysis"
stripe prices create --product=prod_XXX --unit-amount=2000 --currency=usd --recurring[interval]=month
stripe prices create --product=prod_XXX --unit-amount=20000 --currency=usd --recurring[interval]=year

# Create Max Plan
stripe products create --name="TradeBerg Max" --description="Maximum features with priority support"
stripe prices create --product=prod_XXX --unit-amount=20000 --currency=usd --recurring[interval]=month
stripe prices create --product=prod_XXX --unit-amount=200000 --currency=usd --recurring[interval]=year
```

---

## Step 2: Add Price IDs to Environment Variables

Open `backend/env` and add these lines:

```bash
# Stripe Price IDs (from Stripe Dashboard)
STRIPE_PRICE_PRO_MONTHLY=price_xxxxxxxxxxxxx
STRIPE_PRICE_PRO_YEARLY=price_xxxxxxxxxxxxx
STRIPE_PRICE_MAX_MONTHLY=price_xxxxxxxxxxxxx
STRIPE_PRICE_MAX_YEARLY=price_xxxxxxxxxxxxx

# Webhook Secret (for local testing)
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

**How to get Webhook Secret:**
1. Go to: https://dashboard.stripe.com/test/webhooks
2. Click "Add endpoint"
3. URL: `http://localhost:8080/api/billing/webhook`
4. Events: Select `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`
5. Copy the webhook secret (starts with `whsec_...`)

---

## Step 3: Test the Integration

### Quick Test (Automated):
```bash
cd backend
python test_stripe_integration.py
```

### Manual Test:
1. Start the application:
   ```bash
   cd C:\Users\hariom\Downloads\tradebergs
   .\start-all.bat
   ```

2. Open browser: http://localhost:3000/pricing

3. Click "Get Started" on Pro plan

4. Use Stripe test card:
   - Card: `4242 4242 4242 4242`
   - Expiry: Any future date
   - CVC: Any 3 digits
   - ZIP: Any 5 digits

5. Complete checkout

6. Verify:
   - Redirected to success page
   - Check Stripe Dashboard for payment
   - Check billing page: http://localhost:3000/billing

---

## Step 4: Set Up Webhook Testing (Optional)

For local webhook testing, use Stripe CLI:

```bash
# Forward webhooks to local server
stripe listen --forward-to localhost:8080/api/billing/webhook

# This will give you a webhook secret starting with whsec_
# Add it to your backend/env file
```

---

## 🎯 Quick Checklist

- [ ] Created Pro plan in Stripe ($20/month, $200/year)
- [ ] Created Max plan in Stripe ($200/month, $2000/year)
- [ ] Copied all 4 price IDs to `backend/env`
- [ ] Created webhook endpoint
- [ ] Added webhook secret to `backend/env`
- [ ] Tested checkout with test card
- [ ] Verified payment in Stripe Dashboard
- [ ] Checked billing page shows subscription

---

## 🔧 Troubleshooting

### "Invalid price ID" error:
- Make sure you're using TEST mode price IDs (start with `price_`)
- Verify price IDs are correctly copied to `backend/env`
- Restart backend after updating env file

### Webhook not working:
- Use Stripe CLI for local testing: `stripe listen --forward-to localhost:8080/api/billing/webhook`
- Check webhook secret is correct in `backend/env`
- Verify webhook endpoint is registered in Stripe Dashboard

### Checkout not opening:
- Check browser console for errors
- Verify Stripe publishable key in `backend/env`
- Make sure backend is running on port 8080

---

## 📚 Resources

- Stripe Dashboard: https://dashboard.stripe.com/test
- Stripe CLI: https://stripe.com/docs/stripe-cli
- Test Cards: https://stripe.com/docs/testing
- Webhook Testing: https://stripe.com/docs/webhooks/test

---

**Need Help?** Check the logs in your terminal or browser console for detailed error messages.
