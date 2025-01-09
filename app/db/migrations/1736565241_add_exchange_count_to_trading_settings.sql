BEGIN;

ALTER TABLE trading_settings
ADD COLUMN exchange_count INTEGER DEFAULT 0;

COMMIT;
