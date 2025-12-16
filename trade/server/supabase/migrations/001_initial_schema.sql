-- TradeBerg Initial Database Schema
-- This migration creates the core tables for the application

-- ==========================================
-- USER PROFILES
-- ==========================================

CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT UNIQUE NOT NULL,
    email TEXT,
    full_name TEXT,
    avatar_url TEXT,
    subscription_tier TEXT DEFAULT 'free',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster lookups
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_email ON user_profiles(email);

-- ==========================================
-- MARKET ANALYSES
-- ==========================================

CREATE TABLE IF NOT EXISTS market_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT,
    analysis_type TEXT,
    analysis_data JSONB NOT NULL,
    confidence_score DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for faster queries
CREATE INDEX idx_market_analyses_user_id ON market_analyses(user_id);
CREATE INDEX idx_market_analyses_symbol ON market_analyses(symbol);
CREATE INDEX idx_market_analyses_created_at ON market_analyses(created_at DESC);

-- ==========================================
-- SUBSCRIPTIONS
-- ==========================================

CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT UNIQUE NOT NULL,
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    plan_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'inactive',
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    subscription_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_stripe_customer_id ON subscriptions(stripe_customer_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);

-- ==========================================
-- CHAT MESSAGES
-- ==========================================

CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    chat_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    message_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_chat_messages_user_id ON chat_messages(user_id);
CREATE INDEX idx_chat_messages_chat_id ON chat_messages(chat_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at);

-- ==========================================
-- TRADING SIGNALS
-- ==========================================

CREATE TABLE IF NOT EXISTS trading_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    symbol TEXT NOT NULL,
    signal_type TEXT NOT NULL, -- 'entry', 'exit', 'stop'
    direction TEXT NOT NULL, -- 'long', 'short'
    price DECIMAL(20,8) NOT NULL,
    confidence DECIMAL(5,2),
    reasoning TEXT,
    signal_data JSONB DEFAULT '{}',
    status TEXT DEFAULT 'active', -- 'active', 'triggered', 'expired'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    triggered_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_trading_signals_user_id ON trading_signals(user_id);
CREATE INDEX idx_trading_signals_symbol ON trading_signals(symbol);
CREATE INDEX idx_trading_signals_status ON trading_signals(status);

-- ==========================================
-- PAYMENT HISTORY
-- ==========================================

CREATE TABLE IF NOT EXISTS payment_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    stripe_payment_id TEXT,
    amount DECIMAL(10,2) NOT NULL,
    currency TEXT DEFAULT 'usd',
    status TEXT NOT NULL,
    payment_method TEXT,
    payment_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_payment_history_user_id ON payment_history(user_id);
CREATE INDEX idx_payment_history_status ON payment_history(status);

-- ==========================================
-- API USAGE TRACKING
-- ==========================================

CREATE TABLE IF NOT EXISTS api_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    request_count INTEGER DEFAULT 1,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_api_usage_user_id ON api_usage(user_id);
CREATE INDEX idx_api_usage_date ON api_usage(date);

-- Unique constraint to prevent duplicate entries
CREATE UNIQUE INDEX idx_api_usage_unique ON api_usage(user_id, endpoint, date);

-- ==========================================
-- TRIGGERS FOR UPDATED_AT
-- ==========================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to tables with updated_at
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- ROW LEVEL SECURITY (RLS)
-- ==========================================

-- Enable RLS on all tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE trading_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;

-- Policies: Users can only access their own data
CREATE POLICY user_profiles_policy ON user_profiles
    FOR ALL USING (auth.uid()::text = user_id);

CREATE POLICY market_analyses_policy ON market_analyses
    FOR ALL USING (auth.uid()::text = user_id);

CREATE POLICY subscriptions_policy ON subscriptions
    FOR ALL USING (auth.uid()::text = user_id);

CREATE POLICY chat_messages_policy ON chat_messages
    FOR ALL USING (auth.uid()::text = user_id);

CREATE POLICY trading_signals_policy ON trading_signals
    FOR ALL USING (auth.uid()::text = user_id);

CREATE POLICY payment_history_policy ON payment_history
    FOR ALL USING (auth.uid()::text = user_id);

CREATE POLICY api_usage_policy ON api_usage
    FOR ALL USING (auth.uid()::text = user_id);

-- ==========================================
-- FUNCTIONS
-- ==========================================

-- Function to get user's current subscription tier
CREATE OR REPLACE FUNCTION get_user_subscription_tier(p_user_id TEXT)
RETURNS TEXT AS $$
DECLARE
    tier TEXT;
BEGIN
    SELECT subscription_tier INTO tier
    FROM user_profiles
    WHERE user_id = p_user_id;
    
    RETURN COALESCE(tier, 'free');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check API rate limit
CREATE OR REPLACE FUNCTION check_api_rate_limit(
    p_user_id TEXT,
    p_endpoint TEXT,
    p_limit INTEGER
)
RETURNS BOOLEAN AS $$
DECLARE
    current_count INTEGER;
BEGIN
    SELECT COALESCE(request_count, 0) INTO current_count
    FROM api_usage
    WHERE user_id = p_user_id
    AND endpoint = p_endpoint
    AND date = CURRENT_DATE;
    
    RETURN current_count < p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to increment API usage
CREATE OR REPLACE FUNCTION increment_api_usage(
    p_user_id TEXT,
    p_endpoint TEXT
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO api_usage (user_id, endpoint, date, request_count)
    VALUES (p_user_id, p_endpoint, CURRENT_DATE, 1)
    ON CONFLICT (user_id, endpoint, date)
    DO UPDATE SET request_count = api_usage.request_count + 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
