-- Cache of computed analysis so graph/risk/report results are persisted and
-- not recomputed on every request. Keyed by (scope, kind).
--   scope: 'all' (whole network) or a statement UUID
--   kind : 'analyze' | 'risk' | 'report'
CREATE TABLE IF NOT EXISTS analysis_cache (
    scope       TEXT NOT NULL,
    kind        TEXT NOT NULL,
    payload     JSONB NOT NULL,
    computed_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (scope, kind)
);
