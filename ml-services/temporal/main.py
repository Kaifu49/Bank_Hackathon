from fastapi import FastAPI

from services.temporal_service import (
    TemporalService
)

app = FastAPI()

service = TemporalService()


@app.get("/health")
def health():

    return {

        "service":
            "temporal",

        "status":
            "healthy"
    }


@app.get("/temporal/latest")
def temporal_latest():

    result = service.latest()

    return {

        "count":
            len(result),

        "results":
            result
    }


@app.get(
    "/temporal/statement/{statement_id}"
)
def temporal_statement(
    statement_id: str
):

    result = (
        service.statement(
            statement_id
        )
    )

    return {

        "count":
            len(result),

        "results":
            result
    }


@app.get(
    "/temporal/account/{account}"
)
def temporal_account(
    account: str
):

    return (
        service.account(
            account
        )
    )