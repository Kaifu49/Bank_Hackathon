"""
Risk fusion tests. Run: python test_risk.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "services"))
from flow_engine import MoneyFlowEngine     # noqa: E402
import flow_analytics as fa                 # noqa: E402
from risk_fusion import RiskFusionEngine    # noqa: E402

results = []


def check(label, cond):
    results.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {label}")


# Build a network: MULE is in a round-trip AND a layering pass-through AND
# collects from many; LEAF is a clean one-off counterparty.
txns = [
    # round trip MULE -> B -> C -> MULE
    {"sender_account": "MULE", "receiver_account": "B", "amount": 100000},
    {"sender_account": "B", "receiver_account": "C", "amount": 99000},
    {"sender_account": "C", "receiver_account": "MULE", "amount": 98000},
    # fan-in to MULE (collection) + pass-through out
    {"sender_account": "S1", "receiver_account": "MULE", "amount": 50000},
    {"sender_account": "S2", "receiver_account": "MULE", "amount": 50000},
    {"sender_account": "S3", "receiver_account": "MULE", "amount": 50000},
    {"sender_account": "MULE", "receiver_account": "OUT", "amount": 150000},
    # clean leaf
    {"sender_account": "P", "receiver_account": "LEAF", "amount": 200},
]

eng = MoneyFlowEngine().build(txns)
trips = fa.detect_round_trips(eng)
scored = RiskFusionEngine().score_network(eng, rows=[], round_trips=trips)
by_node = {r["node"]: r for r in scored}

mule = by_node["MULE"]
leaf = by_node["LEAF"]

print(f"MULE score={mule['risk_score']} level={mule['risk_level']} "
      f"reasons={mule['top_reasons']}")
print(f"LEAF score={leaf['risk_score']} level={leaf['risk_level']}")

check("MULE riskier than LEAF", mule["risk_score"] > leaf["risk_score"])
check("MULE is HIGH or CRITICAL", mule["risk_level"] in ("HIGH", "CRITICAL"))
check("LEAF is LOW", leaf["risk_level"] == "LOW")
check("MULE flagged round_trip",
      any(f["signal"] == "round_trip" for f in mule["factors"]))
check("MULE flagged fan_in or accumulation",
      any(f["signal"] in ("fan_in", "accumulation") for f in mule["factors"]))
check("factors carry explanations + evidence",
      all("explanation" in f and "evidence" in f for f in mule["factors"]))
check("results sorted desc", scored == sorted(scored, key=lambda r: r["risk_score"], reverse=True))

# failed-ratio signal via rows
rows = [
    {"account": "MULE", "amount": 100, "is_failed": True},
    {"account": "MULE", "amount": 100, "is_failed": True},
    {"account": "MULE", "amount": 100, "is_failed": False},
]
scored2 = RiskFusionEngine().score_network(eng, rows=rows, round_trips=trips)
mule2 = next(r for r in scored2 if r["node"] == "MULE")
check("failed_ratio factor present with rows",
      any(f["signal"] == "failed_ratio" for f in mule2["factors"]))

print()
if all(results):
    print(f"ALL RISK TESTS PASS ({sum(results)}/{len(results)})")
else:
    print(f"FAILURES ({sum(results)}/{len(results)} passed)")
    sys.exit(1)
