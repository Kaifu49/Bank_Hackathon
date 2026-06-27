from pydantic import BaseModel
from typing import List, Optional


class TrailTransaction(BaseModel):

    txn_id: Optional[str] = None

    type: str

    amount: float

    balance: Optional[float] = None


class TrailRequest(BaseModel):

    transactions: List[
        TrailTransaction
    ]