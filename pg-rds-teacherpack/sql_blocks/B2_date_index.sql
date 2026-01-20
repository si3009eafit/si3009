-- B2_date_index.sql
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
ANALYZE;
