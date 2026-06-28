"""
RiskFusionEngine — Phase 4. Fuse multiple signals into one explainable
per-account/per-node risk score.

Signals fused (each normalized to 0..1):
  graph:        round-trip membership, layering (pass-through), accumulation
                (in-flow concentration), fan-in, fan-out, degree centrality
  transaction:  failed/reversal ratio, volume, velocity (txn count)
  external:     temporal_score, anomaly_score  (optional — merged if provided)

Output per node:
  { node, risk_score (0-100), risk_level, factors[], top_reasons[], signals{} }
Each factor carries its weight, normalized value, contribution and a
human-readable explanation + evidence — so every score is fully auditable
(supports the Explainability phase and the /risk endpoints).
"""

from __future__ import annotations

from collections import defaultdict


# weight per signal; renormalized over whichever signals are present
WEIGHTS = {
    "round_trip": 0.22,
    "layering": 0.18,
    "accumulation": 0.15,
    "fan_in": 0.10,
    "fan_out": 0.10,
    "anomaly": 0.10,
    "temporal": 0.08,
    "failed_ratio": 0.04,
    "centrality": 0.03,
}

_EXPLAIN = {
    "round_trip": "Participates in circular/round-trip money movement",
    "layering": "Money passes through almost unchanged (layering/mule pattern)",
    "accumulation": "Concentrates large incoming funds (accumulation point)",
    "fan_in": "Receives from many distinct senders (collection)",
    "fan_out": "Distributes to many distinct receivers (dispersion)",
    "anomaly": "Statistically anomalous behaviour (isolation forest)",
    "temporal": "Suspicious temporal pattern (burst/velocity/structuring)",
    "failed_ratio": "High proportion of failed/reversed transactions",
    "centrality": "Highly connected hub in the network",
}


def _norm(value, max_value):
    if not max_value or max_value <= 0:
        return 0.0
    return max(0.0, min(1.0, value / max_value))


def _level(score):
    if score >= 80:
        return "CRITICAL"
    if score >= 60:
        return "HIGH"
    if score >= 35:
        return "MEDIUM"
    return "LOW"


class RiskFusionEngine:

    def score_network(self, engine, rows=None, round_trips=None,
                      temporal_map=None, anomaly_map=None):
        round_trips = round_trips or []
        temporal_map = temporal_map or {}
        anomaly_map = anomaly_map or {}

        # round-trip membership counts
        rt_count = defaultdict(int)
        for cyc in round_trips:
            for n in set(cyc.get("nodes", [])):
                rt_count[n] += 1
        max_rt = max(rt_count.values(), default=0)

        # per-account transaction stats (holder perspective)
        txn_stats = self._txn_stats(rows or [])
        max_vol = max((s["volume"] for s in txn_stats.values()), default=0)
        max_cnt = max((s["count"] for s in txn_stats.values()), default=0)

        # graph maxima for normalization
        nodes = engine.nodes
        max_in = max((n["total_in"] for n in nodes.values()), default=0)
        max_send = max((len(engine.in_adj.get(nid, ())) for nid in nodes),
                       default=0)
        max_recv = max((len(engine.out_adj.get(nid, ())) for nid in nodes),
                       default=0)
        n_nodes = len(nodes)

        results = []
        for nid, node in nodes.items():
            in_deg = len(engine.in_adj.get(nid, ()))
            out_deg = len(engine.out_adj.get(nid, ()))
            ti, to = node["total_in"], node["total_out"]
            passthrough = 0.0
            if ti > 0 and to > 0:
                passthrough = 1 - abs(ti - to) / max(ti, to)
            stats = txn_stats.get(nid, {})

            signals = {
                "round_trip": _norm(rt_count.get(nid, 0), max(1, max_rt))
                if nid in rt_count else 0.0,
                "layering": passthrough,
                "accumulation": _norm(ti, max_in),
                "fan_in": _norm(in_deg, max_send),
                "fan_out": _norm(out_deg, max_recv),
                "centrality": (in_deg + out_deg) / (n_nodes - 1)
                if n_nodes > 1 else 0.0,
                "failed_ratio": stats.get("failed_ratio", 0.0),
                "anomaly": float(anomaly_map.get(nid, 0.0)),
                "temporal": float(temporal_map.get(nid, 0.0)),
                "volume": _norm(stats.get("volume", 0), max_vol),
                "velocity": _norm(stats.get("count", 0), max_cnt),
            }
            results.append(self._fuse(nid, node, signals,
                                      has_temporal=bool(temporal_map),
                                      has_anomaly=bool(anomaly_map)))

        results.sort(key=lambda r: r["risk_score"], reverse=True)
        return results

    def _fuse(self, nid, node, signals, has_temporal, has_anomaly):
        # choose active weights (skip external signals if not supplied)
        active = dict(WEIGHTS)
        if not has_temporal:
            active.pop("temporal", None)
        if not has_anomaly:
            active.pop("anomaly", None)
        total_w = sum(active.values()) or 1.0

        factors = []
        score = 0.0
        for sig, w in active.items():
            val = signals.get(sig, 0.0)
            if val <= 0:
                continue
            norm_w = w / total_w
            contribution = round(norm_w * val * 100, 2)
            score += contribution
            factors.append({
                "signal": sig,
                "weight": round(norm_w, 3),
                "value": round(val, 3),
                "contribution": contribution,
                "explanation": _EXPLAIN.get(sig, sig),
                "evidence": self._evidence(sig, node, signals),
            })

        factors.sort(key=lambda f: f["contribution"], reverse=True)
        score = round(min(100.0, score), 2)
        return {
            "node": nid,
            "type": node["type"],
            "risk_score": score,
            "risk_level": _level(score),
            "factors": factors,
            "top_reasons": [f["explanation"] for f in factors[:3]],
            "signals": {k: round(v, 3) for k, v in signals.items()},
        }

    def _evidence(self, sig, node, signals):
        if sig == "accumulation":
            return {"total_received": node["total_in"],
                    "sender_count": node["in_count"]}
        if sig == "layering":
            return {"total_in": node["total_in"], "total_out": node["total_out"]}
        if sig in ("fan_in",):
            return {"in_count": node["in_count"]}
        if sig in ("fan_out",):
            return {"out_count": node["out_count"]}
        return {"normalized_value": round(signals.get(sig, 0.0), 3)}

    def _txn_stats(self, rows):
        stats = defaultdict(lambda: {"count": 0, "volume": 0.0, "failed": 0})
        for r in rows:
            acct = r.get("account")
            if not acct:
                continue
            amt = r.get("amount") or 0
            s = stats[acct]
            s["count"] += 1
            s["volume"] += float(amt)
            if r.get("is_failed"):
                s["failed"] += 1
        for s in stats.values():
            s["failed_ratio"] = round(s["failed"] / s["count"], 3) if s["count"] else 0.0
        return stats
