# Stripe Integration - Price Configuration Update

## ✅ Updated Pricing from Strip Folder

I've integrated the pricing structure from the `strip` folder into the new Stripe implementation:

### New Pricing Structure

#### Pro Plan
- **Monthly**: $20/month (was $29)
- **Yearly**: $200/year (was $290)
- **Savings**: 2 months free on yearly plan

**Features**:
- Unlimited messages
- 10x as many citations in answers
- Advanced AI (Gemini + Perplexity)
- Full chart access
- SEC filing analysis
- Unlimited file and photo uploads
- Extended access to image generation
- Technical indicators
- Priority support

#### Max Plan (renamed from Enterprise)
- **Monthly**: $200/month (was $99)
- **Yearly**: $2000/year (was $990)
- **Savings**: 2 months free on yearly plan

**Features**:
- Everything in Pro
- Early access to newest products
- Unlimited access to advanced AI models
- Enhanced access to video generation
- Custom AI training
- API access
- Dedicated support
- White-label option
- Team collaboration

### Changes Made

1. **Backend** (`routes/billing.py`):
   - ✅ Updated Pro pricing: $20/month, $200/year
   - ✅ Renamed Enterprise → Max
   - ✅ Updated Max pricing: $200/month, $2000/year
   - ✅ Updated feature lists to match strip folder

2. **Environment Variables** (`.env.example`):
   - ✅ Changed `STRIPE_PRICE_ID_ENTERPRISE_*` → `STRIPE_PRICE_ID_MAX_*`
   - ✅ Added pricing comments for clarity

3. **Stripe Keys Found**:
   - ⚠️ Found LIVE publishable key in strip folder: `pk_live_51PHqTQKGS1cHUXXS...`
   - This is the same key already in your backend `.env` file

### Next Steps

To complete the integration:

1. **Create Products in Stripe Dashboard**:
   - Pro Monthly: $20/month recurring
   - Pro Yearly: $200/year recurring
   - Max Monthly: $200/month recurring
   - Max Yearly: $2000/year recurring

2. **Add Price IDs to `.env`**:
   ```bash
   STRIPE_PRICE_ID_PRO_MONTHLY=price_xxxxx
   STRIPE_PRICE_ID_PRO_YEARLY=price_xxxxx
   STRIPE_PRICE_ID_MAX_MONTHLY=price_xxxxx
   STRIPE_PRICE_ID_MAX_YEARLY=price_xxxxx
   ```

3. **Test the Integration**:
   ```bash
   cd backend
   python test_stripe_integration.py
   ```

### Stripe Keys Available

From the strip folder, I found you already have:
- ✅ Publishable Key: `pk_live_51PHqTQKGS1cHUXXS...` (already in your env)
- ✅ Secret Key: Already configured in your backend

You just need to create the products/prices in Stripe Dashboard and add the price IDs!
