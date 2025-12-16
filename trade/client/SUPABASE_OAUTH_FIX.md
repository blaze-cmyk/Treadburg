# Fixing Google OAuth for Tradeberg

## Critical Issue: Supabase Site URL Configuration

The main issue causing the OAuth redirect to `localhost:10000` is that your Supabase project still has localhost configured as the Site URL.

## Step-by-Step Fix

### 1. Update Supabase Project Settings

1. Log in to [Supabase Dashboard](https://app.supabase.com/project/pcxscejarxztezfeucgs)
2. Navigate to **Authentication → URL Configuration**
3. Update the **Site URL** to:
   ```
   https://tradeberg-frontend.onrender.com
   ```
4. Add the following **Redirect URLs**:
   ```
   https://tradeberg-frontend.onrender.com/auth/callback
   https://tradeberg-frontend.onrender.com
   ```
5. Click **Save**

### 2. Update Google Cloud Console Settings

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services → Credentials**
3. Find your OAuth client ID used for this application
4. Edit the **Authorized redirect URIs** and add:
   ```
   https://tradeberg-frontend.onrender.com/auth/callback
   ```
5. Save changes

### 3. Code Changes Already Made

We've already made the following changes to the code to ensure it works:

1. Hardcoded production URL in Google OAuth flow
2. Updated the auth callback handler
3. Improved redirect handling
4. Created constants file for consistent URLs

### 4. Deploy Your Changes

1. Commit and push all code changes
2. Deploy the frontend to Render

### 5. Testing

After updating both Supabase settings and deploying code changes:
1. Go to your deployed app: https://tradeberg-frontend.onrender.com
2. Click "Continue with Google"
3. Complete the Google authentication process
4. You should be redirected back to your app

## Why This Fix Works

The issue happens because:
1. Supabase uses the **Site URL** in its configuration to determine the allowed redirect destinations
2. If the Site URL is set to localhost, OAuth providers will be configured to redirect back to localhost
3. In production, this causes the redirect to fail

By updating both the Supabase configuration and hardcoding the production URL in the code, we ensure consistent behavior regardless of environment.
