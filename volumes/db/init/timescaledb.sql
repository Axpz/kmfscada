-- =============================================================================
-- TimescaleDB Initialization Script (Optimized for Supabase OSS)
-- =============================================================================

-- Enable the TimescaleDB extension if not already enabled
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create a dedicated schema for time-series data (optional but recommended)
CREATE SCHEMA IF NOT EXISTS timeseries;

