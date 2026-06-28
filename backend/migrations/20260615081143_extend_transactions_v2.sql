-- Add migration script here
ALTER TABLE transactions
ADD COLUMN IF NOT EXISTS reference_number TEXT;

ALTER TABLE transactions
ADD COLUMN IF NOT EXISTS debit_credit TEXT;

ALTER TABLE transactions
ADD COLUMN IF NOT EXISTS platform TEXT;