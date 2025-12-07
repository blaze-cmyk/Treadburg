# Supabase Authentication Setup

## ✅ What Was Configured

### 1. **Supabase Client** (`frontend/src/lib/supabase.ts`)
- Created Supabase client for frontend
- Uses environment variables for URL and anon key
- Ready for authentication and database operations

### 2. **NextAuth Integration** (`frontend/src/lib/auth.ts`)
- ✅ Removed Prisma adapter
- ✅ Added Supabase integration
- ✅ Google OAuth configured
- ✅ Automatic user sync to Supabase `profiles` table on sign-in

### 3. **Environment Variables** (`frontend/.env.local`)
```env
NEXT_PUBLIC_SUPABASE_URL=https://pcxscejarxztezfeucgs.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
NEXTAUTH_SECRET=jAamxBTZfv5kQH9zFen8YX6Gbr3dh0Ji
NEXTAUTH_URL=http://localhost:3000
```

### 4. **Package Installed**
```bash
npm install @supabase/supabase-js
```

## 🔧 What You Need To Do

### 1. **Setup Google OAuth**

1. Go to: https://console.cloud.google.com/apis/credentials
2. Create a new OAuth 2.0 Client ID
3. Add authorized redirect URI:
   ```
   http://localhost:3000/api/auth/callback/google
   ```
4. Copy Client ID and Client Secret
5. Add to `frontend/.env.local`:
   ```env
   GOOGLE_CLIENT_ID=your_client_id_here
   GOOGLE_CLIENT_SECRET=your_client_secret_here
   ```

### 2. **Verify Supabase Profiles Table**

The `profiles` table should have these columns:
```sql
CREATE TABLE profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

If it doesn't exist, create it in Supabase SQL Editor.

## 🎯 How It Works

1. **User clicks "Continue with Google"** on `/login` page
2. **NextAuth handles OAuth flow** with Google
3. **On successful sign-in:**
   - User data saved to Supabase `profiles` table
   - JWT token created with user info
   - User redirected to home page
4. **Session persists** across page reloads
5. **User data accessible** via `useSession()` hook

## 📝 Usage in Components

```tsx
import { useSession } from "next-auth/react";

export default function MyComponent() {
  const { data: session, status } = useSession();
  
  if (status === "loading") return <p>Loading...</p>;
  if (!session) return <p>Not signed in</p>;
  
  return (
    <div>
      <p>Welcome, {session.user.name}!</p>
      <p>Email: {session.user.email}</p>
    </div>
  );
}
```

## 🔐 Protected Routes

To protect a page, add this at the top:

```tsx
import { useSession } from "next-auth/react";
import { redirect } from "next/navigation";

export default function ProtectedPage() {
  const { data: session, status } = useSession();
  
  if (status === "loading") return <p>Loading...</p>;
  if (!session) return redirect("/login");
  
  return <div>Protected content</div>;
}
```

## 🚀 Testing

1. **Restart frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

2. **Visit:** http://localhost:3000/login

3. **Click "Continue with Google"**

4. **Check Supabase:**
   - Go to Supabase Dashboard → Table Editor → profiles
   - You should see your user data

## ✅ Current Status

- ✅ Supabase client configured
- ✅ NextAuth integrated with Supabase
- ✅ Google OAuth ready (needs credentials)
- ✅ User sync to Supabase profiles table
- ✅ Session management working
- ⚠️ **Need Google OAuth credentials to test**

## 🔗 Related

- **Supabase Dashboard:** https://supabase.com/dashboard/project/pcxscejarxztezfeucgs
- **Google Cloud Console:** https://console.cloud.google.com/apis/credentials
- **NextAuth Docs:** https://next-auth.js.org/

## 📌 Next Steps

1. Get Google OAuth credentials
2. Add to `.env.local`
3. Restart frontend
4. Test login flow
5. Verify user appears in Supabase profiles table
