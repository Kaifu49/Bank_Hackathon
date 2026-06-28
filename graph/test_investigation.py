"""
Investigation engine tests. Run: python test_investigation.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "services"))
from flow_engine import MoneyFlowEngine     # noqa: E402
import flow_analytics as fa                 # noqa: E402
from risk_fusion import RiskFusionEngine    # noqa: E402
import investigation as inv                 # noqa: E402

results = []


def check(label, cond):
    results.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {label}")


# multi-account + single-account mix
txns = [
    {"sender_account": "ACC1", "receiver_account": "ACC2", "amount": 1000, "date": "2025-01-01"},
    {"sender_account": "ACC1", "receiver_account": "ACC3", "amount": 2000, "date": "2025-01-02"},
    {"sender_account": "S1", "receiver_account": "ACC1", "amount": 5000, "date": "2025-01-03"},
]
eng = MoneyFlowEngine().build(txns)
trips = fa.detect_round_trips(eng)
scored = RiskFusionEngine().score_network(eng, rows=[], round_trips=trips)

# top suspicious
top = inv.top_suspicious(scored, limit=5)
check("top_suspicious returns ranked list", len(top) >= 1)
check("entries have account+risk+patterns",
      all({"account", "risk_score", "risk_level", "patterns"} <= set(e) for e in top))

# counterparty analysis for ACC1
cp = inv.counterparty_analysis(eng, "ACC1")
sent = {x["counterparty"]: x for x in cp["sent_to"]}
recv = {x["counterparty"]: x for x in cp["received_from"]}
check("ACC1 sent to ACC2 and ACC3", "ACC2" in sent and "ACC3" in sent)
check("ACC1 received from S1", "S1" in recv)
check("ACC1 total_sent 3000", cp["total_sent"] == 3000.0)
check("ACC1 total_received 5000", cp["total_received"] == 5000.0)
check("distinct receivers=2, senders=1",
      cp["distinct_receivers"] == 2 and cp["distinct_senders"] == 1)
check("sent_to sorted by amount desc", cp["sent_to"][0]["counterparty"] == "ACC3")

# timeline (single-account narration rows)
rows = [
    {"date": "2025-02-01", "debit_credit": "CREDIT", "amount": 700, "balance": 700,
     "narration": "UPI/1/CR/x/HDFC/meera@oksbi/Pay"},
    {"date": "2025-02-02", "debit_credit": "DEBIT", "amount": 200, "balance": 500,
     "narration": "ATM CASH WDL"},
]
tl = inv.timeline(rows)
check("timeline length 2", len(tl) == 2)
check("timeline resolves counterparty",
      tl[0]["counterparty"] == "meera@oksbi" and tl[1]["counterparty"] == "CASH")
check("timeline carries direction+balance",
      tl[1]["direction"] == "DEBIT" and tl[1]["balance"] == 500)

print()
if all(results):
    print(f"ALL INVESTIGATION TESTS PASS ({sum(results)}/{len(results)})")
else:
    print(f"FAILURES ({sum(results)}/{len(results)} passed)")
    sys.exit(1)
