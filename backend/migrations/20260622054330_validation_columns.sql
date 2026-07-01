-- Add migration script here
ALTER TABLE transactions
ADD COLUMN is_duplicate BOOLEAN
DEFAULT FALSE;

ALTER TABLE transactions
ADD COLUMN is_failed BOOLEAN
DEFAULT FALSE;

ALTER TABLE transactions
ADD COLUMN is_valid BOOLEAN
DEFAULT TRUE;

ALTER TABLE transactions
ADD COLUMN confidence_score FLOAT;

ALTER TABLE transactions
ADD COLUMN validation_notes JSONB;