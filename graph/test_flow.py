"""
Graph intelligence tests (dependency-free engine).
Run: python test_flow.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "services"))
from flow_engine import MoneyFlowEngine     # noqa: E402
import flow_analytics as fa                 # noqa: E402

results = []


def check(label, got, exp):
    ok = got == exp
    results.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {label}: got={got}")
    if not ok:
        print(f"        expected={exp}")


# 1) Multi-account round trip A -> B -> C -> A  (Core Req 3)
cyc = MoneyFlowEngine().build([
    {"sender_account": "A", "receiver_account": "B", "amount": 1000, "date": "2025-01-01"},
    {"sender_account": "B", "receiver_account": "C", "amount": 800, "date": "2025-01-02"},
    {"sender_account": "C", "receiver_account": "A", "amount": 500, "date": "2025-01-03"},
])
trips = fa.detect_round_trips(cyc)
check("round trip found", len(trips) >= 1, True)
check("cycle nodes == {A,B,C}",
      set(trips[0]["nodes"]) if trips else set(), {"A", "B", "C"})
check("cycle bottleneck amount", trips[0]["min_amount"] if trips else 0, 500.0)

# 2) Accumulation: X,Y,Z -> D  (Core Req 4)
acc = MoneyFlowEngine().build([
    {"sender_account": "X", "receiver_account": "D", "amount": 100},
    {"sender_account": "Y", "receiver_account": "D", "amount": 200},
    {"sender_account": "Z", "receiver_account": "D", "amount": 300},
])
summ = fa.money_flow_summary(acc)
check("destination account == D", summ["destination_account"], "D")
top = summ["accumulation_accounts"][0]
check("D received 600", top["total_received"], 600.0)
check("D sender_count 3", top["sender_count"], 3)
check("D fan-in detected",
      any(f["node"] == "D" and f["senders"] == 3 for f in summ["fan_in"]), True)

# 3) Single-account statement: counterparty derived from narration
single = MoneyFlowEngine().build([
    {"amount": 500, "debit_credit": "DEBIT",
     "narration": "UPI/123/DR/RAHU/HDFC/rahul@ybl/Pay", "date": "2025-02-01"},
    {"amount": 700, "debit_credit": "CREDIT",
     "narration": "UPI/456/CR/MEER/SBI/meera@oksbi/Pay", "date": "2025-02-02"},
    {"amount": 2000, "debit_credit": "DEBIT",
     "narration": "ATM CASH WITHDRAWAL LUCKNOW", "date": "2025-02-03"},
], holder="112108374579")
edges = set(single.edges.keys())
check("debit edge holder->rahul@ybl",
      ("112108374579", "rahul@ybl") in edges, True)
check("credit edge meera@oksbi->holder",
      ("meera@oksbi", "112108374579") in edges, True)
check("ATM cash edge holder->CASH",
      ("112108374579", "CASH") in edges, True)
check("holder typed ACCOUNT",
      single.nodes["112108374579"]["type"], "ACCOUNT")
check("vpa typed UPI_ID", single.nodes["rahul@ybl"]["type"], "UPI_ID")

# 4) Communities (weakly connected components)
comm = fa.detect_communities(acc)
check("accumulation cluster size 4 (X,Y,Z,D)",
      comm[0]["size"] if comm else 0, 4)

# 5) Payload shape + accumulation flag
payload = fa.graph_payload(acc)
d_node = [n for n in payload["nodes"] if n["id"] == "D"][0]
check("payload marks D accumulation", d_node["is_accumulation"], True)
check("payload has edges", len(payload["edges"]), 3)

print()
if all(results):
    print(f"ALL GRAPH TESTS PASS ({sum(results)}/{len(results)})")
else:
    print(f"FAILURES ({sum(results)}/{len(results)} passed)")
    sys.exit(1)
