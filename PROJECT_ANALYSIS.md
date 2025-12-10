# TradeBerg Project Analysis

## Current Project Status

### Application Overview
**TradeBerg** is an AI-powered trading assistant application with the following structure:

### Technology Stack
- **Frontend**: Next.js 15.5.7 (React 19.1.0)
- **Authentication**: Supabase Auth + NextAuth
- **Database**: Supabase PostgreSQL
- **Backend**: Python (FastAPI) deployed on Railway
- **Deployment**: Render (Frontend), Railway (Backend)

### Current Issues Identified

#### 1. Port Configuration
- **Issue**: Your Next.js development server runs on port `10000` instead of the default `3000`
- **Impact**: This is causing confusion with OAuth redirects
- **Location**: The port is likely set in your system environment variables or Render configuration
- **Why it matters**: Supabase's "Site URL" was probably set to `localhost:10000` during development, which is why Google OAuth redirects to localhost

#### 2. Google OAuth Redirect Problem
- **Root Cause**: Supabase project's "Site URL" is configured as `localhost:10000`
- **Symptom**: When users click "Continue with Google", they're redirected to `localhost:10000` after authentication
- **Solution Required**: Update Supabase Site URL to `https://tradeberg-frontend.onrender.com`

### Application Flow

#### Home Page (`/`)
**File**: `src/app/page.tsx`
**Behavior**:
1. Automatically creates a new chat when accessed
2. Redirects to `/c/{chatId}` on success
3. Falls back to `/pricing` page on error
4. Shows loading state: "Creating your chat..."

#### Login Page (`/login`)
**File**: `src/app/(auth)/login/page.tsx`
**Features**:
- Email/Password login
- Google OAuth login
- Sign up functionality
- Password reset
- Animated trading prompts display
- Session checking (auto-redirects if already logged in)

**Current Implementation**:
- Uses Supabase Auth for authentication
- Implements cookie-based redirect tracking
- Has comprehensive error handling
- Uses our new auth-helpers for OAuth

#### Main Layout
**File**: `src/app/(main)/layout.tsx`
**Components**:
- Header component
- Sidepanel (sidebar navigation)
- Page transition provider
- Responsive layout with sidebar

### Environment Configuration

#### Production URLs
- **Frontend**: `https://tradeberg-frontend.onrender.com`
- **Backend**: `https://tradeberg-backend.railway.app/api`
- **Supabase**: `https://pcxscejarxztezfeucgs.supabase.co`

#### Key Environment Variables (from `env` file)
```
NEXTAUTH_URL=https://tradeberg-frontend.onrender.com
NEXT_PUBLIC_APP_URL=https://tradeberg-frontend.onrender.com
SUPABASE_URL=https://pcxscejarxztezfeucgs.supabase.co
NEXT_PUBLIC_API_URL=https://tradeberg-backend.railway.app/api
```

### Code Changes Made (Recent)

1. **Created Auth Helpers** (`src/lib/auth-helpers.ts`)
   - Centralized OAuth redirect URL handling
   - Google OAuth options configuration
   - Consistent URL resolution

2. **Created Constants** (`src/lib/constants.ts`)
   - Production URL constant
   - OAuth paths
   - Error messages
   - Cookie names

3. **Updated Login Page**
   - Integrated auth-helpers
   - Improved error handling
   - Better logging for debugging
   - Enhanced redirect handling

4. **Updated Auth Callback** (`src/app/auth/callback/route.ts`)
   - Uses production URL consistently
   - Improved session handling
   - Better error reporting

5. **Updated Middleware** (`src/middleware.ts`)
   - Cookie-based redirect tracking
   - Prevents query parameter pollution
   - Better session management

### Critical Action Required

**You MUST update your Supabase configuration:**

1. Go to [Supabase Dashboard](https://app.supabase.com/project/pcxscejarxztezfeucgs)
2. Navigate to **Authentication → URL Configuration**
3. Set **Site URL** to: `https://tradeberg-frontend.onrender.com`
4. Add **Redirect URLs**:
   - `https://tradeberg-frontend.onrender.com/auth/callback`
   - `https://tradeberg-frontend.onrender.com`
   - `http://localhost:10000/auth/callback` (for local development)
5. Save changes

**Also update Google Cloud Console:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Find your OAuth 2.0 Client ID
3. Add **Authorized redirect URIs**:
   - `https://tradeberg-frontend.onrender.com/auth/callback`
   - `https://pcxscejarxztezfeucgs.supabase.co/auth/v1/callback`
4. Save changes

### Deployment Steps

1. **Commit all changes**:
   ```bash
   git add .
   git commit -m "Fix Google OAuth and improve authentication flow"
   git push
   ```

2. **Deploy to Render**:
   - Your frontend will auto-deploy on push
   - Or manually trigger deployment from Render dashboard

3. **Test the authentication flow**:
   - Visit `https://tradeberg-frontend.onrender.com`
   - Try logging in with Google
   - Verify successful redirect

### Why Port 10000?

Your Next.js server is running on port 10000 because:
- It's likely configured in Render's environment settings
- Or it's set in a system environment variable
- This is fine for production, but caused the OAuth configuration issue

### Next Steps

1. ✅ Code changes are complete
2. ⏳ Update Supabase Site URL (CRITICAL)
3. ⏳ Update Google OAuth redirect URIs
4. ⏳ Deploy to Render
5. ⏳ Test Google OAuth login

Once you complete steps 2-5, your Google OAuth should work correctly!
