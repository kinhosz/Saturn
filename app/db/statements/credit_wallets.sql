BEGIN;

CREATE TABLE IF NOT EXISTS wallets(
    id SERIAL PRIMARY KEY,
    profit_rate REAL DEFAULT 0.5,
    total_amount_BRL REAL,
    ceil REAL,
    floor REAL,
    user_id INTEGER NOT NULL REFERENCES users(id)
);

COMMIT;