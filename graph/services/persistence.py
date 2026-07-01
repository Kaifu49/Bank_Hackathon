"""
Persist computed analysis (graph/risk) to the analysis_cache table so results
are not recomputed on every request. All operations are best-effort: a DB hiccup
never breaks an endpoint (compute still returns), it just skips caching.
"""

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


def save(scope: str, kind: str, payload) -> None:
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
        print(f"[WARN] analysis_cache save failed ({scope}/{kind}): {exc}")


def load(scope: str, kind: str):
    """Return {'payload':..., 'computed_at':...} or None."""
    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT payload, computed_at FROM analysis_cache "
                    "WHERE scope = %s AND kind = %s",
                    (scope, kind),
                )
                row = cur.fetchone()
        if not row:
            return None
        payload = row[0]
        if isinstance(payload, str):        # if json adapter not registered
            payload = json.loads(payload)
        return {"payload": payload, "computed_at": str(row[1])}
    except Exception as exc:
        print(f"[WARN] analysis_cache load failed ({scope}/{kind}): {exc}")
        return None
