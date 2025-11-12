# 🚀 How to Run Database Migration in Supabase

## The migration file exists but hasn't been executed yet!

### Step-by-Step Instructions:

#### 1. **Go to Supabase Dashboard**
```
https://app.supabase.com
```

#### 2. **Select Your Project**
- Click on your project: `pcxscejarxztezfeucgs`

#### 3. **Open SQL Editor**
- In left sidebar, click **"SQL Editor"**
- Or go to: https://app.supabase.com/project/pcxscejarxztezfeucgs/sql

#### 4. **Create New Query**
- Click **"New Query"** button

#### 5. **Copy the Migration SQL**
- Open file: `backend/supabase/migrations/002_user_management_system.sql`
- Copy ALL content (entire file)

#### 6. **Paste and Run**
- Paste the SQL into the query editor
- Click **"Run"** button (or press Ctrl+Enter)

#### 7. **Verify Tables Created**
- Go to **"Table Editor"** in left sidebar
- You should see these new tables:
  - ✅ users
  - ✅ credit_transactions
  - ✅ payments
  - ✅ subscriptions
  - ✅ api_usage_log
  - ✅ login_history
  - ✅ admin_activity_log
  - ✅ credit_packages

---

## Alternative: Run via Supabase CLI

If you have Supabase CLI installed:

```bash
cd backend
supabase db push
```

---

## What the Migration Creates:

### 8 Tables:
1. **users** - User profiles with credits
2. **credit_transactions** - All credit movements
3. **payments** - Stripe payment records
4. **subscriptions** - Subscription management
5. **api_usage_log** - API usage tracking
6. **login_history** - Login history
7. **admin_activity_log** - Admin actions
8. **credit_packages** - Credit pricing

### 3 Functions:
- `update_user_credits()` - Add/remove credits
- `check_user_credits()` - Check balance
- `get_user_stats()` - Get user statistics

### 3 Admin Views:
- `admin_user_overview` - User summary
- `admin_revenue_overview` - Revenue stats
- `admin_active_users` - Active users

### Security:
- Row Level Security (RLS) enabled
- User data isolation
- Admin policies

---

## After Running Migration:

### Create Your First Admin User:

1. Register a user via your app (or Supabase Auth)
2. Then run this SQL in Supabase:

```sql
UPDATE public.users
SET is_admin = TRUE
WHERE email = 'your-email@example.com';
```

---

## Troubleshooting:

### Error: "relation already exists"
- Tables already created, you're good!

### Error: "permission denied"
- Make sure you're using the service role key
- Check RLS policies

### Error: "syntax error"
- Make sure you copied the ENTIRE SQL file
- Check for any copy/paste issues

---

## Quick Check:

After running migration, verify with this query:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
  'users', 
  'credit_transactions', 
  'payments', 
  'subscriptions'
);
```

Should return 4 rows (or 8 if all tables created).

---

**Migration File Location:**
`backend/supabase/migrations/002_user_management_system.sql`

**File Size:** ~17KB (450+ lines of SQL)
