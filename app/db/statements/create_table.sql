BEGIN;

CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
    email VARCHAR(30) UNIQUE NOT NULL,
    encrypted_password VARCHAR(50) NOT NULL,
    chat_id BIGINT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS orders(
    id SERIAL PRIMARY KEY,
    ask REAL,
    bid REAL,
    event_date TIMESTAMP default current_timestamp
);

CREATE TABLE IF NOT EXISTS trades(
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    order_bought_id INTEGER REFERENCES orders(id),
    order_sold_id INTEGER REFERENCES orders(id),
    quantity_sold REAL,
    quantity_bought REAL
);

COMMIT;