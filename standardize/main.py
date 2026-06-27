from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from services.standardization_service import (
    StandardizationService
)

app = FastAPI()

service = StandardizationService()


class StandardizeRequest(BaseModel):
    # Tolerant by design: accept any list (or null). Non-dict entries (e.g.
    # stray page text) are skipped by the service rather than 422-ing the whole
    # upload, and a null/missing rows (upstream parser error) becomes an empty
    # result instead of a cascading 422.
    rows: Optional[list] = None


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
        request.rows or []
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