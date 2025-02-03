BEGIN;

CREATE TABLE quotas (
    id                  SERIAL              PRIMARY KEY,
    user_id             SERIAL              REFERENCES users(id),
    quota_state         VARCHAR(10)         NOT NULL,
    amount              DOUBLE PRECISION    NOT NULL,
    price               DOUBLE PRECISION    NOT NULL,
    created_at          TIMESTAMP           NOT NULL
);

COMMIT;
