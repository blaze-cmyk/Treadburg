# CRITICAL SECURITY FIX: User Data Isolation

## Problems Identified

### 1. **Users Can See Each Other's Chats** 🚨
- All users see the same chats regardless of who created them
- Chats from other users are visible in the sidebar

### 2. **Credits Not Deducting** 🚨
- Credits don't reduce when users send prompts
- No user-specific credit tracking

### 3. **Root Cause**
Backend uses **SERVICE_ROLE_KEY** for all Supabase queries, which:
- Bypasses Row Level Security (RLS)
- Returns ALL data from tables
- Doesn't respect user ownership

## Current Architecture (BROKEN)

```
Frontend → Backend (with user JWT) → Supabase (with SERVICE_ROLE_KEY)
                                              ↓
                                        Bypasses RLS
                                        Returns ALL chats
```

## Required Architecture (SECURE)

```
Frontend → Backend (with user JWT) → Supabase (with USER JWT)
                                              ↓
                                        Respects RLS
                                        Returns ONLY user's chats
```

## Implementation Plan

### Phase 1: User-Scoped Supabase Client
1. Modify `SupabaseClient` to accept user JWT token
2. Use user token in Authorization header (not service role)
3. RLS policies will automatically filter data

### Phase 2: Extract User from JWT
1. Add middleware to extract user ID from JWT
2. Pass user context to all route handlers
3. Use user-scoped client for all queries

### Phase 3: Credit Deduction
1. Get user's profile ID from JWT
2. Deduct credits from correct user's profile
3. Track credits per message

### Phase 4: Testing
1. Create 2 test users
2. Verify each user only sees their own chats
3. Verify credits deduct correctly per user

## Files to Modify

1. `backend/services/supabase_client.py` - Add user-scoped client
2. `backend/routes/chat.py` - Use user JWT for queries
3. `backend/middleware/auth.py` - Extract user from JWT
4. `backend/routes/auth.py` - Pass user context

## RLS Policies (Already Correct)

✅ `chats` table: Users can only view/create/update own chats
✅ `messages` table: Users can only view/create own messages  
✅ `profiles` table: Users can only view/update own profile

**The policies are correct, but backend bypasses them!**
