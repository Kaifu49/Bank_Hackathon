"""
Analytics over a built MoneyFlowEngine (Core Requirements 3 & 4).

  detect_round_trips  -> circular money movement (Core Req 3)
  money_flow_summary  -> accumulation/destination, sources, fan-in/out, layering (Core Req 4)
  detect_communities  -> weakly-connected clusters
  graph_payload       -> frontend-ready {nodes, edges}
"""

from __future__ import annotations


# --------------------------------------------------------------------------
# Core Req 3 — round trips / circular flow
# --------------------------------------------------------------------------
def detect_round_trips(engine, max_len: int = 6, max_results: int = 200):
    """
    Enumerate simple directed cycles (money leaving a node and returning).
    Uses the 'smallest node id is the entry point' rule to find each cycle
    exactly once and to prune the search (Johnson-style), so it stays cheap on
    the sparse graphs real statements produce.
    """
    out = engine.out_adj
    order = {nid: i for i, nid in enumerate(sorted(engine.nodes))}
    results = []

    for start in sorted(engine.nodes):
        s_rank = order[start]
        # iterative DFS; only visit nodes whose rank >= start's rank
        stack = [(start, [start])]
        while stack:
            node, path = stack.pop()
            for nxt in out.get(node, ()):
                if order[nxt] < s_rank:
                    continue
                if nxt == start and len(path) >= 2:
                    results.append(_build_cycle(engine, path))
                    if len(results) >= max_results:
                        for i, c in enumerate(results):
                            c["id"] = i
                        return results
                elif nxt not in path and len(path) <= max_len:
                    stack.append((nxt, path + [nxt]))
    results.sort(key=lambda c: c["min_amount"], reverse=True)
    for i, c in enumerate(results):
        c["id"] = i                 # stable chain id for explanation lookups
    return results


def _build_cycle(engine, path):
    amounts = []
    for i in range(len(path)):
        src, dst = path[i], path[(i + 1) % len(path)]
        amounts.append(engine.edges[(src, dst)]["total_amount"])
    return {
        "nodes": path,
        "length": len(path),
        "edge_amounts": amounts,
        "min_amount": round(min(amounts), 2),   # bottleneck / circulatable amount
        "total_amount": round(sum(amounts), 2),
    }


# --------------------------------------------------------------------------
# Core Req 4 — money flow analysis
# --------------------------------------------------------------------------
def money_flow_summary(engine, top_n: int = 10):
    nodes = engine.nodes
    out_deg = {n: len(engine.out_adj.get(n, ())) for n in nodes}
    in_deg = {n: len(engine.in_adj.get(n, ())) for n in nodes}

    def top(metric, reverse=True):
        return sorted(nodes.values(), key=metric, reverse=reverse)[:top_n]

    accumulation = [
        {"node": n["id"], "total_received": n["total_in"],
         "sender_count": in_deg[n["id"]]}
        for n in top(lambda x: x["total_in"])
        if n["total_in"] > 0
    ]
    sources = [
        {"node": n["id"], "total_sent": n["total_out"],
         "receiver_count": out_deg[n["id"]]}
        for n in top(lambda x: x["total_out"])
        if n["total_out"] > 0
    ]
    fan_out = [
        {"node": nid, "receivers": out_deg[nid]}
        for nid in sorted(out_deg, key=out_deg.get, reverse=True)[:top_n]
        if out_deg[nid] >= 3
    ]
    fan_in = [
        {"node": nid, "senders": in_deg[nid]}
        for nid in sorted(in_deg, key=in_deg.get, reverse=True)[:top_n]
        if in_deg[nid] >= 3
    ]

    # layering / pass-through: money in ~= money out, both sides present
    layering = []
    for n in nodes.values():
        ti, to = n["total_in"], n["total_out"]
        if ti > 0 and to > 0:
            ratio = abs(ti - to) / max(ti, to)
            if ratio <= 0.1:
                layering.append({"node": n["id"], "total_in": ti,
                                 "total_out": to, "passthrough_ratio": round(1 - ratio, 3)})
    layering.sort(key=lambda x: x["total_in"], reverse=True)

    destination = accumulation[0]["node"] if accumulation else None

    return {
        "node_count": len(nodes),
        "edge_count": len(engine.edges),
        "unresolved_counterparties": engine.unresolved,
        "destination_account": destination,
        "accumulation_accounts": accumulation,
        "source_accounts": sources,
        "fan_out": fan_out,
        "fan_in": fan_in,
        "layering": layering[:top_n],
    }


def degree_centrality(engine, top_n: int = 10):
    n = len(engine.nodes)
    if n <= 1:
        return []
    scores = []
    for nid in engine.nodes:
        deg = len(engine.out_adj.get(nid, ())) + len(engine.in_adj.get(nid, ()))
        scores.append({"node": nid, "centrality": round(deg / (n - 1), 4)})
    scores.sort(key=lambda x: x["centrality"], reverse=True)
    return scores[:top_n]


# --------------------------------------------------------------------------
# Communities — weakly connected components (union-find)
# --------------------------------------------------------------------------
def detect_communities(engine, min_size: int = 2):
    parent = {n: n for n in engine.nodes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for (src, dst) in engine.edges:
        union(src, dst)

    groups = {}
    for n in engine.nodes:
        groups.setdefault(find(n), []).append(n)

    communities = [
        {"id": i, "size": len(members), "members": sorted(members)}
        for i, members in enumerate(
            sorted(groups.values(), key=len, reverse=True))
        if len(members) >= min_size
    ]
    return communities


# --------------------------------------------------------------------------
# Frontend payload — nodes + edges
# --------------------------------------------------------------------------
def graph_payload(engine):
    summary = money_flow_summary(engine)
    accumulation_ids = {a["node"] for a in summary["accumulation_accounts"][:3]}
    source_ids = {s["node"] for s in summary["source_accounts"][:3]}

    nodes = []
    for n in engine.nodes.values():
        nodes.append({
            "id": n["id"],
            "label": n["id"],
            "type": n["type"],
            "total_in": n["total_in"],
            "total_out": n["total_out"],
            "in_count": n["in_count"],
            "out_count": n["out_count"],
            "is_accumulation": n["id"] in accumulation_ids,
            "is_source": n["id"] in source_ids,
        })
    edges = list(engine.edges.values())
    return {"nodes": nodes, "edges": edges}
