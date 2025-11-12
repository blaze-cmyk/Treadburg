# 🚀 Quick Reference - Supabase & Stripe Integration

## ⚡ Fast Setup (5 minutes)

```bash
# 1. Install dependencies
cd backend
pip install -r requirements-integrations.txt

# 2. Configure credentials
cp .env.mcp.example .env.mcp
# Edit .env.mcp with your Supabase and Stripe credentials

# 3. Run setup
python setup_integrations.py

# 4. Run database migration in Supabase dashboard
# File: backend/supabase/migrations/001_initial_schema.sql
```

## 📋 Required Credentials

### Supabase (Get from: https://app.supabase.com/project/_/settings/api)
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key
```

### Stripe (Get from: https://dashboard.stripe.com/apikeys)
```env
STRIPE_SECRET_KEY=sk_test_your-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-key
```

## 🔌 API Endpoints

### Supabase
- `GET /api/integrations/supabase/profile` - Get user profile
- `POST /api/integrations/supabase/profile` - Update profile
- `POST /api/integrations/supabase/analysis` - Save analysis
- `GET /api/integrations/supabase/analyses` - Get analyses

### Stripe
- `POST /api/integrations/stripe/checkout` - Create checkout
- `GET /api/integrations/stripe/subscription` - Get subscription
- `POST /api/integrations/stripe/subscription/cancel` - Cancel subscription

## 💻 Code Examples

### Save Market Analysis
```python
from open_webui.integrations import get_supabase_client

supabase = get_supabase_client()
await supabase.save_market_analysis(
    user_id="user_123",
    symbol="BTCUSDT",
    analysis_data={"price": 43000, "trend": "bullish"}
)
```

### Create Subscription
```python
from open_webui.integrations import get_stripe_client

stripe = get_stripe_client()
result = await stripe.create_checkout_session(
    price_id="price_xxx",
    success_url="https://tradeberg.com/success",
    cancel_url="https://tradeberg.com/cancel"
)
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `backend/.env.mcp` | Your credentials (create from .env.mcp.example) |
| `backend/setup_integrations.py` | Setup & test script |
| `backend/supabase/migrations/001_initial_schema.sql` | Database schema |
| `SUPABASE_STRIPE_INTEGRATION_GUIDE.md` | Full documentation |

## ✅ Checklist

- [ ] Install dependencies (`pip install -r requirements-integrations.txt`)
- [ ] Create `.env.mcp` from example
- [ ] Add Supabase credentials
- [ ] Add Stripe credentials
- [ ] Run `setup_integrations.py`
- [ ] Run database migration in Supabase
- [ ] Add router to `main.py`
- [ ] Test API endpoints
- [ ] Set up Stripe webhooks

## 🆘 Troubleshooting

**Connection Failed?**
- Check credentials in `.env.mcp`
- Verify Supabase project is active
- Ensure Stripe API key is correct

**Tables Don't Exist?**
- Run the migration SQL in Supabase dashboard
- Check SQL Editor for errors

**Import Errors?**
- Install dependencies: `pip install supabase stripe`

## 📞 Support

- Full Guide: `SUPABASE_STRIPE_INTEGRATION_GUIDE.md`
- Summary: `INTEGRATION_SUMMARY.md`
- Setup Script: `python setup_integrations.py`

---

**Branch:** `feature/supabase-stripe-integration`  
**Status:** ✅ Ready to Use
