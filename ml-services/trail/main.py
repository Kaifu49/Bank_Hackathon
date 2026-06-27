from fastapi import FastAPI

from models.trail_models import (
    TrailRequest
)

from services.fifo_tracker import (
    FIFOTracker
)

app = FastAPI()

tracker = FIFOTracker()


@app.get("/health")
def health():

    return {
        "service": "trail",
        "status": "healthy"
    }


@app.post("/trace")
def trace_money(
    request: TrailRequest
):

    result = tracker.trace(
        [
            txn.model_dump()
            for txn in
            request.transactions
        ]
    )

    return {
        "trails": result
    }