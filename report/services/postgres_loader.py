"""DB aggregates for investigation reports."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor


def _conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "finintel"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    )


def _one(query, params=None):
    conn = _conn()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or [])
                return dict(cur.fetchone())
    finally:
        conn.close()


def _all(query, params=None):
    conn = _conn()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or [])
                return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


class PostgresLoader:

    def summary_counts(self):
        r = _one(
            """
            SELECT
              (SELECT COUNT(*) FROM statements)   AS statements,
              (SELECT COUNT(*) FROM transactions) AS transactions,
              (SELECT COUNT(*) FROM entities)     AS entities,
              (SELECT COUNT(*) FROM transactions WHERE is_duplicate) AS duplicates,
              (SELECT COUNT(*) FROM transactions WHERE is_failed)    AS failed,
              (SELECT COALESCE(SUM(amount),0)::float8 FROM transactions
                 WHERE debit_credit='CREDIT') AS total_credit,
              (SELECT COALESCE(SUM(amount),0)::float8 FROM transactions
                 WHERE debit_credit='DEBIT')  AS total_debit
            """
        )
        return r

    def validation_summary(self):
        return _one(
            """
            SELECT
              COUNT(*) AS total,
              COUNT(*) FILTER (WHERE is_duplicate) AS duplicates,
              COUNT(*) FILTER (WHERE is_failed) AS failed,
              COUNT(*) FILTER (WHERE NOT is_valid) AS invalid,
              AVG(confidence_score)::float8 AS average_confidence
            FROM transactions
            """
        )

    def top_entities(self, limit=25):
        return _all(
            """
            SELECT entity_type, identifier, display_name
            FROM entities
            ORDER BY entity_type, identifier
            LIMIT %s
            """,
            [limit],
        )
