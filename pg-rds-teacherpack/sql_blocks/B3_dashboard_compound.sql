-- B3_dashboard_compound.sql
CREATE INDEX IF NOT EXISTS idx_orders_customer_date_desc ON orders(customer_id, order_date DESC);
ANALYZE;
