# Database Initialization Scripts

This directory contains database initialization scripts that are executed when the PostgreSQL container starts for the first time.

## Files

### `timescaledb.sql`
The core TimescaleDB initialization script that sets up the extension, utility functions, and basic configuration.

### `timescaledb_examples.sql`
Business data examples including sample tables, data generation functions, and common time-series scenarios.

## TimescaleDB Integration

The TimescaleDB setup is split into two scripts for better organization:

**Core Setup** (`timescaledb.sql`):
- Enables TimescaleDB extension
- Sets up permissions for Supabase roles
- Creates utility functions for hypertable management
- Provides monitoring and information functions

**Business Data**:
- Example tables for common time-series scenarios
- Sample data generation functions
- Best practice configurations for different data types

### 1. Core Extension Setup (timescaledb.sql)
- Enables TimescaleDB extension
- Sets up permissions for Supabase roles
- Creates dedicated schemas for time-series data

### 2. Utility Functions (timescaledb.sql)
- `create_hypertable_if_not_exists()` - Safe hypertable creation
- `add_compression_policy()` - Automatic compression management
- `add_retention_policy()` - Automatic retention management
- `get_hypertable_info()` - Monitoring and information

## Usage

The script is automatically executed during database initialization. To test the setup:

```bash
# Start the database
make up

# Test TimescaleDB functionality
make test-timescaledb
```

## Docker Integration

The scripts are mounted in the Docker container at:
```
./volumes/db/init/timescaledb.sql:/docker-entrypoint-initdb.d/init-scripts/100-timescaledb.sql:Z
./volumes/db/init/timescaledb_examples.sql:/docker-entrypoint-initdb.d/init-scripts/101-timescaledb-examples.sql:Z
```

This ensures they run after basic database setup but before application-specific migrations. 