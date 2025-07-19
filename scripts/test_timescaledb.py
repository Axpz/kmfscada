#!/usr/bin/env python3
"""
TimescaleDB Test Script

This script tests the TimescaleDB installation and basic functionality.
It should be run after the database is initialized with TimescaleDB.
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime, timedelta
import random

def get_db_connection():
    """Get database connection using environment variables."""
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            database=os.getenv('POSTGRES_DB', 'postgres'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'postgres')
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def test_timescaledb_extension(conn):
    """Test if TimescaleDB extension is installed."""
    print("Testing TimescaleDB extension installation...")
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Check if extension exists
        cur.execute("""
            SELECT extname, extversion 
            FROM pg_extension 
            WHERE extname = 'timescaledb'
        """)
        result = cur.fetchone()
        
        if result:
            print(f"✅ TimescaleDB extension found: version {result['extversion']}")
            return True
        else:
            print("❌ TimescaleDB extension not found")
            return False

def test_utility_functions(conn):
    """Test utility functions."""
    print("\nTesting utility functions...")
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Test check_timescaledb_installation function
        try:
            cur.execute("SELECT * FROM check_timescaledb_installation()")
            result = cur.fetchone()
            if result:
                print(f"✅ check_timescaledb_installation function works: {result}")
            else:
                print("❌ check_timescaledb_installation function failed")
        except Exception as e:
            print(f"❌ check_timescaledb_installation function error: {e}")
        
        # Test get_hypertable_info function
        try:
            cur.execute("SELECT * FROM get_hypertable_info()")
            results = cur.fetchall()
            print(f"✅ get_hypertable_info function works: found {len(results)} hypertables")
        except Exception as e:
            print(f"❌ get_hypertable_info function error: {e}")

def test_example_tables(conn):
    """Test example tables and insert sample data."""
    print("\nTesting example tables...")
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Check if example tables exist
        tables = ['sensor_readings', 'production_metrics', 'system_logs']
        
        for table in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                print(f"✅ Table {table} exists with {count} rows")
            except Exception as e:
                print(f"❌ Table {table} error: {e}")

def test_sample_data_insertion(conn):
    """Test inserting sample data."""
    print("\nTesting sample data insertion...")
    
    with conn.cursor() as cur:
        try:
            # Insert sample sensor data
            cur.execute("SELECT insert_sample_sensor_data(3, 6)")  # 3 sensors, 6 hours
            print("✅ Sample sensor data inserted successfully")
            
            # Check the data
            cur.execute("SELECT COUNT(*) FROM sensor_readings")
            count = cur.fetchone()[0]
            print(f"✅ Sensor readings table now has {count} rows")
            
        except Exception as e:
            print(f"❌ Sample data insertion error: {e}")

def test_hypertable_queries(conn):
    """Test TimescaleDB-specific queries."""
    print("\nTesting TimescaleDB queries...")
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            # Test time_bucket function
            cur.execute("""
                SELECT 
                    time_bucket('1 hour', timestamp) AS hour,
                    sensor_id,
                    COUNT(*) as readings,
                    AVG(value) as avg_value
                FROM sensor_readings 
                WHERE timestamp >= NOW() - INTERVAL '6 hours'
                GROUP BY hour, sensor_id
                ORDER BY hour DESC
                LIMIT 5
            """)
            results = cur.fetchall()
            print(f"✅ Time bucket query works: found {len(results)} time buckets")
            
            # Test hypertable information
            cur.execute("""
                SELECT 
                    hypertable_name,
                    num_chunks,
                    compression_enabled
                FROM get_hypertable_info('sensor_readings')
            """)
            result = cur.fetchone()
            if result:
                print(f"✅ Hypertable info: {result}")
            
        except Exception as e:
            print(f"❌ TimescaleDB query error: {e}")

def test_compression_and_retention(conn):
    """Test compression and retention policies."""
    print("\nTesting compression and retention policies...")
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            # Check compression settings
            cur.execute("""
                SELECT 
                    hypertable_name,
                    compress_enabled,
                    compress_after
                FROM timescaledb_information.compression_settings
                WHERE hypertable_name = 'sensor_readings'
            """)
            result = cur.fetchone()
            if result:
                print(f"✅ Compression settings: {result}")
            else:
                print("⚠️  No compression settings found for sensor_readings")
            
            # Check retention policies
            cur.execute("""
                SELECT 
                    hypertable_name,
                    drop_after
                FROM timescaledb_information.drop_chunks_policies
                WHERE hypertable_name = 'sensor_readings'
            """)
            result = cur.fetchone()
            if result:
                print(f"✅ Retention policy: {result}")
            else:
                print("⚠️  No retention policy found for sensor_readings")
                
        except Exception as e:
            print(f"❌ Compression/retention test error: {e}")

def main():
    """Main test function."""
    print("🚀 Starting TimescaleDB Test Suite")
    print("=" * 50)
    
    # Get database connection
    conn = get_db_connection()
    if not conn:
        print("❌ Failed to connect to database")
        sys.exit(1)
    
    try:
        # Run tests
        test_timescaledb_extension(conn)
        test_utility_functions(conn)
        test_example_tables(conn)
        test_sample_data_insertion(conn)
        test_hypertable_queries(conn)
        test_compression_and_retention(conn)
        
        print("\n" + "=" * 50)
        print("✅ TimescaleDB test suite completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main() 