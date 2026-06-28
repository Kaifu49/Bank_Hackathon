-- Async processing jobs (DB-backed so status survives restarts).
CREATE TABLE IF NOT EXISTS jobs (
    id           UUID PRIMARY KEY,
    statement_id UUID REFERENCES statements(id),
    status       TEXT NOT NULL DEFAULT 'queued',  -- queued|processing|completed|failed
    progress     INT  NOT NULL DEFAULT 0,         -- 0..100
    stage        TEXT,                            -- ocr|standardize|validate|...
    error        TEXT,
    created_at   TIMESTAMP DEFAULT NOW(),
    updated_at   TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_jobs_statement ON jobs(statement_id);
