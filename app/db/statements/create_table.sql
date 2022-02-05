BEGIN;

CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
    email VARCHAR(30) UNIQUE NOT NULL,
    encrypted_password VARCHAR(50) NOT NULL,
    session_state SMALLINT NOT NULL CHECK(session_state >= 0),
    chat_id VARCHAR(50) UNIQUE NOT NULL
);

COMMIT;