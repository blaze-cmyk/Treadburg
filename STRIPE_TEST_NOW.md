# 🚀 Test Stripe Integration NOW!

## Quick 3-Step Test (2 minutes)

### Step 1: Start the App
```bash
cd C:\Users\hariom\Downloads\tradebergs
.\start-all.bat
```

Wait for both servers to start:
- ✅ Backend: http://localhost:8080
- ✅ Frontend: http://localhost:3000

---

### Step 2: Test Checkout
1. Open: **http://localhost:3000/pricing**
2. Click **"Get Started"** on Pro plan ($20/month)
3. Enter test card details:
   - Card: `4242 4242 4242 4242`
   - Expiry: `12/25`
   - CVC: `123`
   - ZIP: `12345`
4. Click **"Subscribe"**

---

### Step 3: Verify Success
1. You should be redirected to success page
2. Check your Stripe Dashboard: https://dashboard.stripe.com/test/payments
3. Visit billing page: **http://localhost:3000/billing**
4. Your subscription should show as active!

---

## ✅ What to Expect

### Success Page:
- "Payment Successful!" message
- Subscription details
- Link to billing dashboard

### Billing Dashboard:
- Shows "Pro Plan - Monthly"
- Price: $20.00/month
- "Manage Subscription" button
- "Cancel Subscription" button

### Stripe Dashboard:
- New payment of $20.00
- Customer created
- Subscription active

---

## 🎯 Additional Tests (Optional)

### Test Yearly Plan:
1. Go to pricing page
2. Toggle to "Yearly"
3. Click "Get Started" on Pro ($200/year)
4. Complete checkout

### Test Max Plan:
1. Try Max plan ($200/month or $2000/year)
2. Verify higher tier features

### Test Customer Portal:
1. Go to billing dashboard
2. Click "Manage Subscription"
3. Opens Stripe Customer Portal
4. Try updating payment method
5. Try canceling subscription

---

## 🐛 If Something Goes Wrong

### Backend not starting:
```bash
cd backend
.\.runvenv\Scripts\activate
python -m uvicorn app:app --reload --port 8080
```

### Frontend not starting:
```bash
cd frontend
npm run dev
```

### Checkout button not working:
- Check browser console (F12)
- Verify backend is running
- Check `backend/env` has all Stripe keys

---

## 📊 Your Configuration

### Products Created:
- ✅ Pro Plan: $20/month, $200/year
- ✅ Max Plan: $200/month, $2000/year

### Price IDs (in backend/env):
```
STRIPE_PRICE_PRO_MONTHLY=price_1SbPZlKGS1cHUXXSny3UNx2R
STRIPE_PRICE_PRO_YEARLY=price_1SbPZmKGS1cHUXXSpT7PbfQV
STRIPE_PRICE_MAX_MONTHLY=price_1SbPZmKGS1cHUXXSFeSd5bTZ
STRIPE_PRICE_MAX_YEARLY=price_1SbPZnKGS1cHUXXS4S4ZLDbd
```

---

## 🎉 That's It!

Your Stripe integration is fully configured and ready to test. Just run the 3 steps above and you'll have a working payment system!

**Need help?** Check the logs in your terminal or browser console for error messages.
