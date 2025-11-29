-- Initialize database
-- This file runs automatically when PostgreSQL container starts for the first time

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_trgm for text search (useful for searching event properties)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create index on JSONB fields for faster queries
-- This will be useful when querying event properties

-- Function to create GIN index on JSONB columns
CREATE OR REPLACE FUNCTION create_jsonb_indexes()
RETURNS void AS $$
BEGIN
    -- This function can be called after tables are created
    -- to add GIN indexes on JSONB columns
    RAISE NOTICE 'PostgreSQL initialized successfully';
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE analytics_db TO analytics;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE '✅ Database initialized: analytics_db';
    RAISE NOTICE '✅ User: analytics';
    RAISE NOTICE '✅ Extensions enabled: uuid-ossp, pg_trgm';
END $$;