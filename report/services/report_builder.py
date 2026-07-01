"""
ReportBuilder — assembles the investigation report data model from the DB
(counts, validation, entities) + the graph service (money-flow, round-trips,
risk). Graph enrichment is best-effort so a report is always produced.
"""

import json
import os
import urllib.request

from services.postgres_loader import PostgresLoader
from services import persistence

GRAPH_URL = os.getenv("GRAPH_URL", "http://localhost:8005")


def _get(url, timeout=30):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as exc:
        print(f"[INFO] report graph fetch failed ({url}): {exc}")
        return {}


class ReportBuilder:

    def __init__(self):
        self.loader = PostgresLoader()

    def build(self, case_id="all", refresh=False):
        if not refresh:
            cached = persistence.load(case_id, "report")
            if cached:
                return cached

        scoped = case_id and case_id != "all"
        stmt = case_id if scoped else None

        counts = self.loader.summary_counts(stmt)
        validation = self.loader.validation_summary(stmt)
        entities = self.loader.top_entities(25)

        if scoped:
            analysis = _get(f"{GRAPH_URL}/flow/analyze/statement/{case_id}")
        else:
            analysis = _get(f"{GRAPH_URL}/flow/analyze/all")
        risks = _get(f"{GRAPH_URL}/risk/top?limit=20")

        mf = analysis.get("summary", {}) if isinstance(analysis, dict) else {}
        round_trips = analysis.get("round_trips", []) if isinstance(analysis, dict) else []
        communities = analysis.get("communities", []) if isinstance(analysis, dict) else []
        top_risks = risks.get("top_risks", []) if isinstance(risks, dict) else []

        report = {
            "title": "Financial Crime Investigation Report",
            "case_id": case_id,
            "executive_summary": {
                "statements": counts.get("statements", 0),
                "transactions": counts.get("transactions", 0),
                "entities": counts.get("entities", 0),
                "duplicates": counts.get("duplicates", 0),
                "failed_or_reversed": counts.get("failed", 0),
                "total_credit": counts.get("total_credit", 0.0),
                "total_debit": counts.get("total_debit", 0.0),
                "round_trips_detected": len(round_trips),
                "communities_detected": len(communities),
                "high_risk_accounts": sum(
                    1 for r in top_risks if r.get("risk_level") in ("HIGH", "CRITICAL")
                ),
            },
            "money_flow": {
                "destination_account": mf.get("destination_account"),
                "accumulation_accounts": mf.get("accumulation_accounts", [])[:10],
                "source_accounts": mf.get("source_accounts", [])[:10],
                "fan_in": mf.get("fan_in", [])[:10],
                "fan_out": mf.get("fan_out", [])[:10],
                "layering": mf.get("layering", [])[:10],
            },
            "round_trips": round_trips[:25],
            "top_risks": top_risks,
            "top_entities": entities,
            "validation": validation,
            "recommendations": self._recommendations(mf, round_trips, top_risks, validation),
        }
        persistence.save(case_id, "report", report)
        return report

    def _recommendations(self, mf, round_trips, top_risks, validation):
        recs = []
        if round_trips:
            recs.append(
                f"Investigate {len(round_trips)} circular/round-trip chain(s); "
                "these strongly indicate layering."
            )
        dest = mf.get("destination_account")
        if dest:
            recs.append(
                f"Scrutinize destination account {dest} where funds accumulate."
            )
        crit = [r for r in top_risks if r.get("risk_level") == "CRITICAL"]
        if crit:
            names = ", ".join(str(r.get("node")) for r in crit[:5])
            recs.append(f"Prioritize CRITICAL-risk accounts: {names}.")
        if validation.get("failed"):
            recs.append(
                f"Review {validation['failed']} failed/reversed transactions for "
                "intentional probing or refunds."
            )
        if not recs:
            recs.append("No high-priority red flags detected in the current dataset.")
        return recs
