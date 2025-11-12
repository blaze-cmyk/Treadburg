# Supabase & Stripe Integration Guide for TradeBerg

## 📋 Overview

This guide explains how to set up and use the Supabase and Stripe integrations in your TradeBerg project.

## 🌿 Branch Information

**Branch Name:** `feature/supabase-stripe-integration`

All integration files have been created in this new branch.

## 📁 Files Created

### Configuration Files
- `backend/mcp_servers_config.json` - MCP server configuration
- `backend/.env.mcp.example` - Environment variables template

### Integration Modules
- `backend/open_webui/integrations/__init__.py`
- `backend/open_webui/integrations/supabase_integration.py`
- `backend/open_webui/integrations/stripe_integration.py`

### API Router
- `backend/open_webui/routers/integrations.py`

### Database Migration
- `backend/supabase/migrations/001_initial_schema.sql`

## 🚀 Setup Instructions

### Step 1: Install Dependencies

```bash
cd backend
pip install supabase stripe
```

### Step 2: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.mcp.example .env.mcp
```

2. Fill in your credentials in `.env.mcp`:

**Supabase Credentials:**
- Get from: https://app.supabase.com/project/_/settings/api
- Required: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`

**Stripe Credentials:**
- Get from: https://dashboard.stripe.com/apikeys
- Required: `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`

### Step 3: Set Up Supabase Database

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Run the migration file: `backend/supabase/migrations/001_initial_schema.sql`

This creates:
- ✅ User profiles table
- ✅ Market analyses table
- ✅ Subscriptions table
- ✅ Chat messages table
- ✅ Trading signals table
- ✅ Payment history table
- ✅ API usage tracking table
- ✅ Row Level Security (RLS) policies
- ✅ Helper functions

### Step 4: Configure MCP Servers in TradeBerg

Add the MCP server configuration to your application:

```python
# In backend/open_webui/main.py

from open_webui.routers import integrations

# Add the integrations router
app.include_router(
    integrations.router,
    prefix="/api/integrations",
    tags=["integrations"]
)
```

### Step 5: Load Environment Variables

Add to your startup script or `.env` file:

```bash
# Load MCP environment variables
set -a
source .env.mcp
set +a
```

## 📊 Database Schema

### Tables Created

1. **user_profiles**
   - User information and preferences
   - Subscription tier tracking
   - Stripe customer ID linking

2. **market_analyses**
   - Saved market analysis results
   - Symbol and timeframe tracking
   - Confidence scores

3. **subscriptions**
   - Active subscription management
   - Stripe subscription linking
   - Billing period tracking

4. **chat_messages**
   - Chat history storage
   - Message data preservation

5. **trading_signals**
   - Entry/exit signals
   - Stop loss tracking
   - Signal status management

6. **payment_history**
   - Payment transaction records
   - Stripe payment ID linking

7. **api_usage**
   - API rate limiting
   - Usage tracking per endpoint

## 🔌 API Endpoints

### Supabase Endpoints

```
GET    /api/integrations/supabase/profile
POST   /api/integrations/supabase/profile
POST   /api/integrations/supabase/analysis
GET    /api/integrations/supabase/analyses
GET    /api/integrations/supabase/chat-history/{chat_id}
```

### Stripe Endpoints

```
POST   /api/integrations/stripe/customer
GET    /api/integrations/stripe/products
GET    /api/integrations/stripe/prices
POST   /api/integrations/stripe/checkout
GET    /api/integrations/stripe/subscription
POST   /api/integrations/stripe/subscription/cancel
POST   /api/integrations/stripe/webhook
```

### Health Check

```
GET    /api/integrations/health
```

## 💻 Usage Examples

### Python Backend

```python
from open_webui.integrations import SupabaseClient, StripeClient

# Initialize clients
supabase = SupabaseClient()
stripe_client = StripeClient()

# Save market analysis
await supabase.save_market_analysis(
    user_id="user_123",
    symbol="BTCUSDT",
    analysis_data={
        "price": 43000,
        "trend": "bullish",
        "confidence": 0.85
    }
)

# Create Stripe customer
result = await stripe_client.create_customer(
    email="user@example.com",
    name="John Doe"
)

# Create subscription
subscription = await stripe_client.create_subscription(
    customer_id=result["customer"]["id"],
    price_id="price_xxx"
)
```

### Frontend API Calls

```typescript
// Get user profile
const profile = await fetch('/api/integrations/supabase/profile', {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Create checkout session
const checkout = await fetch('/api/integrations/stripe/checkout', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    price_id: 'price_xxx',
    success_url: 'https://tradeberg.com/success',
    cancel_url: 'https://tradeberg.com/cancel'
  })
});
```

## 🔐 Security Features

### Row Level Security (RLS)
- All tables have RLS enabled
- Users can only access their own data
- Automatic user ID validation

### API Rate Limiting
- Built-in usage tracking
- Configurable limits per endpoint
- Automatic increment on each request

### Webhook Verification
- Stripe signature verification
- Secure event handling
- Automatic payload validation

## 🎯 Subscription Tiers

Configure these in your Stripe dashboard:

1. **Free Tier**
   - Basic market analysis
   - Limited API calls
   - No premium features

2. **Pro Tier**
   - Advanced analysis
   - Higher API limits
   - Real-time signals

3. **Enterprise Tier**
   - Unlimited API calls
   - Priority support
   - Custom integrations

## 🔄 Webhook Setup

1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://your-domain.com/api/integrations/stripe/webhook`
3. Select events to listen for:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
4. Copy webhook signing secret to `.env.mcp`

## 📝 MCP Server Configuration

The MCP servers are configured in `mcp_servers_config.json`:

```json
[
  {
    "type": "mcp",
    "info": {
      "id": "supabase-mcp-server",
      "name": "Supabase MCP Server"
    },
    "enabled": true
  },
  {
    "type": "mcp",
    "info": {
      "id": "stripe",
      "name": "Stripe MCP Server"
    },
    "enabled": true
  }
]
```

## 🧪 Testing

### Test Supabase Connection

```python
from open_webui.integrations import get_supabase_client

supabase = get_supabase_client()
profile = await supabase.get_user_profile("test_user_id")
print(profile)
```

### Test Stripe Connection

```python
from open_webui.integrations import get_stripe_client

stripe_client = get_stripe_client()
products = await stripe_client.list_products()
print(products)
```

### Health Check

```bash
curl http://localhost:8080/api/integrations/health
```

## 🐛 Troubleshooting

### Supabase Connection Issues
- Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` are correct
- Check if RLS policies are properly configured
- Ensure migrations have been run

### Stripe Connection Issues
- Verify `STRIPE_SECRET_KEY` is correct
- Check if you're using test/live keys appropriately
- Ensure webhook secret is configured for webhook endpoints

### MCP Server Not Loading
- Check `mcp_servers_config.json` syntax
- Verify environment variables are loaded
- Check application logs for errors

## 📚 Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Stripe Documentation](https://stripe.com/docs)
- [MCP Protocol Specification](https://modelcontextprotocol.io)

## 🎉 Next Steps

1. ✅ Merge this branch when ready
2. ✅ Set up production Supabase project
3. ✅ Configure production Stripe account
4. ✅ Set up webhook endpoints
5. ✅ Test payment flows
6. ✅ Deploy to production

## 📞 Support

For issues or questions:
- Check the logs in `backend/logs/`
- Review the integration code
- Test with the health check endpoint
- Verify environment variables are loaded

---

**Created:** November 12, 2025  
**Branch:** feature/supabase-stripe-integration  
**Status:** ✅ Ready for Testing
