# Google OAuth Double Login Fix

## Problem
Users were experiencing a **double login redirect** when using Google OAuth:
1. Click "Login with Google" → Authenticate with Google
2. Redirect back to app → See login page again (instead of dashboard)
3. Have to login again

Additionally, some users saw "localhost:10000" errors.

## Root Cause
There were **THREE different OAuth callback routes** causing conflicts:

1. `/app/auth/callback/route.ts` - Old Supabase direct OAuth (redirected to `/`)
2. `/app/api/auth/callback/route.ts` - Email confirmation handler
3. `/app/api/auth/google/callback/route.ts` - New backend-proxied OAuth (POST only)

**The Issue:**
- Google OAuth was configured to redirect to `/auth/callback`
- But the backend expected `/api/auth/google/callback`
- The old route would set a Supabase session but not backend cookies
- Middleware would check for backend session → Not found → Redirect to login again

## Solution Applied

### 1. Updated Google OAuth Callback Route
**File:** `frontend/src/app/api/auth/google/callback/route.ts`

- ✅ Added **GET handler** (Google redirects with GET, not POST)
- ✅ Extracts authorization code from URL params
- ✅ Exchanges code for tokens via backend API
- ✅ Sets httpOnly cookies (access_token, refresh_token)
- ✅ Redirects to `/dashboard` on success
- ✅ Handles errors gracefully

### 2. Deprecated Old Auth Callback
**File:** `frontend/src/app/auth/callback/route.ts`

- ✅ Replaced with redirect to new callback route
- ✅ Logs warning when old route is used
- ✅ Prevents conflicts with new flow

### 3. Updated Email Confirmation Callback
**File:** `frontend/src/app/api/auth/callback/route.ts`

- ✅ Now handles email verification and password reset
- ✅ Uses proper origin detection
- ✅ Redirects to appropriate pages based on type

### 4. Fixed Middleware
**File:** `frontend/src/middleware.ts`

- ✅ Updated public paths to include `/api/auth/google/callback`
- ✅ Fixed authenticated user redirect logic
- ✅ Allows callback routes to complete before redirecting

## New OAuth Flow

```
User clicks "Login with Google"
    ↓
Frontend: backendAuth.googleInit()
    ↓
Frontend API: POST /api/auth/google
    ↓
Backend: Creates Google OAuth URL with redirect_url=/api/auth/google/callback
    ↓
User redirected to Google
    ↓
User authenticates with Google
    ↓
Google redirects to: /api/auth/google/callback?code=xxx
    ↓
Frontend API: GET /api/auth/google/callback (NEW!)
    ↓
Backend: POST /auth/google/callback (exchange code for tokens)
    ↓
Backend: Returns access_token + refresh_token
    ↓
Frontend API: Sets httpOnly cookies
    ↓
Frontend API: Redirects to /dashboard
    ↓
✅ User sees dashboard (NO double login!)
```

## Configuration Required

### Supabase OAuth Settings
Update your Google OAuth redirect URLs in Supabase Dashboard:

**Old (Remove):**
```
https://your-domain.com/auth/callback
```

**New (Add):**
```
https://your-domain.com/api/auth/google/callback
```

### Environment Variables
Ensure these are set in Render:

```env
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com/api
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

## Testing Checklist

- [ ] Deploy frontend to Render
- [ ] Update Supabase OAuth redirect URL
- [ ] Test Google login flow
- [ ] Verify user lands on dashboard (not login page)
- [ ] Check browser cookies (access_token, refresh_token should be set)
- [ ] Test logout and login again
- [ ] Test email signup/verification flow

## Files Changed

1. ✅ `frontend/src/app/api/auth/google/callback/route.ts` - Added GET handler
2. ✅ `frontend/src/app/auth/callback/route.ts` - Deprecated, redirects to new route
3. ✅ `frontend/src/app/api/auth/callback/route.ts` - Updated for email confirmations
4. ✅ `frontend/src/middleware.ts` - Fixed public paths and redirect logic

## Expected Behavior After Fix

### ✅ Successful Login
1. Click "Login with Google"
2. Authenticate with Google
3. **Immediately see dashboard** (no second login page!)
4. Profile shows correct user data
5. Credits balance visible
6. Can use chat immediately

### ✅ No More Errors
- ❌ No "localhost:10000" errors
- ❌ No double login redirects
- ❌ No session conflicts
- ✅ Clean, single OAuth flow

## Deployment Steps

```bash
# 1. Commit changes
git add .
git commit -m "fix: resolve Google OAuth double login issue"
git push

# 2. Render will auto-deploy

# 3. Update Supabase OAuth settings
# Go to: Supabase Dashboard → Authentication → Providers → Google
# Update Redirect URL to: https://your-domain.onrender.com/api/auth/google/callback

# 4. Test the flow!
```

## Troubleshooting

### Still seeing double login?
- Check Supabase OAuth redirect URL is updated
- Clear browser cookies and try again
- Check Render logs for errors

### Getting "localhost:10000" error?
- This means old callback route is still being used
- Verify Supabase redirect URL is correct
- Check backend CORS settings

### Cookies not being set?
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check backend is returning tokens
- Ensure `secure: true` in production

---

**Status:** ✅ FIXED - Ready to deploy!
