from pydantic import BaseModel
from typing import Optional


class ValidatedTransaction(BaseModel):

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

    # -------------------------
    # Validation Fields
    # -------------------------

    is_duplicate: bool = False

    is_failed: bool = False

    is_valid: bool = True

    confidence_score: float = 1.0

    validation_notes: list[str] = []