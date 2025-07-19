-- =============================================================================
-- TimescaleDB Business Data Examples
-- This file contains example tables and sample data for common time-series scenarios
-- Should be executed after the main timescaledb.sql script
-- =============================================================================

-- This is a common pattern for IoT or SCADA systems
CREATE TABLE IF NOT EXISTS sensor_readings (
    id BIGSERIAL,
    sensor_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    value DOUBLE PRECISION NOT NULL,
    unit TEXT,
    location TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Convert to hypertable
SELECT create_hypertable_if_not_exists('sensor_readings', 'timestamp', interval '1 hour');

-- Add compression policy (compress data older than 7 days)
SELECT add_compression_policy('sensor_readings', interval '7 days');

-- Add retention policy (drop data older than 1 year)
SELECT add_retention_policy('sensor_readings', interval '1 year');

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_sensor_readings_sensor_id ON sensor_readings (sensor_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_location ON sensor_readings (location, timestamp DESC);

-- Example 2: Production Metrics Table
-- For manufacturing or production line data
CREATE TABLE IF NOT EXISTS production_metrics (
    id BIGSERIAL,
    machine_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    temperature DOUBLE PRECISION,
    pressure DOUBLE PRECISION,
    speed DOUBLE PRECISION,
    status TEXT,
    operator_id TEXT,
    batch_id TEXT
);

-- Convert to hypertable with 6-hour chunks for production data
SELECT create_hypertable_if_not_exists('production_metrics', 'timestamp', interval '6 hours');

-- Add compression policy (compress data older than 3 days)
SELECT add_compression_policy('production_metrics', interval '3 days');

-- Add retention policy (drop data older than 6 months)
SELECT add_retention_policy('production_metrics', interval '6 months');

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_production_metrics_machine_id ON production_metrics (machine_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_production_metrics_batch_id ON production_metrics (batch_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_production_metrics_status ON production_metrics (status, timestamp DESC);

-- Example 3: System Logs Table
-- For application or system logs
CREATE TABLE IF NOT EXISTS system_logs (
    id BIGSERIAL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    level TEXT NOT NULL,
    service TEXT NOT NULL,
    message TEXT NOT NULL,
    user_id TEXT,
    session_id TEXT,
    ip_address INET,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Convert to hypertable with 1-day chunks for logs
SELECT create_hypertable_if_not_exists('system_logs', 'timestamp', interval '1 day');

-- Add compression policy (compress data older than 1 day)
SELECT add_compression_policy('system_logs', interval '1 day');

-- Add retention policy (drop data older than 3 months)
SELECT add_retention_policy('system_logs', interval '3 months');

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs (level, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_system_logs_service ON system_logs (service, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_system_logs_user_id ON system_logs (user_id, timestamp DESC);

-- Example 4: Financial Data Table
-- For time-series financial data
CREATE TABLE IF NOT EXISTS financial_data (
    id BIGSERIAL,
    symbol TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    open_price DOUBLE PRECISION,
    high_price DOUBLE PRECISION,
    low_price DOUBLE PRECISION,
    close_price DOUBLE PRECISION,
    volume BIGINT,
    market_cap DOUBLE PRECISION
);

-- Convert to hypertable with 1-day chunks for financial data
SELECT create_hypertable_if_not_exists('financial_data', 'timestamp', interval '1 day');

-- Add compression policy (compress data older than 30 days)
SELECT add_compression_policy('financial_data', interval '30 days');

-- Add retention policy (drop data older than 5 years)
SELECT add_retention_policy('financial_data', interval '5 years');

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_financial_data_symbol ON financial_data (symbol, timestamp DESC);

-- =============================================================================
-- PART 2: Grant Permissions on Example Tables
-- =============================================================================

-- Grant permissions on example tables
GRANT ALL PRIVILEGES ON TABLE sensor_readings TO anon;
GRANT ALL PRIVILEGES ON TABLE sensor_readings TO authenticated;
GRANT ALL PRIVILEGES ON TABLE sensor_readings TO service_role;

GRANT ALL PRIVILEGES ON TABLE production_metrics TO anon;
GRANT ALL PRIVILEGES ON TABLE production_metrics TO authenticated;
GRANT ALL PRIVILEGES ON TABLE production_metrics TO service_role;

GRANT ALL PRIVILEGES ON TABLE system_logs TO anon;
GRANT ALL PRIVILEGES ON TABLE system_logs TO authenticated;
GRANT ALL PRIVILEGES ON TABLE system_logs TO service_role;

GRANT ALL PRIVILEGES ON TABLE financial_data TO anon;
GRANT ALL PRIVILEGES ON TABLE financial_data TO authenticated;
GRANT ALL PRIVILEGES ON TABLE financial_data TO service_role;

-- =============================================================================
-- PART 3: Sample Data Generation Functions
-- =============================================================================

-- Create a function to insert sample data for testing
CREATE OR REPLACE FUNCTION insert_sample_sensor_data(
    sensor_count integer DEFAULT 5,
    hours_back integer DEFAULT 24
)
RETURNS void AS $$
DECLARE
    i integer;
    j integer;
    current_time timestamptz;
    sensor_id text;
    value double precision;
BEGIN
    FOR i IN 1..sensor_count LOOP
        sensor_id := 'sensor_' || i;
        
        FOR j IN 0..hours_back LOOP
            current_time := NOW() - (j || ' hours')::interval;
            value := 20 + (random() * 30) + sin(j * 0.5) * 5; -- Simulate realistic sensor data
            
            INSERT INTO sensor_readings (sensor_id, timestamp, value, unit, location)
            VALUES (sensor_id, current_time, value, 'celsius', 'location_' || (i % 3 + 1));
        END LOOP;
    END LOOP;
    
    RAISE NOTICE 'Inserted sample data for % sensors over % hours', sensor_count, hours_back;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a function to insert sample production data
CREATE OR REPLACE FUNCTION insert_sample_production_data(
    machine_count integer DEFAULT 3,
    hours_back integer DEFAULT 48
)
RETURNS void AS $$
DECLARE
    i integer;
    j integer;
    current_time timestamptz;
    machine_id text;
    temperature double precision;
    pressure double precision;
    speed double precision;
    status text;
BEGIN
    FOR i IN 1..machine_count LOOP
        machine_id := 'machine_' || i;
        
        FOR j IN 0..hours_back LOOP
            current_time := NOW() - (j || ' hours')::interval;
            temperature := 80 + (random() * 40) + cos(j * 0.3) * 10;
            pressure := 1.5 + (random() * 2.0) + sin(j * 0.2) * 0.5;
            speed := 100 + (random() * 50) + cos(j * 0.1) * 20;
            status := CASE WHEN random() > 0.1 THEN 'running' ELSE 'maintenance' END;
            
            INSERT INTO production_metrics (machine_id, timestamp, temperature, pressure, speed, status, operator_id, batch_id)
            VALUES (machine_id, current_time, temperature, pressure, speed, status, 'operator_' || (i % 2 + 1), 'batch_' || (j / 8 + 1));
        END LOOP;
    END LOOP;
    
    RAISE NOTICE 'Inserted sample production data for % machines over % hours', machine_count, hours_back;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a function to insert sample system logs
CREATE OR REPLACE FUNCTION insert_sample_system_logs(
    hours_back integer DEFAULT 24
)
RETURNS void AS $$
DECLARE
    j integer;
    current_time timestamptz;
    level text;
    service text;
    message text;
    user_id text;
BEGIN
    FOR j IN 0..hours_back LOOP
        current_time := NOW() - (j || ' hours')::interval;
        
        -- Generate realistic log entries
        level := CASE 
            WHEN random() > 0.8 THEN 'ERROR'
            WHEN random() > 0.6 THEN 'WARN'
            WHEN random() > 0.4 THEN 'INFO'
            ELSE 'DEBUG'
        END;
        
        service := CASE (j % 4)
            WHEN 0 THEN 'api'
            WHEN 1 THEN 'auth'
            WHEN 2 THEN 'database'
            ELSE 'frontend'
        END;
        
        message := CASE level
            WHEN 'ERROR' THEN 'Failed to process request: ' || (random() * 1000)::integer
            WHEN 'WARN' THEN 'High memory usage detected: ' || (80 + random() * 20)::integer || '%'
            WHEN 'INFO' THEN 'Request processed successfully: ' || (random() * 100)::integer || 'ms'
            ELSE 'Debug information: ' || (random() * 10000)::integer
        END;
        
        user_id := CASE WHEN random() > 0.3 THEN 'user_' || (random() * 10)::integer ELSE NULL END;
        
        INSERT INTO system_logs (timestamp, level, service, message, user_id, session_id, ip_address)
        VALUES (current_time, level, service, message, user_id, 'session_' || (random() * 1000)::integer, 
                inet '192.168.1.' || (random() * 255)::integer);
    END LOOP;
    
    RAISE NOTICE 'Inserted sample system logs over % hours', hours_back;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permissions on sample data functions
GRANT EXECUTE ON FUNCTION insert_sample_sensor_data(integer, integer) TO authenticated;
GRANT EXECUTE ON FUNCTION insert_sample_sensor_data(integer, integer) TO service_role;

GRANT EXECUTE ON FUNCTION insert_sample_production_data(integer, integer) TO authenticated;
GRANT EXECUTE ON FUNCTION insert_sample_production_data(integer, integer) TO service_role;

GRANT EXECUTE ON FUNCTION insert_sample_system_logs(integer) TO authenticated;
GRANT EXECUTE ON FUNCTION insert_sample_system_logs(integer) TO service_role;

-- =============================================================================
-- PART 4: Business Data Verification
-- =============================================================================

-- Log the examples creation
DO $$
DECLARE
    table_count integer;
    func_count integer;
BEGIN
    -- Check example tables
    SELECT COUNT(*) INTO table_count FROM information_schema.tables 
    WHERE table_name IN ('sensor_readings', 'production_metrics', 'system_logs', 'financial_data');
    
    -- Check sample data functions
    SELECT COUNT(*) INTO func_count FROM pg_proc WHERE proname IN (
        'insert_sample_sensor_data',
        'insert_sample_production_data',
        'insert_sample_system_logs'
    );
    
    RAISE NOTICE 'Business Data Setup Summary:';
    RAISE NOTICE '- Example tables created: %', table_count;
    RAISE NOTICE '- Sample data functions created: %', func_count;
    RAISE NOTICE 'TimescaleDB business data examples created successfully!';
END $$; 