"""
FIFO money-trail tests (Core Requirement 5). Run: python test_fifo.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "services"))
from fifo_tracker import FIFOTracker     # noqa: E402

t = FIFOTracker()
results = []


def check(label, cond):
    results.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {label}")


# 1) Exact example from documentation.md
#    T1 CREDIT 50000 ; T2 DEBIT 10000 ; T3 DEBIT 15000 ; T4 DEBIT 5000
doc = [
    {"txn_id": "T1", "debit_credit": "CREDIT", "amount": 50000, "narration": "NEFT FROM ACME"},
    {"txn_id": "T2", "debit_credit": "DEBIT", "amount": 10000, "narration": "UPI/1/rahul@ybl"},
    {"txn_id": "T3", "debit_credit": "DEBIT", "amount": 15000, "narration": "UPI/2/meera@oksbi"},
    {"txn_id": "T4", "debit_credit": "DEBIT", "amount": 5000, "narration": "ATM CASH"},
]
trails = t.trace(doc)
c = trails[0]
check("one credit trail", len(trails) == 1)
check("credit amount 50000", c["credit_amount"] == 50000)
check("spent 30000", c["spent"] == 30000)
check("remaining 20000", c["remaining"] == 20000)
check("3 debits consumed", len(c["consumed_by"]) == 3)
check("debit order T2,T3,T4",
      [d["debit_txn_id"] for d in c["consumed_by"]] == ["T2", "T3", "T4"])
check("destinations traced",
      [d["destination"] for d in c["consumed_by"]] == ["rahul@ybl", "meera@oksbi", "CASH"])
check("not fully traced (money remains)", c["fully_traced"] is False)

# 2) Multi-credit FIFO: C1 100, C2 100, then DEBIT 150 -> C1 fully + C2 half
multi = [
    {"txn_id": "C1", "debit_credit": "CREDIT", "amount": 100, "narration": "from A"},
    {"txn_id": "C2", "debit_credit": "CREDIT", "amount": 100, "narration": "from B"},
    {"txn_id": "D1", "debit_credit": "DEBIT", "amount": 150, "narration": "UPI/x/bob@ybl"},
]
tr = {x["credit_txn_id"]: x for x in t.trace(multi)}
check("C1 fully consumed (100)", tr["C1"]["spent"] == 100 and tr["C1"]["remaining"] == 0)
check("C1 fully_traced", tr["C1"]["fully_traced"] is True)
check("C2 partially consumed (50)", tr["C2"]["spent"] == 50 and tr["C2"]["remaining"] == 50)
check("D1 split across C1 and C2",
      tr["C1"]["consumed_by"][0]["amount"] == 100 and tr["C2"]["consumed_by"][0]["amount"] == 50)

# 3) trace_for_credit: query a specific credit, and reverse-lookup a debit
res_c = t.trace_for_credit(doc, "T1")
check("trace_for_credit returns credit_trail", res_c["kind"] == "credit_trail")
res_d = t.trace_for_credit(doc, "T3")
check("debit T3 reverse-funded by T1",
      res_d["kind"] == "debit_funding" and res_d["funded_by"][0]["credit_txn_id"] == "T1")

# 4) legacy 'type' key still works
legacy = [{"type": "CREDIT", "amount": 100}, {"type": "DEBIT", "amount": 40}]
check("legacy type key works", t.trace(legacy)[0]["spent"] == 40)

print()
if all(results):
    print(f"ALL FIFO TESTS PASS ({sum(results)}/{len(results)})")
else:
    print(f"FAILURES ({sum(results)}/{len(results)} passed)")
    sys.exit(1)
