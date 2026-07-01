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
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or [])
            return dict(cur.fetchone())


def _all(query, params=None):
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or [])
            return [dict(r) for r in cur.fetchall()]


class PostgresLoader:

    def summary_counts(self, statement_id=None):
        if statement_id:
            return _one(
                """
                SELECT
                  1 AS statements,
                  (SELECT COUNT(*) FROM transactions
                     WHERE statement_id = %(sid)s::uuid) AS transactions,
                  (SELECT COUNT(*) FROM entities) AS entities,
                  (SELECT COUNT(*) FROM transactions
                     WHERE statement_id = %(sid)s::uuid AND is_duplicate) AS duplicates,
                  (SELECT COUNT(*) FROM transactions
                     WHERE statement_id = %(sid)s::uuid AND is_failed) AS failed,
                  (SELECT COALESCE(SUM(amount),0)::float8 FROM transactions
                     WHERE statement_id = %(sid)s::uuid AND debit_credit='CREDIT') AS total_credit,
                  (SELECT COALESCE(SUM(amount),0)::float8 FROM transactions
                     WHERE statement_id = %(sid)s::uuid AND debit_credit='DEBIT') AS total_debit
                """,
                {"sid": statement_id},
            )
        return _one(
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

    def validation_summary(self, statement_id=None):
        if statement_id:
            return _one(
                """
                SELECT
                  COUNT(*) AS total,
                  COUNT(*) FILTER (WHERE is_duplicate) AS duplicates,
                  COUNT(*) FILTER (WHERE is_failed) AS failed,
                  COUNT(*) FILTER (WHERE NOT is_valid) AS invalid,
                  AVG(confidence_score)::float8 AS average_confidence
                FROM transactions WHERE statement_id = %(sid)s::uuid
                """,
                {"sid": statement_id},
            )
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
