docker exec -it supabase-db psql -U postgres -d scada

\pset pager off


docker exec -it supabase-db psql -U supabase_admin -d scada

SELECT * FROM _supavisor.tenants LIMIT 10;
SELECT * FROM _supavisor.users LIMIT 10;

UPDATE auth.users SET raw_user_meta_data = jsonb_set(
  COALESCE(raw_user_meta_data, '{}'::jsonb),
  '{is_super_admin}',
  to_jsonb(is_super_admin),
  true
) WHERE is_super_admin IS NOT NULL;

UPDATE auth.users SET raw_user_meta_data = raw_user_meta_data - 'is_super_admin' WHERE raw_user_meta_data ? 'is_super_admin';

UPDATE auth.users SET raw_user_meta_data = raw_user_meta_data || '{"role": "super_admin"}'::jsonb
UPDATE auth.users SET raw_user_meta_data = raw_user_meta_data || '{"role": "admin"}'::jsonb


# display all functions
\df

# display all tables
\dt

# display all schemas
\dn


CREATE EXTENSION IF NOT EXISTS timescaledb;
SELECT * FROM pg_extension WHERE extname = 'timescaledb';

CREATE SCHEMA IF NOT EXISTS timeseries;
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'timeseries';



SELECT create_hypertable('public.sensor_readings', 'timestamp', if_not_exists => TRUE, migrate_data => TRUE);
SELECT set_chunk_time_interval('public.sensor_readings', INTERVAL '1 day');

SELECT * FROM timescaledb_information.hypertables;
SELECT * FROM timescaledb_information.dimensions;
SELECT * FROM timescaledb_information.chunks;
