from fastapi import FastAPI
from pydantic import BaseModel

from services.graph_builder import (
    GraphBuilder
)
from services.round_trip_detector import (
    RoundTripDetector
)
from services.money_flow_analyzer import (
    MoneyFlowAnalyzer
)

from services.investigation_service import (
    InvestigationService
)

from services.accumulation_detector import (
    AccumulationDetector
)

from services.entity_graph_builder import(
    EntityGraphBuilder
)

from services.accumulation_detector import (
    AccumulationDetector
)

from services.transaction_graph_builder import (
    TransactionGraphBuilder
)

entity_builder = (
    EntityGraphBuilder()
)


accumulation_detector = (
    AccumulationDetector()
)

investigator = InvestigationService()
money_flow = MoneyFlowAnalyzer()

round_trip_detector = RoundTripDetector()

app = FastAPI()

builder = GraphBuilder()

txn_graph_builder = (
    TransactionGraphBuilder()
)

class BuildEntityGraphRequest(
    BaseModel
):
    transactions: list
    entities: list

class TransactionGraphRequest(
    BaseModel
):
    transactions: list
    entities: list
class BuildGraphRequest(
    BaseModel
):
    transactions: list


@app.get("/health")
def health():

    return {
        "service": "graph",
        "status": "healthy"
    }


@app.post("/build-graph")
def build_graph(
    request: BuildGraphRequest
):

    builder.build(
        request.transactions
    )

    return {
        "status": "success",
        "nodes_loaded":
            len(request.transactions)
    }

@app.post(
    "/build-entity-graph"
)
def build_entity_graph(
    request:
    BuildEntityGraphRequest
):

    entity_builder.build(
        request.transactions,
        request.entities
    )

    return {
        "status": "success",
        "transactions":
            len(
                request.transactions
            ),
        "entities":
            len(
                request.entities
            )
    }

@app.get("/round-trips")
def round_trips():

    cycles = (
        round_trip_detector
        .detect_cycles()
    )

    return {

        "count":
            len(cycles),

        "cycles":
            cycles
    }
@app.get(
    "/money-flow/{account}"
)
def money_flow_trace(
    account: str
):

    paths = money_flow.trace(
        account
    )

    return {

        "source":
            account,

        "path_count":
            len(paths),

        "paths":
            paths
    }


@app.get(
    "/investigation/account/{account_id}"
)
def investigate_account(
    account_id: str
):

    return (
        investigator
        .investigate(
            account_id
        )
    )

@app.get(
    "/accumulation-accounts"
)
def accumulation_accounts():

    return {

        "accounts":
            accumulation_detector
            .top_accumulation_accounts()
    }

@app.post(
    "/build-transaction-graph"
)
def build_transaction_graph(
    request:
        TransactionGraphRequest
):

    txn_graph_builder.build(
        request.transactions,
        request.entities
    )

    return {
        "status":
            "success"
    }


# ==========================================================================
# Phase 3 — in-memory graph intelligence (dependency-free, Neo4j-independent).
# Stateless: each call builds the graph from the supplied transactions, so the
# backend can scope analysis to a case without a running graph DB.
# ==========================================================================

from typing import Optional               # noqa: E402
from services.flow_engine import MoneyFlowEngine          # noqa: E402
from services import flow_analytics as fa                 # noqa: E402


class FlowRequest(BaseModel):
    account: Optional[str] = None          # statement holder account (optional)
    transactions: list = []


def _engine(req: "FlowRequest"):
    return MoneyFlowEngine().build(req.transactions, holder=req.account)


@app.post("/flow/analyze")
def flow_analyze(request: FlowRequest):
    eng = _engine(request)
    return {
        "summary": fa.money_flow_summary(eng),
        "round_trips": fa.detect_round_trips(eng),
        "communities": fa.detect_communities(eng),
        "centrality": fa.degree_centrality(eng),
        "graph": fa.graph_payload(eng),
    }


@app.post("/flow/money-flow")
def flow_money_flow(request: FlowRequest):
    eng = _engine(request)
    payload = fa.graph_payload(eng)
    return {
        "summary": fa.money_flow_summary(eng),
        "nodes": payload["nodes"],
        "edges": payload["edges"],
    }


@app.post("/flow/round-trips")
def flow_round_trips(request: FlowRequest):
    eng = _engine(request)
    cycles = fa.detect_round_trips(eng)
    return {"count": len(cycles), "round_trips": cycles}


@app.post("/flow/clusters")
def flow_clusters(request: FlowRequest):
    eng = _engine(request)
    return {"communities": fa.detect_communities(eng)}


# ----- DB-driven: build the graph straight from Postgres (whole network) -----

from services.postgres_loader import PostgresLoader        # noqa: E402

_loader = PostgresLoader()


def _engine_from_rows(rows):
    # rows already carry a per-statement holder `account`; build directly.
    return MoneyFlowEngine().build(rows)


def _full_result(eng):
    return {
        "summary": fa.money_flow_summary(eng),
        "round_trips": fa.detect_round_trips(eng),
        "communities": fa.detect_communities(eng),
        "centrality": fa.degree_centrality(eng),
        "graph": fa.graph_payload(eng),
    }


@app.get("/flow/analyze/all")
def flow_analyze_all():
    eng = _engine_from_rows(_loader.load_all_transactions())
    return _full_result(eng)


@app.get("/flow/money-flow/all")
def flow_money_flow_all():
    eng = _engine_from_rows(_loader.load_all_transactions())
    payload = fa.graph_payload(eng)
    return {"summary": fa.money_flow_summary(eng),
            "nodes": payload["nodes"], "edges": payload["edges"]}


@app.get("/flow/round-trips/all")
def flow_round_trips_all():
    eng = _engine_from_rows(_loader.load_all_transactions())
    cycles = fa.detect_round_trips(eng)
    return {"count": len(cycles), "round_trips": cycles}


@app.get("/flow/clusters/all")
def flow_clusters_all():
    eng = _engine_from_rows(_loader.load_all_transactions())
    return {"communities": fa.detect_communities(eng)}


@app.get("/flow/analyze/statement/{statement_id}")
def flow_analyze_statement(statement_id: str):
    eng = _engine_from_rows(_loader.load_statement_transactions(statement_id))
    return _full_result(eng)


@app.get("/flow/analyze/account/{account}")
def flow_analyze_account(account: str):
    eng = _engine_from_rows(_loader.load_account_transactions(account))
    return _full_result(eng)


# ==========================================================================
# Phase 4 — Risk Fusion (DB-driven). Fuses graph + transaction signals
# (+ optional temporal/anomaly) into an explainable per-account risk score.
# ==========================================================================

import os                                   # noqa: E402
import json as _json                         # noqa: E402
import urllib.request                        # noqa: E402
from services.risk_fusion import RiskFusionEngine          # noqa: E402

_risk = RiskFusionEngine()

ANOMALY_URL = os.getenv("ANOMALY_URL", "http://localhost:8007")
TEMPORAL_URL = os.getenv("TEMPORAL_URL", "http://localhost:8008")


def _get_json(url, timeout=15):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return _json.loads(resp.read().decode())
    except Exception as exc:
        print(f"[INFO] external signal fetch failed ({url}): {exc}")
        return None


def _external_maps():
    """Pull per-account anomaly (8007) + temporal (8008) scores. Graceful: a
    down/empty service just means that signal is skipped in the fusion."""
    temporal_map, anomaly_map = {}, {}
    a = _get_json(f"{ANOMALY_URL}/anomaly")
    if a and isinstance(a.get("results"), list):
        for r in a["results"]:
            acct, sc = r.get("account"), r.get("stat_score")
            if acct is not None and sc is not None:
                anomaly_map[str(acct)] = float(sc)
    t = _get_json(f"{TEMPORAL_URL}/temporal/latest")
    if t and isinstance(t.get("results"), list):
        for r in t["results"]:
            acct, sc = r.get("account"), r.get("temporal_score")
            if acct is not None and sc is not None:
                temporal_map[str(acct)] = float(sc)
    return temporal_map, anomaly_map


def _risk_for_rows(rows, top_n=None, with_external=True):
    eng = _engine_from_rows(rows)
    trips = fa.detect_round_trips(eng)
    temporal_map, anomaly_map = _external_maps() if with_external else ({}, {})
    scored = _risk.score_network(
        eng, rows=rows, round_trips=trips,
        temporal_map=temporal_map, anomaly_map=anomaly_map,
    )
    return scored[:top_n] if top_n else scored


@app.get("/risk/top")
def risk_top(limit: int = 20, include_external: bool = True):
    rows = _loader.load_all_transactions()
    scored = _risk_for_rows(rows, top_n=limit, with_external=include_external)
    return {"count": len(scored), "top_risks": scored}


@app.get("/risk/account/{account}")
def risk_account(account: str, include_external: bool = True):
    rows = _loader.load_account_transactions(account)
    scored = _risk_for_rows(rows, with_external=include_external)
    profile = next((r for r in scored if r["node"] == account), None)
    if profile is None:
        return {"account": account, "risk_score": 0.0, "risk_level": "LOW",
                "factors": [], "top_reasons": [],
                "note": "no resolvable activity for this account"}
    return profile