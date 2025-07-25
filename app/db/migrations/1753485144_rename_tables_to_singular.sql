BEGIN;

ALTER TABLE deposits    RENAME TO deposit;
ALTER TABLE orders      RENAME TO trade;
ALTER TABLE quotas      RENAME TO quota;
ALTER TABLE users       RENAME TO res_user;

COMMIT;
