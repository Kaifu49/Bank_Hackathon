"""
Explainability tests. Run: python test_explainability.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "services"))
from flow_engine import MoneyFlowEngine     # noqa: E402
import flow_analytics as fa                 # noqa: E402
from risk_fusion import RiskFusionEngine    # noqa: E402
import explainability as expl               # noqa: E402

results = []


def check(label, cond):
    results.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {label}")


txns = [
    {"sender_account": "MULE", "receiver_account": "B", "amount": 100000},
    {"sender_account": "B", "receiver_account": "C", "amount": 99000},
    {"sender_account": "C", "receiver_account": "MULE", "amount": 98000},
    {"sender_account": "S1", "receiver_account": "MULE", "amount": 50000},
    {"sender_account": "S2", "receiver_account": "MULE", "amount": 50000},
]
eng = MoneyFlowEngine().build(txns)
cycles = fa.detect_round_trips(eng)
scored = {r["node"]: r for r in RiskFusionEngine().score_network(eng, rows=[], round_trips=cycles)}

# account explanation
acc = expl.explain_account(scored["MULE"], eng, "MULE")
print("NARRATIVE:", acc["narrative"])
check("has narrative", len(acc["narrative"]) > 20)
check("has why reasons", len(acc["why"]) >= 1)
check("has how (factors)", len(acc["how"]) >= 1)
check("how entries carry contribution+evidence",
      all("contribution" in h and "evidence" in h for h in acc["how"]))
check("confidence in 0..1", 0.0 <= acc["confidence"] <= 1.0)
check("evidence has received_from", len(acc["evidence"]["top_received_from"]) >= 1)

# round-trip explanation
check("cycles have ids", all("id" in c for c in cycles))
cyc = cycles[0]
rt = expl.explain_round_trip(cyc, eng)
print("RT NARRATIVE:", rt["narrative"])
check("rt has path string", "→" in rt["path"])
check("rt has hops with amounts", all("amount" in h for h in rt["hops"]))
check("rt severity set", rt["severity"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL"))
check("rt bottleneck matches cycle", rt["bottleneck_amount"] == cyc["min_amount"])

print()
if all(results):
    print(f"ALL EXPLAINABILITY TESTS PASS ({sum(results)}/{len(results)})")
else:
    print(f"FAILURES ({sum(results)}/{len(results)} passed)")
    sys.exit(1)
