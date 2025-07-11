docker exec -it scada-db psql -U postgres -d scada

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

UPDATE auth.users
SET raw_user_meta_data = '{"role": "super_admin"}'::jsonb
WHERE is_super_admin = true;
