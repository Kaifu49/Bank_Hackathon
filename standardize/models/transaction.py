from pydantic import BaseModel
from typing import Optional


class StandardizedTransaction(
    BaseModel
):

    date: Optional[str] = None

    amount: Optional[float] = None

    txn_type: Optional[str] = None

    reference_number: Optional[str] = None

    narration: Optional[str] = None

    narration_normalized: Optional[str] = None

    balance: Optional[float] = None

    debit_credit: Optional[str] = None

    platform: Optional[str] = None

    upi_id: Optional[str] = None

    # -------------------------
    # Investigation Dataset
    # -------------------------

    sender_account: Optional[str] = None

    receiver_account: Optional[str] = None

    bank_name: Optional[str] = None