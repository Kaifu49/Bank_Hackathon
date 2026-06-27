from pydantic import BaseModel
from typing import Optional


class CanonicalTransaction(BaseModel):

    date: Optional[str] = None

    narration: Optional[str] = None

    transaction_id: Optional[str] = None

    debit: Optional[float] = None

    credit: Optional[float] = None

    balance: Optional[float] = None

    sender_account: Optional[str] = None

    receiver_account: Optional[str] = None

    amount: Optional[float] = None

    bank_name: Optional[str] = None

    txn_type: Optional[str] = None