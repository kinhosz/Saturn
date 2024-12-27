BEGIN;

CREATE TABLE currency (
    id              SERIAL              NOT NULL    PRIMARY KEY,
    user_id         SERIAL              REFERENCES users(id),
    amount          DOUBLE PRECISION    NOT NULL, 
    base_symbol     VARCHAR(5)          NOT NULL,
    price           DOUBLE PRECISION    NOT NULL,
    quote_symbol    VARCHAR(5)          NOT NULL
);

COMMIT;
