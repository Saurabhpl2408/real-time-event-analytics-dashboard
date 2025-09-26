-- Event Analytics Platform Database Schema
-- This file will be automatically executed when PostgreSQL starts

-- Table for storing raw events
CREATE TABLE IF NOT EXISTS events (
    id BIGSERIAL PRIMARY KEY,
    event_id UUID UNIQUE NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    source VARCHAR(20) NOT NULL,
    user_id VARCHAR(100),
    session_id VARCHAR(100),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    properties JSONB DEFAULT '{}',
    context JSONB DEFAULT '{}',
    processed_at TIMESTAMPTZ,
    validation_status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_source ON events(source);
CREATE INDEX IF NOT EXISTS idx_events_properties ON events USING GIN(properties);
CREATE INDEX IF NOT EXISTS idx_events_validation_status ON events(validation_status);

-- Table for analytics metrics
CREATE TABLE IF NOT EXISTS analytics_metrics (
    id BIGSERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_type VARCHAR(20) NOT NULL, -- counter, gauge, histogram
    value DOUBLE PRECISION NOT NULL,
    dimensions JSONB DEFAULT '{}',
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    time_window VARCHAR(10), -- 1m, 5m, 1h, 1d
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for metrics queries
CREATE INDEX IF NOT EXISTS idx_metrics_name_time ON analytics_metrics(metric_name, timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON analytics_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_type ON analytics_metrics(metric_type);

-- Table for anomaly alerts
CREATE TABLE IF NOT EXISTS anomaly_alerts (
    id BIGSERIAL PRIMARY KEY,
    alert_id UUID UNIQUE NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    anomaly_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL, -- low, medium, high, critical
    current_value DOUBLE PRECISION NOT NULL,
    expected_value DOUBLE PRECISION NOT NULL,
    deviation_score DOUBLE PRECISION NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    context JSONB DEFAULT '{}',
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for alerts
CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON anomaly_alerts(timestamp);
CREATE INDEX IF NOT EXISTS idx_alerts_metric ON anomaly_alerts(metric_name);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON anomaly_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_resolved ON anomaly_alerts(resolved);

-- Table for user sessions (for analytics)
CREATE TABLE IF NOT EXISTS user_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    user_id VARCHAR(100),
    start_time TIMESTAMPTZ NOT NULL,
    last_activity TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    event_count INTEGER DEFAULT 0,
    pages_viewed TEXT[] DEFAULT '{}',
    total_duration_seconds INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for sessions
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON user_sessions(start_time);
CREATE INDEX IF NOT EXISTS idx_sessions_last_activity ON user_sessions(last_activity);

-- Create some useful views for analytics

-- Recent events view
CREATE OR REPLACE VIEW recent_events AS
SELECT 
    event_id,
    event_type,
    source,
    user_id,
    timestamp,
    properties,
    validation_status
FROM events 
WHERE timestamp >= NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;

-- Events per hour view
CREATE OR REPLACE VIEW events_per_hour AS
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    event_type,
    source,
    COUNT(*) as event_count
FROM events 
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY DATE_TRUNC('hour', timestamp), event_type, source
ORDER BY hour DESC;

-- Active users view
CREATE OR REPLACE VIEW active_users_today AS
SELECT 
    COUNT(DISTINCT user_id) as active_users,
    COUNT(DISTINCT session_id) as active_sessions,
    COUNT(*) as total_events
FROM events 
WHERE timestamp >= CURRENT_DATE 
AND user_id IS NOT NULL;

-- Grant permissions to analytics_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO analytics_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO analytics_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO analytics_user;

-- Insert some sample data for testing
INSERT INTO events (event_id, event_type, source, user_id, session_id, properties, context, validation_status)
VALUES 
    (gen_random_uuid(), 'page_view', 'web', 'user_001', 'session_001', 
     '{"page": "/home", "referrer": "google.com"}', 
     '{"campaign": "summer_sale"}', 'valid'),
    (gen_random_uuid(), 'login', 'mobile', 'user_002', 'session_002', 
     '{"method": "google"}', 
     '{"device": "iPhone"}', 'valid'),
    (gen_random_uuid(), 'purchase', 'web', 'user_001', 'session_001', 
     '{"amount": 99.99, "currency": "USD", "product_id": "prod_123"}', 
     '{"campaign": "summer_sale"}', 'valid')
ON CONFLICT (event_id) DO NOTHING;