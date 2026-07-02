"""
MoneyFlowEngine — dependency-free in-memory money-flow graph + analytics.

Why a new engine (Phase 3):
  The previous graph was Neo4j-only and keyed on sender_account/receiver_account,
  which are empty for real single-account bank statements -> it built almost
  nothing on the real dataset. This engine works for BOTH shapes:

    * Multi-account / investigation data: edges from sender -> receiver.
    * Single-account statements: edges from the statement holder to the
      counterparty derived from the narration (UPI VPA / payee name / merchant /
      CASH), with direction from debit/credit.

Provides (Core Requirements 3 & 4):
    * directed money-flow graph (nodes = accounts/counterparties, edges = aggregated transfers)
    * round-trip / circular-flow detection (cycles)
    * accumulation/destination detection, sources, fan-in / fan-out, layering
    * degree centrality and weakly-connected communities
    * a frontend-ready {nodes, edges} payload

No third-party deps (no neo4j / networkx required) so it is portable and
testable. Neo4j can persist the same graph separately.
"""

from __future__ import annotations

import re
from collections import defaultdict

_UPI_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]+@[A-Za-z][A-Za-z0-9]+")
_NAME_AFTER_VPA = re.compile(
    r"@[A-Za-z0-9]+/([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})"
)
_MERCHANTS = ("PAYTM", "PHONEPE", "GOOGLE PAY", "GPAY", "AMAZON", "FLIPKART",
              "SWIGGY", "ZOMATO", "JIO", "AIRTEL")


def _to_float(v):
    try:
        return float(str(v).replace(",", "").strip())
    except Exception:
        return None


def resolve_counterparty(narration: str):
    """Module-level counterparty resolver (reused by the investigation engine)."""
    narr = narration or ""
    if not narr:
        return None
    m = _UPI_RE.search(narr)
    if m and not (m.end() < len(narr) and narr[m.end()] == "."):
        return m.group(0).lower()
    pm = _NAME_AFTER_VPA.search(narr)
    if pm:
        return pm.group(1).strip().upper()
    up = narr.upper()
    for mk in _MERCHANTS:
        if mk in up:
            return mk
    if "ATM" in up or "CASH" in up:
        return "CASH"
    return None


def _classify(node_id: str) -> str:
    if "@" in node_id:
        return "UPI_ID"
    if node_id == "CASH":
        return "CASH"
    digits = re.sub(r"\D", "", node_id)
    if digits and len(digits) >= 6 and digits == node_id:
        return "ACCOUNT"
    return "ENTITY"


class MoneyFlowEngine:

    def __init__(self):
        self.nodes = {}                       # id -> node dict
        self.edges = {}                       # (src,dst) -> edge dict
        self.out_adj = defaultdict(set)
        self.in_adj = defaultdict(set)
        self.unresolved = 0                   # txns with no usable counterparty

    # ------------------------------------------------------------------ #
    # build
    # ------------------------------------------------------------------ #

    def build(self, transactions, holder=None):
        for txn in (transactions or []):
            self._add_txn(txn, holder)
        return self

    def _add_txn(self, txn, holder):
        amount = _to_float(txn.get("amount"))
        if amount is None or amount <= 0:
            return
        direction = (txn.get("debit_credit") or "").upper()
        src, dst = self._resolve(txn, holder, direction)
        if not src or not dst or src == dst:
            if src is None and dst is None:
                self.unresolved += 1
            return
        self._add_edge(src, dst, amount, txn.get("date"))

    def _resolve(self, txn, holder, direction):
        sender = (txn.get("sender_account") or "").strip() \
            if txn.get("sender_account") else ""
        receiver = (txn.get("receiver_account") or "").strip() \
            if txn.get("receiver_account") else ""
        if sender and receiver:
            return sender, receiver

        holder_id = (txn.get("account") or holder or "SELF")
        holder_id = str(holder_id).strip()
        counterparty = self._counterparty(txn)
        if counterparty is None:
            return None, None

        if direction == "DEBIT":
            return holder_id, counterparty
        if direction == "CREDIT":
            return counterparty, holder_id
        return None, None

    def _counterparty(self, txn):
        return resolve_counterparty(txn.get("narration") or "")

    def _ensure_node(self, node_id):
        if node_id not in self.nodes:
            self.nodes[node_id] = {
                "id": node_id, "type": _classify(node_id),
                "total_in": 0.0, "total_out": 0.0,
                "in_count": 0, "out_count": 0,
            }

    def _add_edge(self, src, dst, amount, date):
        self._ensure_node(src)
        self._ensure_node(dst)
        key = (src, dst)
        e = self.edges.get(key)
        if e is None:
            e = self.edges[key] = {
                "source": src, "target": dst, "total_amount": 0.0,
                "txn_count": 0, "first_date": date, "last_date": date,
            }
        e["total_amount"] = round(e["total_amount"] + amount, 2)
        e["txn_count"] += 1
        if date:
            if not e["first_date"] or str(date) < str(e["first_date"]):
                e["first_date"] = date
            if not e["last_date"] or str(date) > str(e["last_date"]):
                e["last_date"] = date
        self.out_adj[src].add(dst)
        self.in_adj[dst].add(src)
        self.nodes[src]["total_out"] = round(self.nodes[src]["total_out"] + amount, 2)
        self.nodes[src]["out_count"] += 1
        self.nodes[dst]["total_in"] = round(self.nodes[dst]["total_in"] + amount, 2)
        self.nodes[dst]["in_count"] += 1
