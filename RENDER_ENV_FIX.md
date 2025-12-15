# 🔧 Fix Localhost Redirect Issue

## Problem
After Google login, you're being redirected to `localhost:10000` instead of your production URL.

## Root Cause
Your Render environment variables have the **wrong frontend URL**:
- Current: `https://tradeberg-frontend.onrender.com`
- Correct: `https://tradeberg-frontend-qwx0.onrender.com`

---

## ✅ CRITICAL FIX - Update Render Environment Variables

### Step 1: Go to Render Dashboard
1. Open: https://dashboard.render.com
2. Find and click: **tradeberg-frontend-qwx0** (your frontend service)

### Step 2: Update Environment Variables
1. Click the **"Environment"** tab on the left
2. Find and update these variables:

**Change from:**
```
NEXTAUTH_URL=https://tradeberg-frontend.onrender.com
NEXT_PUBLIC_APP_URL=https://tradeberg-frontend.onrender.com
```

**Change to:**
```
NEXTAUTH_URL=https://tradeberg-frontend-qwx0.onrender.com
NEXT_PUBLIC_APP_URL=https://tradeberg-frontend-qwx0.onrender.com
```

3. Click **"Save Changes"**
4. Render will automatically redeploy (takes ~2-3 minutes)

---

## ✅ Also Check Supabase Configuration

### Go to Supabase Dashboard
1. Open: https://supabase.com/dashboard/project/pcxscejarxztezfeucgs
2. Click **"Authentication"** → **"URL Configuration"**

### Verify These Settings:

**Site URL:**
```
https://tradeberg-frontend-qwx0.onrender.com
```

**Redirect URLs (should include):**
```
https://tradeberg-frontend-qwx0.onrender.com/**
https://tradeberg-frontend-qwx0.onrender.com/api/auth/google/callback
```

**Remove any localhost URLs from production** or keep them only for development.

---

## ✅ After Both Changes:

1. Wait 2-3 minutes for Render to redeploy
2. Go to: https://tradeberg-frontend-qwx0.onrender.com
3. Click "Continue with Google"
4. **Should now stay on production URL** ✅

---

## 🎯 Why This Happens

The URL mismatch causes:
- Google OAuth redirects to wrong URL
- Supabase redirects to wrong URL
- Frontend tries to connect to localhost

All three must match: **https://tradeberg-frontend-qwx0.onrender.com**

---

## 📝 Summary of URLs

| Service | Correct URL |
|---------|-------------|
| Frontend | https://tradeberg-frontend-qwx0.onrender.com |
| Backend | https://treadburg.onrender.com |
| Supabase | https://pcxscejarxztezfeucgs.supabase.co |

Make sure all environment variables use these exact URLs!
