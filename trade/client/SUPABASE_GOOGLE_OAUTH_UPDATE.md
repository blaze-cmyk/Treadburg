# Fixing Google OAuth for Production

This guide explains how to update your Google OAuth and Supabase settings to work properly in the production environment.

## 1. Update Google OAuth Settings

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Find your OAuth 2.0 Client ID used for this application
3. Edit the client configuration
4. Add the following Authorized Redirect URIs:
   ```
   https://tradeberg-frontend.onrender.com/auth/callback
   ```
5. Save the changes

## 2. Update Supabase Auth Settings

1. Go to [Supabase Dashboard](https://supabase.com/dashboard/project/pcxscejarxztezfeucgs)
2. Navigate to Authentication → Providers
3. Find Google in the list of providers
4. Ensure it's enabled and using the correct Client ID and Client Secret
5. Under "Redirect URLs", add:
   ```
   https://tradeberg-frontend.onrender.com/auth/callback
   ```
6. Save the changes

## 3. Update Supabase URL Configuration

1. Go to Authentication → URL Configuration
2. Set the Site URL to:
   ```
   https://tradeberg-frontend.onrender.com
   ```
3. Add the following Redirect URLs:
   ```
   https://tradeberg-frontend.onrender.com/auth/callback
   https://tradeberg-frontend.onrender.com
   ```
4. Save the changes

## 4. Verify Environment Variables on Render

Make sure your Render deployment has these environment variables:

```
NEXTAUTH_URL=https://tradeberg-frontend.onrender.com
NEXT_PUBLIC_APP_URL=https://tradeberg-frontend.onrender.com
```

## Why This Is Required

When a user clicks "Login with Google":

1. The app redirects to Google's authentication page
2. After the user authorizes, Google redirects back to your app
3. The redirect URL must be:
   - Pre-configured in both Google OAuth settings and Supabase
   - Match exactly with the URL your app is using for the callback

The issue you're experiencing happens because:
- The app is trying to redirect back to a localhost URL after Google authentication
- This works in development but fails in production
- By updating all these settings, we ensure consistent URL handling

After making these changes and redeploying, the Google OAuth flow should work correctly in production.
