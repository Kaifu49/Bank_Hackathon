"""DB loader for the money-trail service. Loads ONE account's transactions in
chronological order (FIFO needs correct ordering)."""

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


_SELECT = """
SELECT
    t.id::text         AS txn_id,
    t.date::text       AS date,
    t.debit_credit,
    t.amount,
    t.narration,
    t.balance,
    t.statement_id::text AS statement_id,
    t.receiver_account,
    t.upi_id,
    t.reference_number,
    t.txn_type
FROM transactions t
WHERE t.is_valid = true
  AND (t.is_duplicate = false OR t.is_duplicate IS NULL)
"""

_ORDER = " ORDER BY t.date NULLS LAST, t.created_at"


def _rows(query, params=None):
    conn = _conn()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or [])
                rows = cur.fetchall()
        out = []
        for r in rows:
            d = dict(r)
            for k in ("amount", "balance"):
                if d.get(k) is not None:
                    d[k] = float(d[k])
            out.append(d)
        return out
    finally:
        conn.close()


class PostgresLoader:

    def load_statement_transactions(self, statement_id):
        return _rows(_SELECT + " AND t.statement_id = %s" + _ORDER,
                     [statement_id])

    def load_account_transactions(self, account):
        # account = statement holder (statements.account_number)
        q = (_SELECT +
             " AND t.statement_id IN (SELECT id FROM statements"
             " WHERE account_number = %s)" + _ORDER)
        return _rows(q, [account])

    def find_statement_for_transaction(self, transaction_id):
        rows = _rows(_SELECT + " AND t.id = %s", [transaction_id])
        return rows[0]["statement_id"] if rows else None
