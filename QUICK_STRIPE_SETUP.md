# 🚀 Quick Stripe Product Creation Guide

## Step 1: Create Products in Stripe Dashboard

I've opened your Stripe Dashboard. Follow these steps:

### Product 1: TradeBerg Pro

1. Click **"Add product"** button
2. Fill in:
   - **Name**: `TradeBerg Pro`
   - **Description**: `Advanced AI-powered trading analysis with unlimited messages and premium features`
   
3. **Add Monthly Price**:
   - Click "Add another price"
   - **Price**: `20.00` USD
   - **Billing period**: `Monthly`
   - **Recurring**: Yes
   - Click "Add price"
   - **📋 COPY THE PRICE ID** (starts with `price_`)

4. **Add Yearly Price**:
   - Click "Add another price"
   - **Price**: `200.00` USD
   - **Billing period**: `Yearly`
   - **Recurring**: Yes
   - Click "Add price"
   - **📋 COPY THE PRICE ID**

5. Click **"Save product"**

---

### Product 2: TradeBerg Max

1. Click **"Add product"** button
2. Fill in:
   - **Name**: `TradeBerg Max`
   - **Description**: `Ultimate trading platform with all features, early access, and priority support`
   
3. **Add Monthly Price**:
   - Click "Add another price"
   - **Price**: `200.00` USD
   - **Billing period**: `Monthly`
   - **Recurring**: Yes
   - Click "Add price"
   - **📋 COPY THE PRICE ID**

4. **Add Yearly Price**:
   - Click "Add another price"
   - **Price**: `2000.00` USD
   - **Billing period**: `Yearly`
   - **Recurring**: Yes
   - Click "Add price"
   - **📋 COPY THE PRICE ID**

5. Click **"Save product"**

---

## Step 2: Add Price IDs to Your Env File

Once you have all 4 price IDs, add them to `backend/env`:

```bash
# Add these lines to backend/env file:

# Stripe Price IDs
STRIPE_PRICE_ID_PRO_MONTHLY=price_xxxxxxxxxxxxx  # Replace with actual ID
STRIPE_PRICE_ID_PRO_YEARLY=price_xxxxxxxxxxxxx   # Replace with actual ID
STRIPE_PRICE_ID_MAX_MONTHLY=price_xxxxxxxxxxxxx  # Replace with actual ID
STRIPE_PRICE_ID_MAX_YEARLY=price_xxxxxxxxxxxxx   # Replace with actual ID

# Webhook Secret (optional for now, needed for production)
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

---

## Step 3: Test the Integration

After adding the price IDs, run these commands:

### A. Test Backend API
```bash
cd backend
python test_stripe_integration.py
```

### B. Start Servers and Test Manually
```bash
# Terminal 1: Backend
cd backend
.runvenv\Scripts\activate
python -m uvicorn app:app --reload --port 8080

# Terminal 2: Frontend
cd frontend
npm run dev

# Then open: http://localhost:3000/pricing
```

### C. Test Checkout Flow
1. Go to http://localhost:3000/pricing
2. Click "Subscribe Now" on Pro plan
3. Use test card: `4242 4242 4242 4242`
4. Complete checkout
5. Verify success page

---

## ⚠️ Important Notes

- **Test Mode**: Make sure you're in TEST mode in Stripe Dashboard (toggle in top right)
- **Test Cards**: Use `4242 4242 4242 4242` for testing
- **Restart Backend**: After adding env variables, restart the backend server

---

## 📋 Checklist

- [ ] Created TradeBerg Pro product
- [ ] Added Pro monthly price ($20)
- [ ] Added Pro yearly price ($200)
- [ ] Copied Pro price IDs
- [ ] Created TradeBerg Max product
- [ ] Added Max monthly price ($200)
- [ ] Added Max yearly price ($2000)
- [ ] Copied Max price IDs
- [ ] Added all 4 price IDs to backend/env
- [ ] Restarted backend server
- [ ] Tested API with test_stripe_integration.py
- [ ] Tested checkout flow manually
- [ ] Verified payment in Stripe Dashboard

---

## 🎯 Quick Copy Template

Copy this template and fill in your actual price IDs:

```bash
STRIPE_PRICE_ID_PRO_MONTHLY=price_
STRIPE_PRICE_ID_PRO_YEARLY=price_
STRIPE_PRICE_ID_MAX_MONTHLY=price_
STRIPE_PRICE_ID_MAX_YEARLY=price_
STRIPE_WEBHOOK_SECRET=whsec_
FRONTEND_URL=http://localhost:3000
```

---

Let me know once you've added the price IDs and I'll help you test!
