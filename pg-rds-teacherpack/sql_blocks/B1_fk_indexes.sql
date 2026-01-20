-- B1_fk_indexes.sql
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_order_item_order_id ON order_item(order_id);
CREATE INDEX IF NOT EXISTS idx_order_item_product_id ON order_item(product_id);
CREATE INDEX IF NOT EXISTS idx_payment_order_id ON payment(order_id);
ANALYZE;
