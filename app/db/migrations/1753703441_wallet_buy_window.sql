BEGIN;

ALTER TABLE wallet
ADD COLUMN buy_window INTEGER DEFAULT 1536, -- 1 day
DROP COLUMN percentage_to_buy,
DROP COLUMN exchange_count;

COMMIT;