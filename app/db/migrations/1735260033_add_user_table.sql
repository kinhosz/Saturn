BEGIN;

CREATE TABLE users (
    id                  SERIAL      PRIMARY KEY,
    telegram_chat_id    BIGINT      NOT NULL,
    telegram_username   VARCHAR(20) NOT NULL,
    active              BOOLEAN     NOT NULL DEFAULT FALSE
);

COMMIT;
