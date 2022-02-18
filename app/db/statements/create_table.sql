BEGIN;

CREATE TABLE IF NOT EXISTS usessions(
    id SERIAL PRIMARY KEY,
    email VARCHAR(30) UNIQUE NOT NULL,
    encrypted_password VARCHAR(50) NOT NULL,
    session_state SMALLINT NOT NULL CHECK(session_state >= 0),
    chat_id VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS trades(
    id SERIAL PRIMARY KEY,
    usession_id INT,
    sell REAL,
    buy REAL,
    quantity_selled REAL,
    quantity_buyed REAL,
    CONSTRAINT fk_usessins
        FOREIGN KEY(usession_id)
            REFERENCES usessions(id)
);

CREATE TABLE IF NOT EXISTS tickets(
    id SERIAL PRIMARY KEY,
    ask REAL,
    bid REAL,
    added TIMESTAMP
);

COMMIT;