from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from services.fifo_tracker import FIFOTracker
from services.postgres_loader import PostgresLoader

app = FastAPI()

tracker = FIFOTracker()
loader = PostgresLoader()


class TraceRequest(BaseModel):
    # flexible: accepts standardized txns (debit_credit) or legacy (type)
    transactions: list = []


@app.get("/health")
def health():
    return {"service": "trail", "status": "healthy"}


# -- stateless (caller supplies transactions) ----------------------------

@app.post("/trace")
def trace_money(request: TraceRequest):
    trails = tracker.trace(request.transactions)
    return {"count": len(trails), "trails": trails}


# -- DB-driven (Core Requirement 5) --------------------------------------

@app.get("/trail/statement/{statement_id}")
def trail_statement(statement_id: str):
    txns = loader.load_statement_transactions(statement_id)
    trails = tracker.trace(txns)
    return {"statement_id": statement_id, "count": len(trails), "trails": trails}


@app.get("/trail/account/{account}")
def trail_account(account: str):
    txns = loader.load_account_transactions(account)
    trails = tracker.trace(txns)
    return {"account": account, "count": len(trails), "trails": trails}


@app.get("/trail/transaction/{transaction_id}")
def trail_transaction(transaction_id: str):
    statement_id = loader.find_statement_for_transaction(transaction_id)
    if not statement_id:
        return {"kind": "not_found", "transaction_id": transaction_id,
                "message": "transaction not found"}
    txns = loader.load_statement_transactions(statement_id)
    return tracker.trace_for_credit(txns, transaction_id)
