-- =============================================================================
-- TimescaleDB Extension Setup for KMF SCADA System
-- This file contains all TimescaleDB initialization scripts
-- =============================================================================

-- =============================================================================
-- PART 1: Core TimescaleDB Extension Setup
-- =============================================================================

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Grant necessary permissions to Supabase roles
GRANT USAGE ON SCHEMA timescaledb TO anon;
GRANT USAGE ON SCHEMA timescaledb TO authenticated;
GRANT USAGE ON SCHEMA timescaledb TO service_role;

-- Create a dedicated schema for time-series data (optional but recommended)
CREATE SCHEMA IF NOT EXISTS timeseries;

-- Grant permissions on the timeseries schema
GRANT USAGE ON SCHEMA timeseries TO anon;
GRANT USAGE ON SCHEMA timeseries TO authenticated;
GRANT USAGE ON SCHEMA timeseries TO service_role;

-- Create a function to check if TimescaleDB is properly installed
CREATE OR REPLACE FUNCTION check_timescaledb_installation()
RETURNS TABLE(extension_name text, version text, installed boolean) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.extname::text as extension_name,
        e.extversion::text as version,
        true as installed
    FROM pg_extension e
    WHERE e.extname = 'timescaledb';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission on the check function
GRANT EXECUTE ON FUNCTION check_timescaledb_installation() TO anon;
GRANT EXECUTE ON FUNCTION check_timescaledb_installation() TO authenticated;
GRANT EXECUTE ON FUNCTION check_timescaledb_installation() TO service_role;

-- Log the TimescaleDB installation
DO $$
BEGIN
    RAISE NOTICE 'TimescaleDB extension initialized successfully';
END $$;

-- =============================================================================
-- PART 2: TimescaleDB Configuration and Utilities
-- =============================================================================

-- Create utility functions for time-series data management
CREATE OR REPLACE FUNCTION create_hypertable_if_not_exists(
    table_name text,
    time_column_name text DEFAULT 'created_at',
    chunk_time_interval interval DEFAULT interval '1 day'
)
RETURNS void AS $$
BEGIN
    -- Check if the table exists
    IF EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = create_hypertable_if_not_exists.table_name
    ) THEN
        -- Check if it's already a hypertable
        IF NOT EXISTS (
            SELECT FROM timescaledb_information.hypertables 
            WHERE hypertable_name = create_hypertable_if_not_exists.table_name
        ) THEN
            -- Convert to hypertable
            PERFORM create_hypertable(table_name, time_column_name, chunk_time_interval => chunk_time_interval);
            RAISE NOTICE 'Converted table % to hypertable with chunk interval %', table_name, chunk_time_interval;
        ELSE
            RAISE NOTICE 'Table % is already a hypertable', table_name;
        END IF;
    ELSE
        RAISE EXCEPTION 'Table % does not exist', table_name;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to add compression policy to a hypertable
CREATE OR REPLACE FUNCTION add_compression_policy(
    table_name text,
    compress_after interval DEFAULT interval '7 days',
    if_not_exists boolean DEFAULT true
)
RETURNS void AS $$
BEGIN
    IF if_not_exists AND EXISTS (
        SELECT FROM timescaledb_information.compression_settings 
        WHERE hypertable_name = add_compression_policy.table_name
    ) THEN
        RAISE NOTICE 'Compression policy already exists for table %', table_name;
        RETURN;
    END IF;
    
    PERFORM add_compression_policy(table_name, compress_after);
    RAISE NOTICE 'Added compression policy to table % with compress_after %', table_name, compress_after;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to add retention policy to a hypertable
CREATE OR REPLACE FUNCTION add_retention_policy(
    table_name text,
    drop_after interval DEFAULT interval '90 days',
    if_not_exists boolean DEFAULT true
)
RETURNS void AS $$
BEGIN
    IF if_not_exists AND EXISTS (
        SELECT FROM timescaledb_information.drop_chunks_policies 
        WHERE hypertable_name = add_retention_policy.table_name
    ) THEN
        RAISE NOTICE 'Retention policy already exists for table %', table_name;
        RETURN;
    END IF;
    
    PERFORM add_retention_policy(table_name, drop_after);
    RAISE NOTICE 'Added retention policy to table % with drop_after %', table_name, drop_after;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get hypertable information
CREATE OR REPLACE FUNCTION get_hypertable_info(table_name text DEFAULT NULL)
RETURNS TABLE(
    hypertable_name text,
    schema_name text,
    table_name text,
    num_chunks bigint,
    compression_enabled boolean,
    is_compressed boolean
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        h.hypertable_name::text,
        h.schema_name::text,
        h.table_name::text,
        h.num_chunks,
        COALESCE(cs.compress_enabled, false) as compression_enabled,
        COALESCE(cs.compress_enabled, false) as is_compressed
    FROM timescaledb_information.hypertables h
    LEFT JOIN timescaledb_information.compression_settings cs 
        ON h.hypertable_name = cs.hypertable_name
    WHERE (get_hypertable_info.table_name IS NULL OR h.hypertable_name = get_hypertable_info.table_name);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant permissions on utility functions
GRANT EXECUTE ON FUNCTION create_hypertable_if_not_exists(text, text, interval) TO anon;
GRANT EXECUTE ON FUNCTION create_hypertable_if_not_exists(text, text, interval) TO authenticated;
GRANT EXECUTE ON FUNCTION create_hypertable_if_not_exists(text, text, interval) TO service_role;

GRANT EXECUTE ON FUNCTION add_compression_policy(text, interval, boolean) TO anon;
GRANT EXECUTE ON FUNCTION add_compression_policy(text, interval, boolean) TO authenticated;
GRANT EXECUTE ON FUNCTION add_compression_policy(text, interval, boolean) TO service_role;

GRANT EXECUTE ON FUNCTION add_retention_policy(text, interval, boolean) TO anon;
GRANT EXECUTE ON FUNCTION add_retention_policy(text, interval, boolean) TO authenticated;
GRANT EXECUTE ON FUNCTION add_retention_policy(text, interval, boolean) TO service_role;

GRANT EXECUTE ON FUNCTION get_hypertable_info(text) TO anon;
GRANT EXECUTE ON FUNCTION get_hypertable_info(text) TO authenticated;
GRANT EXECUTE ON FUNCTION get_hypertable_info(text) TO service_role;

-- Create a view for easy access to TimescaleDB information
CREATE OR REPLACE VIEW timescaledb_status AS
SELECT 
    'TimescaleDB Extension' as component,
    extversion as version,
    'Installed' as status
FROM pg_extension 
WHERE extname = 'timescaledb'
UNION ALL
SELECT 
    'Hypertables' as component,
    count(*)::text as version,
    'Available' as status
FROM timescaledb_information.hypertables;

-- Grant permissions on the view
GRANT SELECT ON timescaledb_status TO anon;
GRANT SELECT ON timescaledb_status TO authenticated;
GRANT SELECT ON timescaledb_status TO service_role;

-- Log the configuration completion
DO $$
BEGIN
    RAISE NOTICE 'TimescaleDB configuration and utilities initialized successfully';
END $$;

-- =============================================================================
-- PART 3: Core Setup Complete
-- =============================================================================

-- Log the core setup completion
DO $$
BEGIN
    RAISE NOTICE 'TimescaleDB core setup completed successfully';
    RAISE NOTICE 'Business data examples are available in timescaledb_examples.sql';
END $$;

-- =============================================================================
-- PART 4: Final Status Check
-- =============================================================================

-- Verify TimescaleDB installation
DO $$
DECLARE
    ext_count integer;
    func_count integer;
    table_count integer;
BEGIN
    -- Check extension
    SELECT COUNT(*) INTO ext_count FROM pg_extension WHERE extname = 'timescaledb';
    
    -- Check utility functions
    SELECT COUNT(*) INTO func_count FROM pg_proc WHERE proname IN (
        'create_hypertable_if_not_exists',
        'add_compression_policy',
        'add_retention_policy',
        'get_hypertable_info',
        'check_timescaledb_installation'
    );
    
    RAISE NOTICE 'TimescaleDB Setup Summary:';
    RAISE NOTICE '- Extension installed: %', CASE WHEN ext_count > 0 THEN 'YES' ELSE 'NO' END;
    RAISE NOTICE '- Utility functions created: %', func_count;
    RAISE NOTICE '- Example tables created: %', table_count;
    RAISE NOTICE 'TimescaleDB initialization completed successfully!';
END $$;
