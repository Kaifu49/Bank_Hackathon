"""
PostgresLoader — load clean transactions from the DB for graph intelligence.

Unlike the anomaly/temporal loaders (which require sender_account, excluding
real single-account statements), this loader joins `statements` to obtain the
holder account and returns narration + debit_credit so the MoneyFlowEngine can
derive counterparties for single-account statements too.

Only valid, non-duplicate rows are loaded (clean dataset). A fresh connection
is opened per call so a transient DB outage never bricks the service at import.
"""

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


_BASE = """
SELECT
    COALESCE(s.account_number, 'STMT:' || t.statement_id::text) AS account,
    t.sender_account,
    t.receiver_account,
    t.amount,
    t.debit_credit,
    t.narration,
    t.balance,
    t.reference_number,
    t.date,
    t.statement_id
FROM transactions t
JOIN statements s ON s.id = t.statement_id
WHERE t.is_valid = true
  AND (t.is_duplicate = false OR t.is_duplicate IS NULL)
"""


def _rows(query, params=None):
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or [])
            rows = cur.fetchall()
    return [_clean(dict(r)) for r in rows]


def _clean(r):
    for k in ("amount", "balance"):
        if r.get(k) is not None:
            r[k] = float(r[k])
    if r.get("date") is not None:
        r["date"] = str(r["date"])
    if r.get("statement_id") is not None:
        r["statement_id"] = str(r["statement_id"])
    return r


class PostgresLoader:

    def load_all_transactions(self):
        return _rows(_BASE + " ORDER BY t.date NULLS LAST, t.created_at")

    def load_statement_transactions(self, statement_id):
        return _rows(
            _BASE + " AND t.statement_id = %s ORDER BY t.date NULLS LAST, t.created_at",
            [statement_id],
        )

    def load_account_transactions(self, account):
        return _rows(
            _BASE + """ AND (s.account_number = %s
                            OR t.sender_account = %s
                            OR t.receiver_account = %s)
                       ORDER BY t.date NULLS LAST, t.created_at""",
            [account, account, account],
        )
