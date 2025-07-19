# TimescaleDB Setup and Usage Guide

## Overview

This document describes the TimescaleDB extension setup for the KMF SCADA system. TimescaleDB is a time-series database extension for PostgreSQL that provides automatic partitioning, compression, and retention policies for time-series data.

## Architecture

The TimescaleDB setup is consolidated into a single comprehensive initialization script:

**Core Script** (`volumes/db/init/timescaledb.sql`): Contains TimescaleDB core setup organized in logical sections:

1. **Core Extension Setup** - Enables the TimescaleDB extension and sets up basic permissions
2. **Configuration & Utilities** - Provides utility functions for managing hypertables, compression, and retention policies
3. **Core Setup Complete** - Verifies the core installation

**Business Data Script** Contains business data examples:

1. **Example Tables** - Common time-series scenarios (sensors, production, logs, financial)
2. **Sample Data Functions** - Functions to generate test data
3. **Business Data Verification** - Verifies the business data setup

## Initialization Order

The scripts are executed during database initialization as:

1. `100-timescaledb.sql` - Core TimescaleDB setup
2. `101-timescaledb-examples.sql` - Business data examples

## Features

### Core Features

- **Hypertables**: Automatic time-based partitioning of tables
- **Compression**: Automatic compression of older data to save storage
- **Retention Policies**: Automatic deletion of old data based on time
- **Continuous Aggregates**: Pre-computed aggregations for fast queries

### Utility Functions

#### `create_hypertable_if_not_exists(table_name, time_column, chunk_interval)`

Converts a regular table to a hypertable if it doesn't already exist.

```sql
-- Convert a table to hypertable with 1-hour chunks
SELECT create_hypertable_if_not_exists('sensor_data', 'timestamp', interval '1 hour');
```

#### `add_compression_policy(table_name, compress_after, if_not_exists)`

Adds automatic compression policy to a hypertable.

```sql
-- Compress data older than 7 days
SELECT add_compression_policy('sensor_data', interval '7 days');
```

#### `add_retention_policy(table_name, drop_after, if_not_exists)`

Adds automatic retention policy to a hypertable.

```sql
-- Delete data older than 1 year
SELECT add_retention_policy('sensor_data', interval '1 year');
```

#### `get_hypertable_info(table_name)`

Returns information about hypertables.

```sql
-- Get info for all hypertables
SELECT * FROM get_hypertable_info();

-- Get info for specific table
SELECT * FROM get_hypertable_info('sensor_data');
```

## Example Tables

### 1. Sensor Readings

For IoT or SCADA sensor data:

```sql
CREATE TABLE sensor_readings (
    id BIGSERIAL,
    sensor_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    value DOUBLE PRECISION NOT NULL,
    unit TEXT,
    location TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);
```

**Configuration:**
- Chunk interval: 1 hour
- Compression: After 7 days
- Retention: 1 year

### 2. Production Metrics

For manufacturing or production line data:

```sql
CREATE TABLE production_metrics (
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
```

**Configuration:**
- Chunk interval: 6 hours
- Compression: After 3 days
- Retention: 6 months

### 3. System Logs

For application or system logs:

```sql
CREATE TABLE system_logs (
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
```

**Configuration:**
- Chunk interval: 1 day
- Compression: After 1 day
- Retention: 3 months

## Usage Examples

### Inserting Data

```sql
-- Insert sensor data
INSERT INTO sensor_readings (sensor_id, value, unit, location)
VALUES ('temp_sensor_01', 23.5, 'celsius', 'room_a');

-- Insert production data
INSERT INTO production_metrics (machine_id, temperature, pressure, status)
VALUES ('machine_01', 85.2, 2.1, 'running');
```

### Querying Data

```sql
-- Get latest readings for a sensor
SELECT * FROM sensor_readings 
WHERE sensor_id = 'temp_sensor_01' 
ORDER BY timestamp DESC 
LIMIT 10;

-- Get hourly averages for the last 24 hours
SELECT 
    time_bucket('1 hour', timestamp) AS hour,
    sensor_id,
    avg(value) as avg_value
FROM sensor_readings 
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY hour, sensor_id
ORDER BY hour DESC;
```

### Sample Data Generation

```sql
-- Generate sample sensor data for testing
SELECT insert_sample_sensor_data(5, 24); -- 5 sensors, 24 hours of data
```

## Monitoring and Maintenance

### Check TimescaleDB Status

```sql
-- View overall status
SELECT * FROM timescaledb_status;

-- Check hypertable information
SELECT * FROM get_hypertable_info();
```

### Manual Compression

```sql
-- Manually compress chunks
SELECT compress_chunk(chunk_name) 
FROM timescaledb_information.chunks 
WHERE hypertable_name = 'sensor_readings' 
AND NOT is_compressed;
```

### Manual Retention

```sql
-- Manually drop old chunks
SELECT drop_chunks('sensor_readings', older_than => interval '1 year');
```

## Best Practices

### 1. Chunk Interval Selection

Choose chunk intervals based on your data volume and query patterns:

- **High-frequency data** (seconds/minutes): 1 hour chunks
- **Medium-frequency data** (minutes/hours): 6 hour chunks  
- **Low-frequency data** (hours/days): 1 day chunks

### 2. Compression Strategy

- Compress data that is no longer actively queried
- Consider query patterns when setting compression policies
- Monitor compression ratios and query performance

### 3. Retention Strategy

- Set retention based on business requirements and storage constraints
- Consider regulatory requirements for data retention
- Monitor storage usage and adjust retention policies accordingly

### 4. Indexing

- Create indexes on frequently queried columns
- Use composite indexes for multi-column queries
- Consider partial indexes for filtered queries

### 5. Continuous Aggregates

For frequently accessed aggregations, consider creating continuous aggregates:

```sql
-- Example: Hourly averages
CREATE MATERIALIZED VIEW sensor_readings_hourly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', timestamp) AS hour,
    sensor_id,
    avg(value) as avg_value,
    min(value) as min_value,
    max(value) as max_value
FROM sensor_readings
GROUP BY hour, sensor_id;
```

## Troubleshooting

### Common Issues

1. **Extension not available**: Ensure TimescaleDB is installed in the PostgreSQL image
2. **Permission errors**: Check that roles have proper permissions on schemas and functions
3. **Chunk creation failures**: Verify chunk intervals are appropriate for your data volume
4. **Compression failures**: Check that compression policies are properly configured

### Debugging Queries

```sql
-- Check chunk information
SELECT * FROM timescaledb_information.chunks 
WHERE hypertable_name = 'your_table_name';

-- Check compression settings
SELECT * FROM timescaledb_information.compression_settings 
WHERE hypertable_name = 'your_table_name';

-- Check retention policies
SELECT * FROM timescaledb_information.drop_chunks_policies 
WHERE hypertable_name = 'your_table_name';
```

## Performance Considerations

1. **Chunk Size**: Larger chunks reduce overhead but may impact query performance
2. **Compression**: Compressed data uses less storage but may be slower to query
3. **Indexes**: Create indexes on frequently queried columns
4. **Continuous Aggregates**: Use for frequently accessed aggregations
5. **Partitioning**: Consider additional partitioning strategies for very large datasets

## Security

- All utility functions are created with `SECURITY DEFINER`
- Proper permissions are granted to Supabase roles (anon, authenticated, service_role)
- Sensitive data should be encrypted at rest and in transit
- Regular security audits should be performed

## Migration from Regular Tables

To migrate existing tables to hypertables:

```sql
-- 1. Create the table (if it doesn't exist)
CREATE TABLE IF NOT EXISTS your_table (
    id BIGSERIAL,
    timestamp TIMESTAMPTZ NOT NULL,
    -- other columns...
);

-- 2. Convert to hypertable
SELECT create_hypertable_if_not_exists('your_table', 'timestamp');

-- 3. Add compression and retention policies
SELECT add_compression_policy('your_table', interval '7 days');
SELECT add_retention_policy('your_table', interval '1 year');
```

## References

- [TimescaleDB Documentation](https://docs.timescale.com/)
- [TimescaleDB Best Practices](https://docs.timescale.com/timescaledb/latest/how-to-guides/best-practices/)
- [Supabase Documentation](https://supabase.com/docs) 