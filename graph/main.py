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