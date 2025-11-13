-- FIX INFINITE RECURSION IN RLS POLICIES
-- Run this in Supabase SQL Editor

-- First, drop all existing policies that might be causing recursion
DROP POLICY IF EXISTS "users_select_policy" ON users;
DROP POLICY IF EXISTS "users_insert_policy" ON users;
DROP POLICY IF EXISTS "users_update_policy" ON users;
DROP POLICY IF EXISTS "payments_select_policy" ON payments;
DROP POLICY IF EXISTS "payments_insert_policy" ON payments;
DROP POLICY IF EXISTS "credit_transactions_select_policy" ON credit_transactions;
DROP POLICY IF EXISTS "credit_transactions_insert_policy" ON credit_transactions;

-- Disable RLS temporarily to allow service role access
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE payments DISABLE ROW LEVEL SECURITY;
ALTER TABLE credit_transactions DISABLE ROW LEVEL SECURITY;

-- Re-enable RLS with simple policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE credit_transactions ENABLE ROW LEVEL SECURITY;

-- Create simple, non-recursive policies
-- Users table: Allow service role full access
CREATE POLICY "users_service_role_all" ON users
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Payments table: Allow service role full access
CREATE POLICY "payments_service_role_all" ON payments
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Credit transactions table: Allow service role full access
CREATE POLICY "credit_transactions_service_role_all" ON credit_transactions
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Optional: Allow authenticated users to view their own data
CREATE POLICY "users_view_own" ON users
    FOR SELECT
    TO authenticated
    USING (auth_user_id = auth.uid());

CREATE POLICY "payments_view_own" ON payments
    FOR SELECT
    TO authenticated
    USING (user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid()));

CREATE POLICY "credit_transactions_view_own" ON credit_transactions
    FOR SELECT
    TO authenticated
    USING (user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid()));
