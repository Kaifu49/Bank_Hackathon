"""Persist assembled reports to analysis_cache (best-effort)."""

import json
import os
import psycopg2


def _conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "finintel"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    )


def save(scope, kind, payload):
    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO analysis_cache (scope, kind, payload, computed_at)
                    VALUES (%s, %s, %s::jsonb, NOW())
                    ON CONFLICT (scope, kind)
                    DO UPDATE SET payload = EXCLUDED.payload, computed_at = NOW()
                    """,
                    (scope, kind, json.dumps(payload)),
                )
            conn.commit()
    except Exception as exc:
        print(f"[WARN] report cache save failed ({scope}/{kind}): {exc}")


def load(scope, kind):
    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT payload FROM analysis_cache WHERE scope=%s AND kind=%s",
                    (scope, kind),
                )
                row = cur.fetchone()
        if not row:
            return None
        payload = row[0]
        return json.loads(payload) if isinstance(payload, str) else payload
    except Exception as exc:
        print(f"[WARN] report cache load failed ({scope}/{kind}): {exc}")
        return None
