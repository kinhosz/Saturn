BEGIN;

CREATE TABLE balances (
    id              SERIAL              NOT NULL    PRIMARY KEY,
    user_id         SERIAL              REFERENCES users(id),
    amount          DOUBLE PRECISION    NOT NULL, 
    base_symbol     VARCHAR(5)          NOT NULL,
    price           DOUBLE PRECISION    NOT NULL,
    quote_symbol    VARCHAR(5)          NOT NULL,
    CONSTRAINT unique_user_base_quote UNIQUE (user_id, base_symbol, quote_symbol)
);

COMMIT;
