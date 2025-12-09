# Complete TradeBerg Website Setup Guide

This guide will walk you through the final steps to make your TradeBerg website fully functional with proper authentication, user profiles, and dashboard.

## 1. Supabase Configuration

### Update Site URL and Redirect URLs

1. Go to the [Supabase Dashboard](https://app.supabase.com/project/pcxscejarxztezfeucgs)
2. Navigate to **Authentication → URL Configuration**
3. Update the **Site URL** to:
   ```
   https://tradeberg-frontend.onrender.com
   ```
4. Add these **Redirect URLs** (one per line):
   ```
   https://tradeberg-frontend.onrender.com/auth/callback
   https://tradeberg-frontend.onrender.com
   http://localhost:10000/auth/callback
   ```
5. Click **Save**

## 2. Google OAuth Provider Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Find your OAuth 2.0 Client ID for this project
3. Edit the OAuth client settings
4. Add these **Authorized redirect URIs** (one per line):
   ```
   https://tradeberg-frontend.onrender.com/auth/callback
   https://pcxscejarxztezfeucgs.supabase.co/auth/v1/callback
   http://localhost:10000/auth/callback
   ```
5. Save changes

## 3. Deploy the Frontend

1. Push all code changes to your repository:
   ```bash
   git add .
   git commit -m "Implement complete user authentication and profile system"
   git push
   ```

2. Deploy to Render:
   - Go to your [Render Dashboard](https://dashboard.render.com/)
   - Select your frontend service
   - Click "Manual Deploy" > "Deploy latest commit"
   - Wait for deployment to complete

## 4. Testing the Complete System

After deploying:

1. Go to your production URL: `https://tradeberg-frontend.onrender.com`
2. Try to sign up or log in with Google OAuth
3. Check that you're redirected correctly after authentication
4. Verify your profile information is loaded and can be edited
5. Test the dashboard with the example charts

## 5. Database Schema Reference

Here's a summary of your existing `profiles` table structure:

```sql
CREATE TABLE public.profiles (
  id UUID PRIMARY KEY,
  auth_user_id UUID REFERENCES auth.users(id),
  email TEXT,
  full_name TEXT,
  bio TEXT,
  country TEXT,
  phone TEXT,
  avatar_url TEXT,
  timezone TEXT,
  language TEXT,
  preferred_assets TEXT[],
  risk_tolerance TEXT,
  trading_experience TEXT,
  subscription_tier TEXT,
  credits_balance INTEGER,
  total_credits_purchased INTEGER,
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE,
  last_login_at TIMESTAMP WITH TIME ZONE,
  is_active BOOLEAN,
  is_verified BOOLEAN
);
```

## 6. Next Development Steps

Once the authentication system works properly:

1. Connect your charts to real data APIs
2. Implement subscription management using Stripe
3. Add portfolio tracking functionality
4. Create user settings page
5. Implement trading capabilities

## Troubleshooting

If you encounter OAuth redirect issues:

1. Check your browser console for error messages
2. Verify that Supabase Site URL is correctly set
3. Clear your browser cookies and cache
4. Try the login flow again

For persistence issues with user profiles:

1. Check the Supabase logs for any database errors
2. Verify the RLS policies are configured correctly
3. Test the API calls using the Supabase dashboard

Remember to keep your environment variables properly configured in both development and production environments!
