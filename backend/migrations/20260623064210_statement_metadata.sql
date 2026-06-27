-- Add migration script here
ALTER TABLE statements

ADD COLUMN account_number TEXT,
ADD COLUMN account_holder TEXT,
ADD COLUMN ifsc_code TEXT,

ADD COLUMN opening_balance NUMERIC(15,2),
ADD COLUMN closing_balance NUMERIC(15,2),

ADD COLUMN statement_start_date DATE,
ADD COLUMN statement_end_date DATE;