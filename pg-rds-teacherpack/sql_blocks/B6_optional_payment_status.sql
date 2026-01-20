-- B6_optional_payment_status.sql
-- Útil si payment_status es selectivo (no siempre).
CREATE INDEX IF NOT EXISTS idx_payment_status ON payment(payment_status);
ANALYZE;
