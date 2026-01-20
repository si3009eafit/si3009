-- B4_sargability.sql
-- Opción 1 (recomendada): reescribir Q5 a rango (no requiere índice extra)
-- WHERE order_date >= '2023-11-15' AND order_date < '2023-11-16'

-- Opción 2 (didáctica): índice por expresión
CREATE INDEX IF NOT EXISTS idx_orders_order_date_day_expr ON orders (date_trunc('day', order_date));
ANALYZE;
