-- ============================================
-- USER MANAGEMENT SYSTEM - COMPLETE SCHEMA
-- ============================================
-- This migration creates a complete user management system with:
-- - User profiles with credits
-- - Authentication tracking
-- - Payment history
-- - Subscription management
-- - Admin monitoring

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- 1. USERS TABLE (Enhanced)
-- ============================================
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Authentication (Supabase Auth)
    auth_user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    email_confirmed BOOLEAN DEFAULT FALSE,
    phone TEXT,
    phone_confirmed BOOLEAN DEFAULT FALSE,
    
    -- Profile Information
    username TEXT UNIQUE,
    full_name TEXT,
    avatar_url TEXT,
    bio TEXT,
    
    -- Credits System
    credits INTEGER DEFAULT 0,
    total_credits_purchased INTEGER DEFAULT 0,
    total_credits_used INTEGER DEFAULT 0,
    
    -- Subscription
    subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'basic', 'pro', 'enterprise')),
    subscription_status TEXT DEFAULT 'inactive' CHECK (subscription_status IN ('active', 'inactive', 'cancelled', 'expired')),
    subscription_start_date TIMESTAMPTZ,
    subscription_end_date TIMESTAMPTZ,
    
    -- Stripe Integration
    stripe_customer_id TEXT UNIQUE,
    stripe_subscription_id TEXT,
    
    -- Metadata
    last_login_at TIMESTAMPTZ,
    login_count INTEGER DEFAULT 0,
    ip_address TEXT,
    user_agent TEXT,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for users
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_auth_user_id ON public.users(auth_user_id);
CREATE INDEX IF NOT EXISTS idx_users_stripe_customer_id ON public.users(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_users_subscription_status ON public.users(subscription_status);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON public.users(created_at DESC);

-- ============================================
-- 2. CREDIT TRANSACTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.credit_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Transaction Details
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('purchase', 'usage', 'refund', 'bonus', 'admin_adjustment')),
    amount INTEGER NOT NULL, -- Positive for credit, negative for debit
    balance_after INTEGER NOT NULL,
    
    -- Description
    description TEXT,
    metadata JSONB DEFAULT '{}',
    
    -- Related Records
    payment_id UUID,
    stripe_payment_intent_id TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id ON public.credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_created_at ON public.credit_transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_type ON public.credit_transactions(transaction_type);

-- ============================================
-- 3. PAYMENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Payment Details
    amount DECIMAL(10, 2) NOT NULL,
    currency TEXT DEFAULT 'USD',
    credits_purchased INTEGER NOT NULL,
    
    -- Stripe Details
    stripe_payment_intent_id TEXT UNIQUE,
    stripe_charge_id TEXT,
    stripe_customer_id TEXT,
    
    -- Status
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'succeeded', 'failed', 'refunded', 'cancelled')),
    
    -- Metadata
    payment_method TEXT, -- card, google_pay, apple_pay, etc.
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    paid_at TIMESTAMPTZ,
    refunded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_payments_user_id ON public.payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON public.payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON public.payments(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_payments_stripe_payment_intent ON public.payments(stripe_payment_intent_id);

-- ============================================
-- 4. SUBSCRIPTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Subscription Details
    plan_name TEXT NOT NULL,
    plan_price DECIMAL(10, 2) NOT NULL,
    billing_interval TEXT CHECK (billing_interval IN ('monthly', 'yearly')),
    
    -- Stripe Details
    stripe_subscription_id TEXT UNIQUE,
    stripe_price_id TEXT,
    stripe_product_id TEXT,
    
    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'past_due', 'unpaid', 'incomplete')),
    
    -- Dates
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    cancel_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON public.subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON public.subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_subscription_id ON public.subscriptions(stripe_subscription_id);

-- ============================================
-- 5. API USAGE LOG TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.api_usage_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- API Details
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    
    -- Credits
    credits_used INTEGER DEFAULT 1,
    
    -- Request Details
    request_data JSONB,
    response_status INTEGER,
    response_time_ms INTEGER,
    
    -- Metadata
    ip_address TEXT,
    user_agent TEXT,
    
    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_api_usage_log_user_id ON public.api_usage_log(user_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_log_created_at ON public.api_usage_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_usage_log_endpoint ON public.api_usage_log(endpoint);

-- ============================================
-- 6. LOGIN HISTORY TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.login_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Login Details
    login_method TEXT CHECK (login_method IN ('email', 'google', 'phone', 'magic_link')),
    success BOOLEAN DEFAULT TRUE,
    
    -- Device Info
    ip_address TEXT,
    user_agent TEXT,
    device_type TEXT,
    browser TEXT,
    os TEXT,
    
    -- Location (optional)
    country TEXT,
    city TEXT,
    
    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_login_history_user_id ON public.login_history(user_id);
CREATE INDEX IF NOT EXISTS idx_login_history_created_at ON public.login_history(created_at DESC);

-- ============================================
-- 7. ADMIN ACTIVITY LOG TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.admin_activity_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    admin_user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    
    -- Activity Details
    action TEXT NOT NULL,
    target_user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    description TEXT,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_admin_activity_log_admin_user_id ON public.admin_activity_log(admin_user_id);
CREATE INDEX IF NOT EXISTS idx_admin_activity_log_created_at ON public.admin_activity_log(created_at DESC);

-- ============================================
-- FUNCTIONS
-- ============================================

-- Function: Update user credits
CREATE OR REPLACE FUNCTION update_user_credits(
    p_user_id UUID,
    p_amount INTEGER,
    p_transaction_type TEXT,
    p_description TEXT DEFAULT NULL,
    p_payment_id UUID DEFAULT NULL
)
RETURNS JSONB AS $$
DECLARE
    v_new_balance INTEGER;
    v_transaction_id UUID;
BEGIN
    -- Update user credits
    UPDATE public.users
    SET 
        credits = credits + p_amount,
        total_credits_purchased = CASE 
            WHEN p_transaction_type = 'purchase' THEN total_credits_purchased + p_amount
            ELSE total_credits_purchased
        END,
        total_credits_used = CASE 
            WHEN p_transaction_type = 'usage' THEN total_credits_used + ABS(p_amount)
            ELSE total_credits_used
        END,
        updated_at = NOW()
    WHERE id = p_user_id
    RETURNING credits INTO v_new_balance;
    
    -- Create transaction record
    INSERT INTO public.credit_transactions (
        user_id, transaction_type, amount, balance_after, description, payment_id
    )
    VALUES (
        p_user_id, p_transaction_type, p_amount, v_new_balance, p_description, p_payment_id
    )
    RETURNING id INTO v_transaction_id;
    
    RETURN jsonb_build_object(
        'success', TRUE,
        'new_balance', v_new_balance,
        'transaction_id', v_transaction_id
    );
END;
$$ LANGUAGE plpgsql;

-- Function: Check if user has enough credits
CREATE OR REPLACE FUNCTION check_user_credits(p_user_id UUID, p_required_credits INTEGER)
RETURNS BOOLEAN AS $$
DECLARE
    v_current_credits INTEGER;
BEGIN
    SELECT credits INTO v_current_credits
    FROM public.users
    WHERE id = p_user_id;
    
    RETURN v_current_credits >= p_required_credits;
END;
$$ LANGUAGE plpgsql;

-- Function: Get user stats
CREATE OR REPLACE FUNCTION get_user_stats(p_user_id UUID)
RETURNS JSONB AS $$
DECLARE
    v_stats JSONB;
BEGIN
    SELECT jsonb_build_object(
        'total_credits_purchased', COALESCE(total_credits_purchased, 0),
        'total_credits_used', COALESCE(total_credits_used, 0),
        'current_credits', COALESCE(credits, 0),
        'total_payments', (SELECT COUNT(*) FROM public.payments WHERE user_id = p_user_id AND status = 'succeeded'),
        'total_spent', (SELECT COALESCE(SUM(amount), 0) FROM public.payments WHERE user_id = p_user_id AND status = 'succeeded'),
        'api_calls_count', (SELECT COUNT(*) FROM public.api_usage_log WHERE user_id = p_user_id),
        'login_count', COALESCE(login_count, 0),
        'last_login', last_login_at,
        'member_since', created_at
    ) INTO v_stats
    FROM public.users
    WHERE id = p_user_id;
    
    RETURN v_stats;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- TRIGGERS
-- ============================================

-- Trigger: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON public.payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON public.subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.credit_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_usage_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.login_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.admin_activity_log ENABLE ROW LEVEL SECURITY;

-- Users: Can read own data
CREATE POLICY "Users can view own profile" ON public.users
    FOR SELECT USING (auth.uid() = auth_user_id);

CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE USING (auth.uid() = auth_user_id);

-- Credit Transactions: Can read own transactions
CREATE POLICY "Users can view own transactions" ON public.credit_transactions
    FOR SELECT USING (user_id IN (SELECT id FROM public.users WHERE auth_user_id = auth.uid()));

-- Payments: Can read own payments
CREATE POLICY "Users can view own payments" ON public.payments
    FOR SELECT USING (user_id IN (SELECT id FROM public.users WHERE auth_user_id = auth.uid()));

-- Subscriptions: Can read own subscriptions
CREATE POLICY "Users can view own subscriptions" ON public.subscriptions
    FOR SELECT USING (user_id IN (SELECT id FROM public.users WHERE auth_user_id = auth.uid()));

-- API Usage Log: Can read own logs
CREATE POLICY "Users can view own API usage" ON public.api_usage_log
    FOR SELECT USING (user_id IN (SELECT id FROM public.users WHERE auth_user_id = auth.uid()));

-- Login History: Can read own history
CREATE POLICY "Users can view own login history" ON public.login_history
    FOR SELECT USING (user_id IN (SELECT id FROM public.users WHERE auth_user_id = auth.uid()));

-- Admin policies: Full access for admins
CREATE POLICY "Admins have full access to users" ON public.users
    FOR ALL USING (
        EXISTS (SELECT 1 FROM public.users WHERE auth_user_id = auth.uid() AND is_admin = TRUE)
    );

CREATE POLICY "Admins have full access to transactions" ON public.credit_transactions
    FOR ALL USING (
        EXISTS (SELECT 1 FROM public.users WHERE auth_user_id = auth.uid() AND is_admin = TRUE)
    );

CREATE POLICY "Admins have full access to payments" ON public.payments
    FOR ALL USING (
        EXISTS (SELECT 1 FROM public.users WHERE auth_user_id = auth.uid() AND is_admin = TRUE)
    );

-- ============================================
-- INITIAL DATA
-- ============================================

-- Create credit packages (for reference)
CREATE TABLE IF NOT EXISTS public.credit_packages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    credits INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    currency TEXT DEFAULT 'USD',
    stripe_price_id TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default credit package
INSERT INTO public.credit_packages (name, credits, price, stripe_price_id)
VALUES ('Starter Pack', 100, 15.00, NULL)
ON CONFLICT DO NOTHING;

-- ============================================
-- VIEWS FOR ADMIN PANEL
-- ============================================

-- View: User Overview
CREATE OR REPLACE VIEW admin_user_overview AS
SELECT 
    u.id,
    u.email,
    u.username,
    u.full_name,
    u.credits,
    u.subscription_tier,
    u.subscription_status,
    u.is_active,
    u.is_verified,
    u.created_at,
    u.last_login_at,
    u.login_count,
    COUNT(DISTINCT p.id) as total_payments,
    COALESCE(SUM(p.amount), 0) as total_spent,
    COUNT(DISTINCT a.id) as total_api_calls
FROM public.users u
LEFT JOIN public.payments p ON u.id = p.user_id AND p.status = 'succeeded'
LEFT JOIN public.api_usage_log a ON u.id = a.user_id
GROUP BY u.id;

-- View: Revenue Overview
CREATE OR REPLACE VIEW admin_revenue_overview AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_payments,
    SUM(amount) as total_revenue,
    SUM(credits_purchased) as total_credits_sold
FROM public.payments
WHERE status = 'succeeded'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- View: Active Users
CREATE OR REPLACE VIEW admin_active_users AS
SELECT 
    DATE(created_at) as date,
    COUNT(DISTINCT user_id) as active_users
FROM public.api_usage_log
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

COMMENT ON TABLE public.users IS 'User profiles with credits and subscription management';
COMMENT ON TABLE public.credit_transactions IS 'All credit transactions (purchases, usage, refunds)';
COMMENT ON TABLE public.payments IS 'Payment records from Stripe';
COMMENT ON TABLE public.subscriptions IS 'Active and past subscriptions';
COMMENT ON TABLE public.api_usage_log IS 'API usage tracking for billing';
COMMENT ON TABLE public.login_history IS 'User login history for security';
COMMENT ON TABLE public.admin_activity_log IS 'Admin actions audit log';
