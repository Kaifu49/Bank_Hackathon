from pydantic import BaseModel
from typing import Any


class RawRow(BaseModel):
    row_id: str
    fields: dict[str, Any]


class ExtractResponse(BaseModel):
    raw_rows: list[RawRow]


class StandardizedTransaction(BaseModel):
    date: str | None
    amount: float | None
    narration: str | None
    balance: float | None
    txn_type: str | None


class StandardizeResponse(BaseModel):
    transactions: list[StandardizedTransaction]