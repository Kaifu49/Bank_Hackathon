from fastapi import FastAPI
from pydantic import BaseModel

from services.anomaly_service import (
    AnomalyService
)

app = FastAPI()

service = AnomalyService()


class AnomalyRequest(
    BaseModel
):
    transactions: list


@app.get("/health")
def health():

    return {
        "service": "anomaly",
        "status": "healthy"
    }


@app.get("/anomaly")
def anomaly():

    result = service.latest()

    return {

        "count":
            len(result),

        "results":
            result
    }

@app.get("/anomaly/latest")
def anomaly_latest():

    result = service.latest()

    return {

        "count":
            len(result),

        "results":
            result
    }


@app.get(
    "/anomaly/statement/{statement_id}"
)
def anomaly_statement(
    statement_id: str
):

    result = service.statement(
        statement_id
    )

    return {

        "count":
            len(result),

        "results":
            result
    }


@app.get(
    "/anomaly/account/{account}"
)
def anomaly_account(
    account: str
):

    return service.account(
        account
    )

@app.get("/anomaly/debug")
def anomaly_debug():

    result = service.latest()

    print("\nDEBUG RESULT:\n")
    print(result[:3])

    return result[:3]