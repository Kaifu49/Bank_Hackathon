from fastapi import FastAPI
from pydantic import BaseModel

from services.validation_service import (
    ValidationService
)

app = FastAPI()

service = ValidationService()


class ValidationRequest(
    BaseModel
):
    transactions: list


@app.get("/health")
def health():

    return {
        "service": "validation",
        "status": "healthy"
    }


@app.post("/validate")
def validate(
    request: ValidationRequest
):

    result, summary = service.process_with_summary(
        request.transactions
    )

    return {

        "count": len(result),

        "summary": summary,

        "transactions": [

            txn.model_dump()

            for txn in result
        ]
    }