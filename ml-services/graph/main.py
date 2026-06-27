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