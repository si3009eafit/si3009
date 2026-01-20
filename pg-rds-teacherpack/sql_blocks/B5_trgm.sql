-- B5_trgm.sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS idx_product_name_trgm ON product USING gin (name gin_trgm_ops);
ANALYZE;
