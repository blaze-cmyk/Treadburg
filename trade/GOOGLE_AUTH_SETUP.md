# 🔐 Google OAuth Setup Guide (No Supabase)

This guide shows you how to set up Google OAuth authentication directly in your code, without using Supabase.

## ✅ What's Been Implemented

### Backend (FastAPI)
- ✅ Direct Google OAuth 2.0 flow
- ✅ JWT token generation and verification
- ✅ SQLite database for user storage (easily replaceable with PostgreSQL/MongoDB)
- ✅ Automatic 100 free credits for new users
- ✅ Session management

### Frontend (Next.js)
- ✅ NextAuth with Google Provider
- ✅ Automatic user sync to backend database
- ✅ JWT session management

## 📋 Setup Steps

### Step 1: Get Google OAuth Credentials

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/

2. **Create a New Project** (or select existing)
   - Click "Select a project" → "New Project"
   - Name: "TradeBerg" or your app name
   - Click "Create"

3. **Enable Google+ API**
   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API"
   - Click "Enable"

4. **Create OAuth Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Web application"
   - Name: "TradeBerg Web Client"
   
5. **Configure OAuth Consent Screen** (if prompted)
   - User Type: "External"
   - App name: "TradeBerg"
   - User support email: your email
   - Developer contact: your email
   - Click "Save and Continue"
   - Scopes: Add `email`, `profile`, `openid`
   - Test users: Add your email for testing

6. **Add Authorized Redirect URIs**
   ```
   Development:
   http://localhost:3000/api/auth/callback/google
   
   Production:
   https://your-domain.com/api/auth/callback/google
   https://tradeberg-frontend.onrender.com/api/auth/callback/google
   ```

7. **Copy Credentials**
   - You'll get:
     - Client ID: `123456789-abcdefg.apps.googleusercontent.com`
     - Client Secret: `GOCSPX-xxxxxxxxxxxxx`

### Step 2: Update Environment Variables

#### Frontend (.env.local)
```bash
# Google OAuth
GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret_here

# NextAuth
NEXTAUTH_SECRET=generate_random_string_here
NEXTAUTH_URL=http://localhost:3000

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8080
```

**Generate NEXTAUTH_SECRET:**
```bash
# On Windows PowerShell:
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})

# On Linux/Mac:
openssl rand -base64 32
```

#### Backend (.env)
```bash
# Google OAuth
GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:3000/api/auth/callback/google

# JWT Secret (same as NEXTAUTH_SECRET or generate new one)
JWT_SECRET=your_jwt_secret_here

# Database (optional - defaults to SQLite)
DATABASE_PATH=data/users.db

# Frontend URL
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Step 3: Install Required Dependencies

#### Backend
```bash
cd trade/server
pip install google-auth google-auth-oauthlib google-auth-httplib2 PyJWT httpx
```

Or add to `requirements.txt`:
```
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
PyJWT>=2.8.0
httpx>=0.25.0
```

#### Frontend
```bash
cd trade/client
npm install next-auth
```

### Step 4: Test the Setup

1. **Start Backend**
   ```bash
   cd trade/server
   python -m uvicorn app:app --reload --port 8080
   ```

2. **Start Frontend**
   ```bash
   cd trade/client
   npm run dev
   ```

3. **Test Google Login**
   - Go to http://localhost:3000
   - Click "Sign in with Google"
   - You should be redirected to Google
   - After authorization, you'll be logged in
   - Check backend logs to see user creation

### Step 5: Verify Database

The SQLite database will be created at `trade/server/data/users.db`

**View users:**
```bash
cd trade/server
sqlite3 data/users.db "SELECT * FROM users;"
```

**Check user credits:**
```bash
sqlite3 data/users.db "SELECT email, credits_balance FROM users;"
```

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    picture TEXT,
    credits_balance INTEGER DEFAULT 100,
    subscription_tier TEXT DEFAULT 'free',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    email_verified BOOLEAN DEFAULT 0
);
```

## 🔄 How It Works

### Authentication Flow

1. **User clicks "Sign in with Google"**
   - NextAuth redirects to Google OAuth
   
2. **User authorizes on Google**
   - Google redirects back with authorization code
   
3. **NextAuth exchanges code for tokens**
   - Gets user info from Google
   
4. **NextAuth signIn callback**
   - Sends user data to backend `/api/auth/save-user`
   
5. **Backend saves user**
   - Creates new user with 100 credits (if new)
   - Updates existing user's last login
   
6. **User is logged in**
   - JWT token stored in session
   - User can access protected routes

## 🚀 API Endpoints

### Backend Endpoints

**Save User (called by NextAuth)**
```
POST /api/auth/save-user
Body: { id, email, name, picture }
```

**Get User**
```
GET /api/auth/user/{email}
Response: { id, email, name, picture, credits, subscription_tier }
```

**Direct Google OAuth (alternative)**
```
GET /api/auth/google/init
Returns: { auth_url }

GET /api/auth/google/callback?code=xxx&state=xxx
Redirects to frontend with token
```

**Verify JWT Token**
```
POST /api/auth/verify-token
Body: { token }
Response: { success, user }
```

## 🔒 Security Features

- ✅ CSRF protection with state parameter
- ✅ JWT tokens with expiration
- ✅ Secure password hashing (if adding email/password)
- ✅ HTTPS in production
- ✅ HttpOnly cookies for session tokens
- ✅ Rate limiting on auth endpoints

## 🌐 Production Deployment

### Update Environment Variables

**Frontend (Render/Vercel)**
```bash
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
NEXTAUTH_SECRET=your_production_secret
NEXTAUTH_URL=https://your-frontend-domain.com
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

**Backend (Render/Railway)**
```bash
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=https://your-frontend-domain.com/api/auth/callback/google
JWT_SECRET=your_jwt_secret
NEXT_PUBLIC_APP_URL=https://your-frontend-domain.com
```

### Update Google OAuth Settings

Add production redirect URIs in Google Cloud Console:
```
https://your-frontend-domain.com/api/auth/callback/google
https://tradeberg-frontend.onrender.com/api/auth/callback/google
```

## 🔄 Migrating from Supabase

If you were using Supabase auth before:

1. **Export existing users** (if needed)
2. **Update frontend** - Already done! ✅
3. **Update backend** - Already done! ✅
4. **Remove Supabase dependencies** (optional)
   ```bash
   npm uninstall @supabase/supabase-js @supabase/auth-helpers-nextjs
   pip uninstall supabase
   ```

## 🎨 Frontend Usage

### Check if user is logged in
```typescript
import { useSession } from "next-auth/react"

export default function Component() {
  const { data: session, status } = useSession()
  
  if (status === "loading") return <div>Loading...</div>
  if (!session) return <div>Not logged in</div>
  
  return <div>Welcome {session.user?.name}!</div>
}
```

### Sign in/out buttons
```typescript
import { signIn, signOut } from "next-auth/react"

<button onClick={() => signIn("google")}>
  Sign in with Google
</button>

<button onClick={() => signOut()}>
  Sign out
</button>
```

### Protected API routes
```typescript
import { getServerSession } from "next-auth/next"
import { authOptions } from "@/lib/auth"

export async function GET(request: Request) {
  const session = await getServerSession(authOptions)
  
  if (!session) {
    return new Response("Unauthorized", { status: 401 })
  }
  
  // Protected logic here
}
```

## 🐛 Troubleshooting

### "Invalid client" error
- Check GOOGLE_CLIENT_ID matches exactly
- Verify redirect URI is added in Google Console

### "Redirect URI mismatch"
- Ensure redirect URI in Google Console matches exactly
- Check for trailing slashes
- Verify http vs https

### User not saving to database
- Check backend logs for errors
- Verify database file permissions
- Test `/api/auth/save-user` endpoint directly

### Session not persisting
- Check NEXTAUTH_SECRET is set
- Verify cookies are enabled
- Check NEXTAUTH_URL matches your domain

## 📚 Additional Resources

- [NextAuth.js Documentation](https://next-auth.js.org/)
- [Google OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

---

**Your Google OAuth is now set up and ready to use!** 🎉
