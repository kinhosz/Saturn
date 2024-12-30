BEGIN;

CREATE TABLE deposits (
    id      SERIAL           PRIMARY KEY,
    user_id SERIAL           REFERENCES users(id),
    amount  DOUBLE PRECISION NOT NULL,
    stage   VARCHAR(10)      NOT NULL
);

COMMIT;
