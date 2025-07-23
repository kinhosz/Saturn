BEGIN;

ALTER TABLE holding
ADD COLUMN wallet_id INTEGER REFERENCES wallet(id);

-- Setting a wallet for all existing holdings
UPDATE holding
SET wallet_id = wallet.id
FROM wallet
WHERE holding.user_id = wallet.user_id;

COMMIT;
