# Test Stripe Purchase Flow

## What Was Fixed

### 1. **Stripe Object Access Issues**
- ❌ Problem: Trying to access Stripe objects as dicts (`session['url']`)
- ✅ Solution: Access as attributes (`session.url`)

### 2. **User ID Mismatch**
- ❌ Problem: Using auth user ID instead of Supabase user ID
- ✅ Solution: Consistently use Supabase user ID from database

### 3. **Customer Creation**
- ❌ Problem: Accessing `customer_result['customer']['id']`
- ✅ Solution: Access as `customer_result['customer'].id`

## Changes Made

### Backend (`user_management.py`)
```python
# Fixed Stripe customer access
stripe_customer_id = customer_result['customer'].id  # Was: ['customer']['id']

# Fixed Stripe session access
checkout_url = session.url  # Was: session['url']
session_id = session.id     # Was: session['id']

# Fixed user ID consistency
supabase_user_id = user_response.data[0]['id']  # Use Supabase ID everywhere
```

### Added Logging
- Log when creating Stripe checkout
- Log payment record creation
- Log errors with detailed messages

## How to Test

### 1. Start Backend Server
```bash
cd backend
.\start_windows.bat
```

### 2. Start Frontend
```bash
npm run dev
```

### 3. Test Purchase Flow
1. Open browser: `http://localhost:5173`
2. Login to your account
3. Click on your profile → **Credits**
4. Click **"Buy Now"** on any package
5. Should redirect to Stripe checkout page

### 4. Expected Behavior

#### ✅ Success Flow:
1. Frontend calls `/api/user-management/credits/purchase`
2. Backend creates/gets user in Supabase
3. Backend creates/gets Stripe customer
4. Backend creates payment record
5. Backend creates Stripe checkout session
6. Backend returns `checkout_url`
7. Frontend redirects to Stripe
8. User completes payment
9. Stripe webhook updates payment status
10. Credits added to user account

#### ❌ If It Fails:
Check backend logs for:
```
Creating Stripe checkout for user <email>: $<amount> for <credits> credits
Created payment record <id> for user <email>
```

## Test with Stripe Test Cards

### Success Card
```
Card Number: 4242 4242 4242 4242
Expiry: Any future date
CVC: Any 3 digits
ZIP: Any 5 digits
```

### Decline Card
```
Card Number: 4000 0000 0000 0002
```

## API Response Format

### Success Response
```json
{
  "success": true,
  "checkout_url": "https://checkout.stripe.com/c/pay/...",
  "session_id": "cs_test_...",
  "payment_id": "uuid"
}
```

### Error Response
```json
{
  "detail": "Failed to create checkout session: <error message>"
}
```

## Debugging

### Check Backend Logs
```bash
# Look for these messages:
- "Creating Stripe checkout for user..."
- "Created payment record..."
- "Stripe checkout failed: ..."
```

### Check Browser Console
```javascript
// Should see:
- Calling purchaseCredits API
- Received checkout_url
- Redirecting to Stripe
```

### Check Database
```sql
-- Check if user was created
SELECT * FROM users WHERE email = 'your@email.com';

-- Check if payment record was created
SELECT * FROM payments WHERE user_id = 'uuid' ORDER BY created_at DESC;

-- Check Stripe customer ID
SELECT stripe_customer_id FROM users WHERE email = 'your@email.com';
```

## Common Issues

### Issue 1: "Failed to create checkout: Internal Server Error"
**Cause**: Stripe object access error
**Fix**: ✅ Already fixed - using `.url` and `.id` attributes

### Issue 2: "User not found in database"
**Cause**: User not auto-created
**Fix**: ✅ Already fixed - auto-creates user if missing

### Issue 3: "Invalid customer ID"
**Cause**: Customer creation failed
**Fix**: Check Stripe API key in `.env.mcp`

### Issue 4: Not redirecting to Stripe
**Cause**: `checkout_url` not returned correctly
**Fix**: ✅ Already fixed - accessing `session.url` correctly

## Verification Checklist

- [ ] Backend server running on port 8080
- [ ] Frontend running on port 5173
- [ ] Stripe API key configured in `.env.mcp`
- [ ] Supabase credentials configured
- [ ] User can login
- [ ] Credits page loads
- [ ] "Buy Now" button works
- [ ] Redirects to Stripe checkout
- [ ] Can complete test payment
- [ ] Credits added after payment

## Next Steps After Testing

1. **Add Success Page** - Create `/credits/success` route
2. **Add Cancel Page** - Handle cancelled payments
3. **Test Webhooks** - Verify payment confirmation
4. **Add Transaction History** - Show past purchases
5. **Add Email Notifications** - Confirm purchases

---

**Status**: 🟢 Ready to test
**Last Updated**: November 13, 2025
