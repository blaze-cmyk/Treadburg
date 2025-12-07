# Stripe Integration Testing Checklist

## ✅ Pre-Testing Setup

### 1. Install Dependencies
- [ ] Backend: `pip install stripe==11.3.0`
- [ ] Frontend: Already installed

### 2. Configure Stripe Keys
- [ ] Get test keys from https://dashboard.stripe.com/test/apikeys
- [ ] Add to `backend/.env`:
  ```
  STRIPE_SECRET_KEY=sk_test_...
  STRIPE_PUBLISHABLE_KEY=pk_test_...
  ```

### 3. Create Test Products (Optional)
- [ ] Go to Stripe Dashboard → Products
- [ ] Create "TradeBerg Pro" product
- [ ] Create monthly price ($29)
- [ ] Copy price ID to `.env` as `STRIPE_PRICE_ID_PRO_MONTHLY`

---

## 🧪 Test 1: Backend API Endpoints

### Run Test Script
```bash
cd backend
python test_stripe_integration.py
```

### Expected Results
- [x] ✅ Pricing endpoint returns subscription tiers
- [x] ✅ Checkout session creation works
- [x] ✅ Subscription status endpoint responds
- [x] ✅ Webhook endpoint exists

---

## 🧪 Test 2: Frontend Pricing Page

### Steps
1. [ ] Start backend: `cd backend && python -m uvicorn app:app --reload --port 8080`
2. [ ] Start frontend: `cd frontend && npm run dev`
3. [ ] Navigate to http://localhost:3000/pricing
4. [ ] Verify pricing cards display correctly
5. [ ] Toggle between Monthly/Yearly billing
6. [ ] Check all 3 tiers show (Free, Pro, Enterprise)
7. [ ] Verify credit packages display

### Expected Results
- [ ] ✅ Page loads without errors
- [ ] ✅ All pricing tiers visible
- [ ] ✅ Billing toggle works
- [ ] ✅ Subscribe buttons present

---

## 🧪 Test 3: Checkout Flow

### Steps
1. [ ] On pricing page, click "Subscribe Now" for Pro tier
2. [ ] Stripe Checkout should open
3. [ ] Use test card: `4242 4242 4242 4242`
4. [ ] Expiry: `12/34`, CVC: `123`, ZIP: `12345`
5. [ ] Complete checkout
6. [ ] Should redirect to success page
7. [ ] Check Stripe Dashboard for payment

### Expected Results
- [ ] ✅ Checkout opens in new window/tab
- [ ] ✅ Test card accepted
- [ ] ✅ Redirect to /billing/success
- [ ] ✅ Payment appears in Stripe Dashboard

---

## 🧪 Test 4: Webhook Handling

### Option A: Stripe CLI (Recommended)

#### Setup
```bash
# Install Stripe CLI
scoop install stripe  # Windows
# OR download from https://stripe.com/docs/stripe-cli

# Login
stripe login

# Forward webhooks
stripe listen --forward-to localhost:8080/api/billing/webhook
```

#### Test
```bash
# Trigger test events
stripe trigger checkout.session.completed
stripe trigger customer.subscription.created
stripe trigger invoice.paid
```

### Option B: Manual Testing
1. [ ] Complete a test checkout (Test 3)
2. [ ] Check backend console for webhook logs
3. [ ] Verify events are logged

### Expected Results
- [ ] ✅ Webhook endpoint receives events
- [ ] ✅ Events logged in console
- [ ] ✅ No signature verification errors

---

## 🧪 Test 5: Billing Dashboard

### Steps
1. [ ] Navigate to http://localhost:3000/billing
2. [ ] Verify current plan displays
3. [ ] Click "Manage Subscription"
4. [ ] Stripe Customer Portal should open
5. [ ] Test subscription cancellation
6. [ ] Verify cancellation in Stripe Dashboard

### Expected Results
- [ ] ✅ Dashboard loads correctly
- [ ] ✅ Subscription status shows
- [ ] ✅ Portal opens successfully
- [ ] ✅ Can cancel subscription

---

## 🧪 Test 6: Credit Purchase

### Steps
1. [ ] Go to pricing page
2. [ ] Scroll to credit packages
3. [ ] Click "Buy Now" on any package
4. [ ] Complete checkout with test card
5. [ ] Verify payment in Stripe Dashboard

### Expected Results
- [ ] ✅ Checkout opens for one-time payment
- [ ] ✅ Payment completes
- [ ] ✅ Redirect to success page

---

## 🐛 Common Issues & Solutions

### Issue: "Price ID not configured"
**Solution**: Add price IDs to `backend/.env`

### Issue: Checkout doesn't open
**Solution**: 
- Check browser console for errors
- Verify backend is running
- Check Stripe keys are valid

### Issue: Webhooks not working
**Solution**:
- Verify webhook secret in `.env`
- Use Stripe CLI for local testing
- Check webhook endpoint is accessible

### Issue: "Invalid signature" on webhook
**Solution**:
- Get webhook secret from Stripe CLI
- Add to `.env` as `STRIPE_WEBHOOK_SECRET`

---

## ✅ Final Verification

### All Tests Passed
- [ ] Backend API endpoints working
- [ ] Pricing page displays correctly
- [ ] Checkout flow completes
- [ ] Webhooks received and processed
- [ ] Billing dashboard functional
- [ ] Credit purchases work

### Ready for Production
- [ ] Switch to live Stripe keys
- [ ] Create products in live mode
- [ ] Update webhook endpoint URL
- [ ] Test in production environment

---

## 📊 Test Results

**Date**: ___________
**Tester**: ___________

**Backend Tests**: ☐ Pass ☐ Fail
**Frontend Tests**: ☐ Pass ☐ Fail
**Checkout Flow**: ☐ Pass ☐ Fail
**Webhooks**: ☐ Pass ☐ Fail
**Overall**: ☐ Pass ☐ Fail

**Notes**:
_______________________________________
_______________________________________
_______________________________________
