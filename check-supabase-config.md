# How to Check and Fix Supabase Site URL

## The Problem
Google OAuth redirects to `localhost:10000` because your Supabase project's **Site URL** is set to `localhost:10000`.

Email login works fine because it doesn't use the Site URL for redirects.

## Solution: Update Supabase Site URL

### Method 1: Using Supabase Dashboard (RECOMMENDED)

1. **Open this URL in your browser**:
   ```
   https://app.supabase.com/project/pcxscejarxztezfeucgs/settings/auth
   ```

2. **Scroll to "Site URL" section**

3. **Change the Site URL from**:
   ```
   http://localhost:10000
   ```
   **to**:
   ```
   https://tradeberg-frontend.onrender.com
   ```

4. **Scroll to "Redirect URLs" section**

5. **Add these URLs** (click "Add URL" for each):
   ```
   https://tradeberg-frontend.onrender.com/auth/callback
   https://tradeberg-frontend.onrender.com
   http://localhost:10000/auth/callback
   ```

6. **Click "Save"** at the bottom

7. **Wait 1-2 minutes** for changes to propagate

8. **Test Google OAuth** on your deployed site

### Method 2: Verify Current Settings

If you want to see what's currently configured, you can check:

1. Go to: https://app.supabase.com/project/pcxscejarxztezfeucgs/settings/auth
2. Look for these sections:
   - **Site URL**: Should be `https://tradeberg-frontend.onrender.com`
   - **Redirect URLs**: Should include your production callback URL

### What Each Setting Does

- **Site URL**: The default URL Supabase redirects to after OAuth authentication
- **Redirect URLs**: Allowed URLs that can be used in the `redirectTo` parameter

### Why Your Code Changes Weren't Enough

Even though we hardcoded the production URL in the code, Supabase Auth has its own configuration that takes precedence for OAuth flows. The Site URL setting in Supabase overrides what we specify in the code.

### After Making Changes

1. Clear your browser cache (or use incognito mode)
2. Go to: https://tradeberg-frontend.onrender.com/login
3. Click "Continue with Google"
4. You should now be redirected to your production site instead of localhost

### Troubleshooting

If it still doesn't work after updating:

1. **Check Google Cloud Console**:
   - Go to: https://console.cloud.google.com/apis/credentials
   - Find your OAuth 2.0 Client ID
   - Make sure these redirect URIs are added:
     - `https://tradeberg-frontend.onrender.com/auth/callback`
     - `https://pcxscejarxztezfeucgs.supabase.co/auth/v1/callback`

2. **Wait a few minutes**: Sometimes it takes time for DNS/config changes to propagate

3. **Clear browser cache**: Old OAuth tokens might be cached

4. **Try incognito mode**: This ensures no cached data interferes

### Screenshot Guide

When you open the Supabase Auth settings page, you should see:

```
┌─────────────────────────────────────────┐
│ Authentication Settings                  │
├─────────────────────────────────────────┤
│                                          │
│ Site URL                                 │
│ ┌─────────────────────────────────────┐ │
│ │ https://tradeberg-frontend.onrender │ │
│ │ .com                                 │ │
│ └─────────────────────────────────────┘ │
│                                          │
│ Redirect URLs                            │
│ ┌─────────────────────────────────────┐ │
│ │ + Add URL                            │ │
│ │                                      │ │
│ │ https://tradeberg-frontend.onrender │ │
│ │ .com/auth/callback                  │ │
│ │                                      │ │
│ │ https://tradeberg-frontend.onrender │ │
│ │ .com                                 │ │
│ │                                      │ │
│ │ http://localhost:10000/auth/callback│ │
│ └─────────────────────────────────────┘ │
│                                          │
│ [Save]                                   │
└─────────────────────────────────────────┘
```

This is the ONLY way to fix the Google OAuth redirect issue!
