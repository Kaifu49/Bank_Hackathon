"""
Investigation engine (Phase 5) — investigator-centric views built on the
money-flow graph: top-suspicious accounts, counterparty analysis, and a
chronological timeline.
"""

from __future__ import annotations

from services.flow_engine import resolve_counterparty


def top_suspicious(scored_risks, limit=20, account_only=False):
    """Condense risk-fusion output into an investigator-facing ranked list."""
    out = []
    for r in scored_risks:
        if account_only and r.get("type") != "ACCOUNT":
            continue
        out.append({
            "account": r["node"],
            "type": r["type"],
            "risk_score": r["risk_score"],
            "risk_level": r["risk_level"],
            "patterns": r["top_reasons"],
        })
        if len(out) >= limit:
            break
    return out


def counterparty_analysis(engine, account, top_n=20):
    """Who an account sent to / received from, aggregated by amount + count."""
    sent, received = [], []
    for (src, dst), e in engine.edges.items():
        if src == account:
            sent.append({"counterparty": dst, "amount": e["total_amount"],
                         "count": e["txn_count"]})
        if dst == account:
            received.append({"counterparty": src, "amount": e["total_amount"],
                             "count": e["txn_count"]})
    sent.sort(key=lambda x: x["amount"], reverse=True)
    received.sort(key=lambda x: x["amount"], reverse=True)
    node = engine.nodes.get(account, {})
    return {
        "account": account,
        "total_sent": node.get("total_out", 0.0),
        "total_received": node.get("total_in", 0.0),
        "distinct_receivers": len(sent),
        "distinct_senders": len(received),
        "sent_to": sent[:top_n],
        "received_from": received[:top_n],
    }


def timeline(rows, limit=500):
    """Chronological transaction events for an account (already date-ordered)."""
    events = []
    for r in rows[:limit]:
        events.append({
            "date": r.get("date"),
            "direction": r.get("debit_credit"),
            "amount": r.get("amount"),
            "balance": r.get("balance"),
            "counterparty": resolve_counterparty(r.get("narration")),
            "narration": r.get("narration"),
        })
    return events
