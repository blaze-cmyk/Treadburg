# 🚀 Stripe Integration - Final Testing & Deployment Guide

## ✅ Current Status

**Stripe Configuration Found**:
- ✅ STRIPE_SECRET_KEY: Configured (LIVE key)
- ✅ STRIPE_PUBLISHABLE_KEY: Configured (LIVE key)
- ⚠️ **IMPORTANT**: You're using LIVE keys - be careful with testing!

**Missing Configuration**:
- ❌ STRIPE_WEBHOOK_SECRET: Not set
- ❌ Price IDs: Not configured yet

---

## 📋 Step-by-Step Setup

### Step 1: Create Products in Stripe Dashboard

1. Go to https://dashboard.stripe.com/products
2. Click "Add product"

#### Product 1: TradeBerg Pro
- **Name**: TradeBerg Pro
- **Description**: Advanced AI-powered trading analysis
- **Pricing**:
  - Price 1: $20.00 USD / month (recurring)
  - Price 2: $200.00 USD / year (recurring)
- Click "Save product"
- **Copy the price IDs** (format: `price_xxxxx`)

#### Product 2: TradeBerg Max
- **Name**: TradeBerg Max
- **Description**: Ultimate trading platform with all features
- **Pricing**:
  - Price 1: $200.00 USD / month (recurring)
  - Price 2: $2000.00 USD / year (recurring)
- Click "Save product"
- **Copy the price IDs**

#### Product 3-5: Credit Packages (Optional)
- **100 Credits**: $9.99 USD (one-time)
- **500 Credits**: $39.99 USD (one-time)
- **1000 Credits**: $69.99 USD (one-time)

---

### Step 2: Add Price IDs to .env

Open `backend/env` and add these lines (replace with your actual price IDs):

```bash
# Stripe Price IDs
STRIPE_PRICE_ID_PRO_MONTHLY=price_xxxxxxxxxxxxx
STRIPE_PRICE_ID_PRO_YEARLY=price_xxxxxxxxxxxxx
STRIPE_PRICE_ID_MAX_MONTHLY=price_xxxxxxxxxxxxx
STRIPE_PRICE_ID_MAX_YEARLY=price_xxxxxxxxxxxxx

# Optional: Credit packages
STRIPE_PRICE_ID_CREDITS_100=price_xxxxxxxxxxxxx
STRIPE_PRICE_ID_CREDITS_500=price_xxxxxxxxxxxxx
STRIPE_PRICE_ID_CREDITS_1000=price_xxxxxxxxxxxxx

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

---

### Step 3: Set Up Webhook (Important!)

#### Option A: For Local Testing (Stripe CLI)

1. **Install Stripe CLI**:
   ```bash
   scoop install stripe
   # OR download from https://stripe.com/docs/stripe-cli
   ```

2. **Login**:
   ```bash
   stripe login
   ```

3. **Forward webhooks to local server**:
   ```bash
   stripe listen --forward-to localhost:8080/api/billing/webhook
   ```

4. **Copy the webhook signing secret** (starts with `whsec_`)

5. **Add to env file**:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
   ```

#### Option B: For Production

1. Go to https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. **Endpoint URL**: `https://yourdomain.com/api/billing/webhook`
4. **Events to listen for**:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.paid`
   - `invoice.payment_failed`
5. Click "Add endpoint"
6. **Copy the signing secret** and add to env

---

### Step 4: Test the Integration

#### A. Test Backend API

```bash
cd backend
python test_stripe_integration.py
```

**Expected Output**:
```
✅ Pricing endpoint working
✅ Checkout session created
✅ Subscription status endpoint working
✅ Webhook endpoint exists
```

#### B. Test Full Checkout Flow

1. **Start Backend**:
   ```bash
   cd backend
   .runvenv\Scripts\activate
   python -m uvicorn app:app --reload --port 8080
   ```

2. **Start Frontend** (new terminal):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test Checkout**:
   - Go to http://localhost:3000/pricing
   - Click "Subscribe Now" on Pro plan
   - **Use Stripe test card**: `4242 4242 4242 4242`
   - Expiry: `12/34`, CVC: `123`
   - Complete checkout
   - Verify redirect to success page

4. **Check Stripe Dashboard**:
   - Go to https://dashboard.stripe.com/payments
   - Verify payment appears

---

## ⚠️ IMPORTANT: Test Mode vs Live Mode

**You're currently using LIVE keys!**

For testing, you should:

1. **Switch to TEST keys**:
   ```bash
   # In backend/env, replace:
   STRIPE_SECRET_KEY=sk_test_...  # Not sk_live_
   STRIPE_PUBLISHABLE_KEY=pk_test_...  # Not pk_live_
   ```

2. **Get test keys from**:
   - https://dashboard.stripe.com/test/apikeys

3. **Create products in TEST mode**:
   - Switch to "Test mode" in Stripe Dashboard (toggle in top right)
   - Create products with same pricing
   - Get test price IDs

4. **Test with test cards**:
   - Success: `4242 4242 4242 4242`
   - Decline: `4000 0000 0000 0002`
   - More: https://stripe.com/docs/testing

5. **Switch to LIVE keys only when ready for production**

---

## 🧪 Testing Checklist

### Backend Tests
- [ ] Stripe package installed (`pip install stripe==11.3.0`)
- [ ] Price IDs added to env file
- [ ] Backend starts without errors
- [ ] `/api/billing/pricing` returns tiers
- [ ] `/api/billing/create-checkout-session` creates session

### Frontend Tests
- [ ] Pricing page loads at `/pricing`
- [ ] All 3 tiers display (Free, Pro, Max)
- [ ] Monthly/Yearly toggle works
- [ ] Subscribe buttons work
- [ ] Checkout opens in new tab

### Checkout Flow
- [ ] Stripe Checkout loads
- [ ] Test card accepted
- [ ] Redirect to success page
- [ ] Payment appears in Stripe Dashboard

### Webhooks
- [ ] Webhook secret configured
- [ ] Stripe CLI forwarding (for local)
- [ ] Webhook events logged in console
- [ ] No signature errors

### Billing Dashboard
- [ ] `/billing` page loads
- [ ] Subscription status shows
- [ ] "Manage Subscription" button works
- [ ] Customer portal opens

---

## 🎯 Quick Start Commands

```bash
# 1. Install Stripe package
cd backend
pip install stripe==11.3.0

# 2. Start backend
python -m uvicorn app:app --reload --port 8080

# 3. Start frontend (new terminal)
cd frontend
npm run dev

# 4. Start Stripe webhook forwarding (new terminal, optional)
stripe listen --forward-to localhost:8080/api/billing/webhook

# 5. Run tests (new terminal)
cd backend
python test_stripe_integration.py
```

---

## 📊 Configuration Summary

**Required**:
- ✅ STRIPE_SECRET_KEY
- ✅ STRIPE_PUBLISHABLE_KEY
- ⚠️ STRIPE_WEBHOOK_SECRET (add this!)
- ⚠️ Price IDs (add these!)

**Optional**:
- STRIPE_PRICE_ID_CREDITS_* (for credit packages)
- FRONTEND_URL (defaults to localhost:3000)

---

## 🐛 Troubleshooting

### "Price ID not configured"
- Make sure price IDs are in env file
- Restart backend after adding env variables

### Checkout doesn't open
- Check browser console for errors
- Verify backend is running on port 8080
- Check price IDs are correct

### Webhooks not working
- Verify webhook secret is correct
- Use Stripe CLI for local testing
- Check webhook logs in Stripe Dashboard

### "Invalid signature" error
- Webhook secret is wrong or missing
- Get new secret from Stripe CLI or Dashboard

---

## ✅ Ready for Production?

Before going live:

- [ ] Switch from TEST to LIVE keys
- [ ] Create products in LIVE mode
- [ ] Set up production webhook endpoint
- [ ] Test with real payment method
- [ ] Configure tax settings (if applicable)
- [ ] Set up email receipts
- [ ] Enable fraud prevention
- [ ] Test subscription cancellation
- [ ] Test failed payment handling

---

## 🎉 You're Almost There!

**Next Steps**:
1. Create products in Stripe Dashboard
2. Add price IDs to `backend/env`
3. Add webhook secret
4. Run `python test_stripe_integration.py`
5. Test checkout flow manually

Need help? Check the testing checklist above!
