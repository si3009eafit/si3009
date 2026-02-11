-- 00_schema.sql
DROP TABLE IF EXISTS audit_log;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  user_id     BIGINT PRIMARY KEY,
  email       TEXT NOT NULL,
  country     TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL
);

CREATE TABLE transactions (
  tx_id    BIGINT PRIMARY KEY,
  user_id  BIGINT NOT NULL REFERENCES users(user_id),
  amount   NUMERIC(12,2) NOT NULL,
  status   TEXT NOT NULL,
  tx_date  TIMESTAMPTZ NOT NULL
);

CREATE TABLE audit_log (
  id         BIGINT PRIMARY KEY,
  tx_id      BIGINT NOT NULL REFERENCES transactions(tx_id),
  event      TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL
);
