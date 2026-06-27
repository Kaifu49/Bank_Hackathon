CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE statements (
    id UUID PRIMARY KEY,
    filename TEXT NOT NULL,
    bank_name TEXT,
    upload_time TIMESTAMP DEFAULT NOW(),
    status TEXT NOT NULL,
    file_path TEXT NOT NULL
);

CREATE TABLE transactions (
    id UUID PRIMARY KEY,

    statement_id UUID
        REFERENCES statements(id),

    date DATE,

    sender_account TEXT,
    receiver_account TEXT,

    amount DECIMAL(15,2),

    txn_type TEXT,

    upi_id TEXT,

    narration TEXT,
    narration_normalized TEXT,

    balance DECIMAL(15,2),

    bank_name TEXT,

    raw_row JSONB,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE entities (
    id UUID PRIMARY KEY,

    entity_type TEXT,

    identifier TEXT UNIQUE,

    display_name TEXT,

    metadata JSONB
);

CREATE TABLE risk_profiles (
    entity_id UUID REFERENCES entities(id),

    rule_score FLOAT,
    stat_score FLOAT,
    temporal_score FLOAT,

    graph_score FLOAT,
    gnn_score FLOAT,

    final_score FLOAT,

    risk_level TEXT,

    patterns JSONB,

    computed_at TIMESTAMP DEFAULT NOW()
);