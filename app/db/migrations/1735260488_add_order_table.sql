BEGIN;

CREATE TABLE orders (
    id                      SERIAL              PRIMARY KEY NOT NULL,
    user_id                 SERIAL              REFERENCES users(id),
    foxbit_order_id         VARCHAR(15),
    client_order_id         VARCHAR(15)         NOT NULL,
    market_symbol           VARCHAR(10)         NOT NULL,
    side                    VARCHAR(4)          NOT NULL,
    market_type             VARCHAR(10)         NOT NULL,
    order_state             VARCHAR(10)         NOT NULL,
    price                   DOUBLE PRECISION,
    price_avg               DOUBLE PRECISION,
    quantity                DOUBLE PRECISION,
    quantity_executed       DOUBLE PRECISION,
    instant_amount          DOUBLE PRECISION,
    instant_amount_executed DOUBLE PRECISION,
    created_at              TIMESTAMP,
    trades_count            INTEGER,
    remark                  VARCHAR(30),
    funds_received          DOUBLE PRECISION,
    fee_paid                DOUBLE PRECISION,
    post_only               BOOLEAN,
    time_in_force           VARCHAR(5),
    cancellation_reason     INTEGER
);

COMMIT;
