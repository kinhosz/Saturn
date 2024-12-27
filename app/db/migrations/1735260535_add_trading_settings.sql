BEGIN;

CREATE TABLE trading_settings(
    id                      SERIAL             PRIMARY KEY,
    user_id                 SERIAL             REFERENCES users(id),
    lock_buy                BOOLEAN            NOT NULL DEFAULT TRUE,
    lock_sell               BOOLEAN            NOT NULL DEFAULT TRUE,
    allocation_percentage   DOUBLE PRECISION   NOT NULL DEFAULT 0.10,
    percentage_to_buy       DOUBLE PRECISION   NOT NULL DEFAULT 0.99,
    percentage_to_sell      DOUBLE PRECISION   NOT NULL DEFAULT 1.01
);

COMMIT;
