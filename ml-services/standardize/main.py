from fastapi import FastAPI
from pydantic import BaseModel

from services.standardization_service import (
    StandardizationService
)

app = FastAPI()

service = StandardizationService()


class StandardizeRequest(BaseModel):
    rows: list[dict]


@app.get("/health")
def health():
    return {
        "service": "standardize",
        "status": "healthy"
    }


@app.post("/standardize")
def standardize(
    request: StandardizeRequest
):

    result, meta = service.process_with_meta(
        request.rows
    )

    return {
        "count": len(result),
        "transactions": [
            row.model_dump()
            for row in result
        ],
        # additive: column-resolution quality for the frontend / QA
        "column_resolution": meta,
    }