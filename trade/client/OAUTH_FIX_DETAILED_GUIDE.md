# Complete Guide to Fixing Google OAuth Redirect Issues

## Understanding the Problem

When you click "Continue with Google", the application is currently redirecting to `localhost:10000` after Google authentication instead of the production URL. This happens because Supabase uses the "Site URL" configuration for redirects, and your Supabase project still has `localhost:10000` configured as the Site URL.

## Solution Approach

We've implemented several layers of fixes to ensure the Google OAuth flow works correctly:

1. **Hardcoded Production URL**: We're now explicitly using your production URL (`tradeberg-frontend.onrender.com`) in the OAuth flow
2. **Auth Helper Functions**: Created reusable functions to ensure consistent URL handling
3. **Improved Error Handling**: Better logging and error reporting for authentication issues
4. **Debugging Tools**: Added tools to help identify and troubleshoot OAuth issues

## Step 1: Required Supabase Configuration Changes

Before deploying the code, you **MUST** update your Supabase project settings:

1. Log in to [Supabase Dashboard](https://app.supabase.com/project/pcxscejarxztezfeucgs)
2. Navigate to **Authentication → URL Configuration**
3. Update the **Site URL** to: 
   ```
   https://tradeberg-frontend.onrender.com
   ```
4. Add these **Redirect URLs**:
   ```
   https://tradeberg-frontend.onrender.com/auth/callback
   https://tradeberg-frontend.onrender.com
   ```
5. Click **Save**

## Step 2: Google OAuth Provider Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Find your OAuth 2.0 Client ID for this project
3. Edit the OAuth client settings
4. Add these **Authorized redirect URIs**:
   ```
   https://tradeberg-frontend.onrender.com/auth/callback
   https://pcxscejarxztezfeucgs.supabase.co/auth/v1/callback
   ```
5. Save changes

## Step 3: Deploy Code Changes

1. Push all code changes to your repository:
   ```bash
   git add .
   git commit -m "Fix Google OAuth redirect issues"
   git push
   ```

2. Deploy to Render:
   - Go to your [Render Dashboard](https://dashboard.render.com/)
   - Select your frontend service
   - Click "Manual Deploy" > "Deploy latest commit"
   - Wait for deployment to complete

## Step 4: Testing the Fix

After deploying the changes and updating your Supabase configuration:

1. Go to your deployed application: `https://tradeberg-frontend.onrender.com`
2. Open your browser's developer console (F12)
3. Click "Continue with Google"
4. Watch the console for the OAuth flow logs
5. Complete the Google authentication

## Debugging Persistent Issues

If you still encounter issues:

1. Open your browser's developer console
2. Paste and run the following code before attempting login:
   ```javascript
   const debugScript = document.createElement('script');
   debugScript.src = '/lib/debug-oauth.js';
   document.body.appendChild(debugScript);
   ```
3. Try the login again and check the console for detailed logs
4. Note any error messages or redirect URLs

## How Our Code Changes Work

1. **Constants File**: Centralizes the production URL configuration
2. **Auth Helpers**: Provides consistent functions for getting redirect URLs
3. **Login Page Updates**: 
   - Uses helper functions for OAuth redirects
   - Improved error handling and logging
4. **Callback Route**: Always uses the production URL for OAuth callbacks

If you continue to experience issues after deploying these changes and updating your Supabase configuration, please check your browser console for any error messages and ensure all URLs are correctly configured in both Supabase and Google Cloud Console.
