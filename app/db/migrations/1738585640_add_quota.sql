BEGIN;

CREATE TABLE quotas (
    id                  SERIAL              PRIMARY KEY,
    user_id             SERIAL              REFERENCES users(id),
    purchase_order_id   SERIAL              REFERENCES orders(id),
    quota_state         VARCHAR(10)         NOT NULL,
    amount              DOUBLE PRECISION    NOT NULL,
    price               DOUBLE PRECISION    NOT NULL,
    created_at          TIMESTAMP           NOT NULL
);

-- To be able to store 'PARTIALLY_CANCELED'
ALTER TABLE orders ALTER COLUMN order_state TYPE VARCHAR(20);

COMMIT;
