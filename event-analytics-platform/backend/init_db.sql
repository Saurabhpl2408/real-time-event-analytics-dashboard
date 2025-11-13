-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Create events table will be done by SQLAlchemy
-- But we need to convert it to a hypertable after creation

-- This will be executed after tables are created
-- You'll need to run this manually or through migration
-- We'll handle this in the application startup

-- For now, just ensure database is created
SELECT 'Database initialized' as status;