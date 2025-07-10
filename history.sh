docker exec -it scada-db psql -U postgres -d scada

\pset pager off


docker exec -it supabase-db psql -U supabase_admin -d _supabase

SELECT * FROM _supavisor.tenants LIMIT 10;
SELECT * FROM _supavisor.users LIMIT 10;
